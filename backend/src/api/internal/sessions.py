"""Sessions router — session CRUD and restore"""
import sqlite3
from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_task_db_dep
from db.database import TaskDB
from .shared import SessionResponse, SessionsListResponse


router = APIRouter(tags=["Sessions"])


@router.get("/sessions", response_model=SessionsListResponse)
def get_sessions(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取所有 Session 列表"""
    sessions = task_db.list_sessions()
    return SessionsListResponse(sessions=sessions)


@router.get("/tasks/{task_id}/session", response_model=SessionResponse)
def get_task_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """获取 Task 关联的 Session"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session)


@router.delete("/sessions/{task_id}", status_code=204)
def delete_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除 Task 的 Session（软删除）"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    task_db.soft_delete_session(task_id)
    return None


@router.post("/sessions/{task_id}/restore", response_model=SessionResponse)
def restore_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复 Session"""
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE task_id = ? AND deleted_at IS NOT NULL",
            (task_id,),
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    task_db.restore_session(task_id)
    session = task_db.get_session(task_id)
    return SessionResponse(**session)
