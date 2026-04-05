"""Tasks router — task CRUD, restore, download"""
import os
import sqlite3
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from api.models import TaskResponse, TasksListResponse
from api.dependencies import get_task_db_dep
from db.database import TaskDB
from config import PROJECT_ROOT
from constants import STATUS_COMPLETED, STATUS_FAILED


router = APIRouter(tags=["Tasks"])


@router.get("/tasks", response_model=TasksListResponse)
def get_tasks(task_db: TaskDB = Depends(get_task_db_dep)):
    tasks = task_db.list_tasks()
    return TasksListResponse(tasks=tasks)


@router.get("/tasks/deleted")
def get_deleted_tasks(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取已删除的任务列表（回收站）"""
    tasks = task_db.get_deleted_tasks()
    from api.internal.shared import DeletedTasksListResponse
    return DeletedTasksListResponse(tasks=tasks)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)


@router.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除任务（软删除，只能删除 completed 或 failed 状态）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] not in (STATUS_COMPLETED, STATUS_FAILED):
        raise HTTPException(status_code=400, detail="Cannot delete task in pending/running status")

    task_db.soft_delete_task(task_id)
    return None


@router.post("/tasks/{task_id}/restore", response_model=TaskResponse)
def restore_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复已删除的任务"""
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute("SELECT id, deleted_at FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    if row[1] is None:
        raise HTTPException(status_code=400, detail="Task is not deleted")

    success = task_db.restore_task(task_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to restore task")

    restored_task = task_db.get_task(task_id)
    return TaskResponse(**restored_task)


@router.get("/download/{task_id}")
def download_task_file(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """下载任务的 Excel 文件"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] != STATUS_COMPLETED:
        raise HTTPException(status_code=400, detail="Task not completed yet")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=404, detail="No file associated with this task")

    normalized = os.path.normpath(result_file.replace("/", os.sep))
    if ".." in normalized or not normalized.startswith("test_cases"):
        raise HTTPException(status_code=400, detail="Invalid file path")

    full_path = os.path.join(PROJECT_ROOT, normalized)

    if os.path.isdir(full_path):
        for f in os.listdir(full_path):
            if f.endswith(".xlsx"):
                full_path = os.path.join(full_path, f)
                break
        else:
            raise HTTPException(status_code=404, detail="No xlsx file found in directory")

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=full_path,
        filename=os.path.basename(full_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
