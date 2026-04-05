"""Shared models and background workers used by all routers."""
import threading
from typing import Optional, List
from pydantic import BaseModel

from db.database import get_task_db, TaskDB
from services.generator import generate_excel, continue_session
from constants import PHASE_EXCEL, PHASE_CODE


# ─── Shared Pydantic models ────────────────────────────────────────────────────

class DeletedTasksListResponse(BaseModel):
    tasks: List["TaskResponse"]


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


# ─── Background workers ───────────────────────────────────────────────────────

def _save_session(task_id: str, excel_path: str, session_id: str):
    """Save or update session in TaskDB after background generation completes."""
    task_db = get_task_db()
    existing = task_db.get_session(task_id)
    if existing:
        task_db.update_session_last_used(task_id)
    else:
        task_db.create_session(task_id, session_id, excel_path=excel_path)


def run_generate_excel(
    task_id: str,
    url: str,
    filepath: str,
    description: str,
    username: str,
    password: str,
    continue_excel: Optional[str],
    continue_session_id: Optional[str] = None,
):
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
            continue_excel=continue_excel,
            continue_session_id=continue_session_id,
        )
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        result_file = result.get("actual_file", filepath)
        task_db.update_task_status(task_id, status, result_file=result_file, result_message=result["message"])
        # Save session returned by OpenCode
        if result.get("session_id"):
            _save_session(task_id, filepath, result["session_id"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))


def run_continue_session(
    task_id: str,
    excel_file: str,
    save_path: str = "",
    session_id: str = None,
):
    """Background worker for continue_session"""
    task_db = get_task_db()
    task_db.update_task_phase(task_id, PHASE_CODE)
    try:
        task_db.update_task_status(task_id, "running")

        if not save_path:
            task = task_db.get_task(task_id)
            save_path = task.get("name", "") if task else ""

        result = continue_session(excel_file, save_path=save_path, session_id=session_id)
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        test_code_dir = result.get("test_code_dir")
        task_db.update_task_status(task_id, status, result_file=excel_file, result_message=result["message"])
        if test_code_dir and status == "completed":
            task_db.update_task_test_code(task_id, test_code_dir)
        # Save or update session returned by OpenCode
        if result.get("session_id"):
            _save_session(task_id, excel_file, result["session_id"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))
