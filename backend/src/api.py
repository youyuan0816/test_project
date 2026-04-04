import sys
import os
import threading
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import generate_excel, continue_session, list_sessions
from db import TaskDB

# Project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database path
TASK_DB_PATH = os.environ.get('TASK_DB_PATH', os.path.join(os.path.dirname(__file__), "..", "tasks.db"))

# Global db instance
task_db = TaskDB(TASK_DB_PATH)

app = FastAPI(title="UI Test Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    url: str
    filepath: str
    username: Optional[str] = ""
    password: Optional[str] = ""
    description: str
    continue_excel: Optional[str] = None  # 可选：继续之前的 session


class ContinueRequest(BaseModel):
    excel_file: str


class TaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    url: str
    description: str
    status: str
    session_id: Optional[str]
    result_file: Optional[str]
    result_message: Optional[str]
    created_at: str
    completed_at: Optional[str]

class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]

class CreateTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


def run_generate_excel(task_id: str, url: str, filepath: str, description: str, username: str, password: str, continue_excel: Optional[str]):
    """Background worker for generate_excel"""
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
        task_db.update_task_status(task_id, status, result_message=result["message"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))


@app.post("/generate")
def generate_excel_api(req: GenerateRequest):
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

    # Start background worker
    thread = threading.Thread(
        target=run_generate_excel,
        args=(task_id, req.url, req.filepath, req.description, req.username or "", req.password or "", req.continue_excel)
    )
    thread.start()

    # Return immediately
    return {"task_id": task_id, "status": "pending", "message": "Task created, processing in background"}


def run_continue_session(task_id: str, excel_file: str):
    """Background worker for continue_session"""
    try:
        task_db.update_task_status(task_id, "running")
        result = continue_session(excel_file)
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        task_db.update_task_status(task_id, status, result_message=result["message"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))


@app.post("/continue")
def continue_session_api(req: ContinueRequest):
    """继续 session，读取 Excel 生成测试代码（后台异步执行）

    调用 generator.py 中的 continue_session 函数，通过 OpenCode 生成 pytest 测试代码
    立即返回 task_id，实际工作在后台执行
    """
    # Create task
    task_id = task_db.create_task(
        name=req.excel_file,
        task_type="continue_session",
        url="",
        description="",
    )

    # Start background worker
    thread = threading.Thread(
        target=run_continue_session,
        args=(task_id, req.excel_file)
    )
    thread.start()

    # Return immediately
    return {"task_id": task_id, "status": "pending", "message": "Task created, processing in background"}


@app.get("/sessions")
def get_sessions():
    """获取所有保存的 session 列表"""
    result = list_sessions()
    return result


@app.get("/tasks")
def get_tasks():
    tasks = task_db.list_tasks()
    return {"tasks": tasks}


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/download/{task_id}")
def download_task_file(task_id: str):
    """Download the Excel file for a completed task"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=404, detail="No file associated with this task")

    # Security check: ensure file is within test_cases/ directory
    if ".." in result_file or result_file.startswith("/") or not result_file.startswith("test_cases/"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    full_path = os.path.join(PROJECT_ROOT, result_file)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    filename = os.path.basename(result_file)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
