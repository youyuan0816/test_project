"""Generation router — /generate, /continue, /upload/{task_id}"""
import os
import threading
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.routing import APIRouter

from api.models import GenerateRequest, ContinueRequest, CreateTaskResponse
from api.dependencies import get_task_db_dep
from db.database import TaskDB
from config import PROJECT_ROOT
from constants import PHASE_EXCEL, PHASE_CODE
from .shared import run_generate_excel, run_continue_session


router = APIRouter(tags=["Generation"])


@router.post("/generate", response_model=CreateTaskResponse)
def generate_excel_api(req: GenerateRequest, task_db: TaskDB = Depends(get_task_db_dep)):
    """生成 Excel 测试用例（后台异步执行）"""
    # Look up existing session by continue_excel path
    continue_session_id = None
    if req.continue_excel:
        existing = task_db.get_session_by_excel(req.continue_excel)
        if existing:
            continue_session_id = existing["id"]

    task_id = task_db.create_task(
        name=req.filepath,
        task_type="generate_excel",
        url=req.url,
        description=req.description,
    )
    task_db.update_task_phase(task_id, PHASE_EXCEL)

    # Pre-create session so background worker can update it later
    # (session_id will be set by OpenCode during generation)
    if continue_session_id:
        task_db.create_session(task_id, continue_session_id, excel_path=req.filepath)

    thread = threading.Thread(
        target=run_generate_excel,
        args=(task_id, req.url, req.filepath, req.description, req.username or "", req.password or "", req.continue_excel, continue_session_id),
    )
    thread.start()

    return CreateTaskResponse(
        task_id=task_id,
        status="pending",
        message="Task created, processing in background",
    )


@router.post("/continue", response_model=CreateTaskResponse)
def continue_session_api(req: ContinueRequest, task_db: TaskDB = Depends(get_task_db_dep)):
    """读取 Excel 生成测试代码（后台异步执行）"""
    task_id = req.task_id

    if not task_id:
        task_id = task_db.create_task(
            name=req.excel_file,
            task_type="continue_session",
            url="",
            description="",
        )
    else:
        task = task_db.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        task_db.update_task_phase(task_id, PHASE_CODE)
        task_db.update_task_status(task_id, "running")

    # Look up existing session for this task
    session_id = None
    existing_session = task_db.get_session(task_id)
    if existing_session:
        session_id = existing_session["id"]
    else:
        # Try to find session by excel_path and migrate it
        existing_by_excel = task_db.get_session_by_excel(req.excel_file)
        if existing_by_excel:
            session_id = existing_by_excel["id"]
            task_db.create_session(task_id, session_id, excel_path=req.excel_file)

    thread = threading.Thread(
        target=run_continue_session,
        args=(task_id, req.excel_file, "", session_id),
    )
    thread.start()

    return CreateTaskResponse(
        task_id=task_id,
        status="running",
        message="Code generation started in background",
    )


@router.post("/upload/{task_id}")
async def upload_excel_api(task_id: str, file: UploadFile = File(...), task_db: TaskDB = Depends(get_task_db_dep)):
    """上传 Excel 文件并立即生成测试代码（后台异步执行）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=400, detail="Task has no result_file")

    normalized = os.path.normpath(result_file.replace("/", os.sep))
    if ".." in normalized or not normalized.startswith("test_cases"):
        raise HTTPException(status_code=400, detail="Invalid result_file path")

    base_dir = os.path.join(PROJECT_ROOT, normalized)
    if os.path.isdir(base_dir):
        for f in os.listdir(base_dir):
            if f.endswith(".xlsx"):
                base_dir = os.path.join(base_dir, f)
                break
        else:
            raise HTTPException(status_code=404, detail="No xlsx file found in task's result directory")

    if not file.filename.endswith(".xlsx"):
        raise HTTPException(status_code=400, detail="Only .xlsx files are allowed")

    try:
        content = await file.read()
        with open(base_dir, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    task_db.update_task_status(task_id, "running")
    task_db.update_task_phase(task_id, PHASE_CODE)

    excel_relative = os.path.relpath(base_dir, PROJECT_ROOT).replace(os.sep, "/")
    task = task_db.get_task(task_id)
    save_path = task.get("name", "") if task else ""

    # Look up existing session for this task
    session_id = None
    existing_session = task_db.get_session(task_id)
    if existing_session:
        session_id = existing_session["id"]

    thread = threading.Thread(
        target=run_continue_session,
        args=(task_id, excel_relative, save_path, session_id),
    )
    thread.start()

    return {
        "task_id": task_id,
        "status": "running",
        "message": "File uploaded and test code generation started in background",
    }
