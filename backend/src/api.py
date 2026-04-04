import sys
import os
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generator import generate_excel, continue_session, list_sessions
from db import TaskDB

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


@app.post("/generate")
def generate_excel_api(req: GenerateRequest):
    """生成 Excel 测试用例

    调用 generator.py 中的 generate_excel 函数，通过 OpenCode 生成测试用例 Excel
    支持继续之前的 session（如果指定了 continue_excel 参数）
    """
    # Create task first
    task_id = task_db.create_task(
        name=req.filepath,
        task_type="generate_excel",
        url=req.url,
        description=req.description,
    )

    # Update to running
    task_db.update_task_status(task_id, "running")

    result = generate_excel(
        url=req.url,
        filepath=req.filepath,
        description=req.description,
        username=req.username or "",
        password=req.password or "",
        continue_excel=req.continue_excel
    )

    # Update final status
    status = "completed" if result["status"] == "success" else "failed"
    task_db.update_task_status(
        task_id,
        status,
        result_message=result["message"]
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return {"task_id": task_id, "status": status, "message": result["message"]}


@app.post("/continue")
def continue_session_api(req: ContinueRequest):
    """继续 session，读取 Excel 生成测试代码

    调用 generator.py 中的 continue_session 函数，通过 OpenCode 生成 pytest 测试代码
    会自动查找 Excel 文件对应的 session 进行继续
    """
    # Create task first
    task_id = task_db.create_task(
        name=req.excel_file,
        task_type="continue_session",
        url="",
        description="",
    )

    # Update to running
    task_db.update_task_status(task_id, "running")

    result = continue_session(req.excel_file)

    # Update final status
    status = "completed" if result["status"] == "success" else "failed"
    task_db.update_task_status(
        task_id,
        status,
        result_message=result["message"]
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])

    return {"task_id": task_id, "status": status, "message": result["message"]}


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


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
