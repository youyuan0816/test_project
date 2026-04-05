import os
import sqlite3
import sys
import threading
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# Ensure src directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import CORS_ORIGINS, PROJECT_ROOT
from constants import PHASE_EXCEL, PHASE_CODE, STATUS_COMPLETED, STATUS_FAILED
from api.models import GenerateRequest, ContinueRequest, TaskResponse, TasksListResponse, CreateTaskResponse, TestCaseResponse, TestCasesListResponse
from api.dependencies import get_task_db_dep
from db.database import get_task_db, TaskDB
from services.generator import generate_excel, continue_session, list_sessions


app = FastAPI(title="UI Test Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DeletedTasksListResponse(BaseModel):
    tasks: List[TaskResponse]


class SessionResponse(BaseModel):
    id: str
    task_id: str
    excel_path: Optional[str]
    title: Optional[str]
    time_created: Optional[int]
    time_updated: Optional[int]
    last_used: Optional[str]
    status: str
    created_at: str
    deleted_at: Optional[str]


class SessionsListResponse(BaseModel):
    sessions: List[SessionResponse]


def run_generate_excel(task_id: str, url: str, filepath: str, description: str, username: str, password: str, continue_excel: Optional[str]):
    """Background worker for generate_excel"""
    task_db = get_task_db()
    try:
        task_db.update_task_status(task_id, "running")
        result = generate_excel(
            url=url,
            filepath=filepath,
            description=description,
            username=username,
            password=password,
            continue_excel=continue_excel
        )
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        result_file = result.get("actual_file", filepath)
        task_db.update_task_status(task_id, status, result_file=result_file, result_message=result["message"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))


@app.post("/generate", response_model=CreateTaskResponse)
def generate_excel_api(req: GenerateRequest, task_db: TaskDB = Depends(get_task_db_dep)):
    """生成 Excel 测试用例（后台异步执行）

    调用 generator.py 中的 generate_excel 函数，通过 OpenCode 生成测试用例 Excel
    立即返回 task_id，实际工作在后台执行
    """
    # Create task
    task_id = task_db.create_task(
        name=req.filepath,
        task_type="generate_excel",
        url=req.url,
        description=req.description,
    )
    task_db.update_task_phase(task_id, PHASE_EXCEL)

    # Start background worker
    thread = threading.Thread(
        target=run_generate_excel,
        args=(task_id, req.url, req.filepath, req.description, req.username or "", req.password or "", req.continue_excel)
    )
    thread.start()

    # Return immediately
    return CreateTaskResponse(
        task_id=task_id,
        status="pending",
        message="Task created, processing in background"
    )


def run_continue_session(task_id: str, excel_file: str):
    """Background worker for continue_session"""
    task_db = get_task_db()
    task_db.update_task_phase(task_id, PHASE_CODE)
    try:
        task_db.update_task_status(task_id, "running")
        result = continue_session(excel_file)
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        # For continue_session, result_file is the excel file that was processed
        task_db.update_task_status(task_id, status, result_file=excel_file, result_message=result["message"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))


@app.post("/continue", response_model=CreateTaskResponse)
def continue_session_api(req: ContinueRequest, task_db: TaskDB = Depends(get_task_db_dep)):
    """继续 session，读取 Excel 生成测试代码（后台异步执行）

    调用 generator.py 中的 continue_session 函数，通过 OpenCode 生成 pytest 测试代码
    立即返回 task_id，实际工作在后台执行
    """
    task_id = req.task_id

    # 如果没有提供 task_id，创建新 task
    if not task_id:
        task_id = task_db.create_task(
            name=req.excel_file,
            task_type="continue_session",
            url="",
            description="",
        )
    else:
        # 复用现有 task，更新状态和 phase
        task = task_db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task_db.update_task_phase(task_id, PHASE_CODE)
        task_db.update_task_status(task_id, "running")

    # Start background worker
    thread = threading.Thread(
        target=run_continue_session,
        args=(task_id, req.excel_file)
    )
    thread.start()

    # Return immediately
    return CreateTaskResponse(
        task_id=task_id,
        status="running",
        message="Code generation started in background"
    )


@app.post("/upload/{task_id}")
async def upload_excel_api(task_id: str, file: UploadFile = File(...), task_db: TaskDB = Depends(get_task_db_dep)):
    """上传 Excel 文件替换现有文件，并立即生成测试代码（后台异步执行）

    Args:
        task_id: 任务 ID，用于获取 result_file 路径
        file: 上传的 Excel 文件 (multipart/form-data)

    Returns:
        {"task_id": str, "status": str, "message": str}
    """

    # Get the task
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=400, detail="Task has no result_file")

    # Security check: ensure result_file is within test_cases/ directory
    normalized = os.path.normpath(result_file.replace('/', os.sep))
    if ".." in normalized or not normalized.startswith("test_cases"):
        raise HTTPException(status_code=400, detail="Invalid result_file path")

    # If result_file is a directory, find the existing .xlsx file inside
    base_dir = os.path.join(PROJECT_ROOT, normalized)
    if os.path.isdir(base_dir):
        for f in os.listdir(base_dir):
            if f.endswith('.xlsx'):
                base_dir = os.path.join(base_dir, f)
                break
        else:
            raise HTTPException(status_code=404, detail="No xlsx file found in task's result directory")

    # Validate uploaded file is an Excel file
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")

    # Write uploaded file to replace existing Excel
    try:
        content = await file.read()
        with open(base_dir, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    # Start background worker to generate test code using SAME task_id
    task_db.update_task_status(task_id, "running")
    task_db.update_task_phase(task_id, PHASE_CODE)

    # Use relative path from PROJECT_ROOT for continue_session
    excel_relative = os.path.relpath(base_dir, PROJECT_ROOT)
    excel_relative = excel_relative.replace(os.sep, '/')
    thread = threading.Thread(
        target=run_continue_session,
        args=(task_id, excel_relative)
    )
    thread.start()

    return {
        "task_id": task_id,
        "status": "running",
        "message": "File uploaded and test code generation started in background"
    }


@app.get("/sessions", response_model=SessionsListResponse)
def get_sessions(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取所有 Session 列表"""
    sessions = task_db.list_sessions()
    return SessionsListResponse(sessions=sessions)


@app.get("/tasks/{task_id}/session", response_model=SessionResponse)
def get_task_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """获取 Task 关联的 Session"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session)


@app.delete("/sessions/{task_id}", status_code=204)
def delete_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除 Task 的 Session（软删除）"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    task_db.soft_delete_session(task_id)
    return None


@app.post("/sessions/{task_id}/restore", response_model=SessionResponse)
def restore_session_api(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复 Session"""
    # Check if session exists and is deleted
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE task_id = ? AND deleted_at IS NOT NULL",
            (task_id,)
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    task_db.restore_session(task_id)
    session = task_db.get_session(task_id)
    return SessionResponse(**session)


@app.get("/tasks", response_model=TasksListResponse)
def get_tasks(task_db: TaskDB = Depends(get_task_db_dep)):
    tasks = task_db.list_tasks()
    return TasksListResponse(tasks=tasks)


@app.get("/tasks/deleted", response_model=DeletedTasksListResponse)
def get_deleted_tasks(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取已删除的任务列表（回收站）"""
    tasks = task_db.get_deleted_tasks()
    return DeletedTasksListResponse(tasks=tasks)


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除任务（软删除，只能删除 completed 或 failed 状态的任务）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 检查任务状态，只能删除 completed 或 failed
    if task["status"] not in (STATUS_COMPLETED, STATUS_FAILED):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete task in pending/running status"
        )

    task_db.soft_delete_task(task_id)
    return None


@app.post("/tasks/{task_id}/restore", response_model=TaskResponse)
def restore_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复已删除的任务"""
    # First check if task exists at all (including deleted)
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute("SELECT id, deleted_at FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    # Check if task is actually deleted
    if row[1] is None:  # deleted_at is None means not deleted
        raise HTTPException(status_code=400, detail="Task is not deleted")

    # Restore the task
    success = task_db.restore_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to restore task")

    restored_task = task_db.get_task(task_id)
    return TaskResponse(**restored_task)


@app.get("/download/{task_id}")
def download_task_file(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """Download the Excel file for a completed task"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] != STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed yet")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=404, detail="No file associated with this task")

    # Security check: ensure file is within test_cases/ directory
    # Normalize path separators for Windows compatibility
    normalized = os.path.normpath(result_file.replace('/', os.sep))
    if ".." in normalized or not normalized.startswith("test_cases"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    full_path = os.path.join(PROJECT_ROOT, normalized)

    # If path is a directory, find the xlsx file inside
    if os.path.isdir(full_path):
        for f in os.listdir(full_path):
            if f.endswith('.xlsx'):
                full_path = os.path.join(full_path, f)
                break
        else:
            raise HTTPException(status_code=404, detail="No xlsx file found in directory")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    filename = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/testcases", response_model=TestCasesListResponse)
def get_testcases(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取所有生成了测试代码的 Task 列表"""
    tasks = task_db.list_tasks()
    testcases = [
        TestCaseResponse(
            task_id=t["id"],
            name=t["name"],
            excel_file=t.get("result_file"),
            test_code_dir=t.get("test_code_file"),
            created_at=t["created_at"],
        )
        for t in tasks
        if t.get("test_code_file") and t.get("status") == "completed"
    ]
    return TestCasesListResponse(testcases=testcases)


@app.get("/download-code/{task_id}")
def download_test_code(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """下载测试代码目录（zip 格式）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    test_code_dir = task.get("test_code_file")
    if not test_code_dir:
        raise HTTPException(status_code=404, detail="No test code for this task")

    # Security check: ensure path is within tests/ directory
    normalized = os.path.normpath(test_code_dir.replace('/', os.sep))
    if ".." in normalized or not normalized.startswith("tests"):
        raise HTTPException(status_code=400, detail="Invalid path")

    full_path = os.path.join(PROJECT_ROOT, normalized)

    if not os.path.exists(full_path) or not os.path.isdir(full_path):
        raise HTTPException(status_code=404, detail="Directory not found")

    # Create zip from directory
    import zipfile
    import io

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(full_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, PROJECT_ROOT)
                zipf.write(file_path, arcname)

    zip_buffer.seek(0)

    return StreamingResponse(
        iter([zip_buffer.getvalue()]),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(test_code_dir)}.zip"
        }
    )
