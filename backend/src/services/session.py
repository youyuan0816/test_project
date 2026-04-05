import sys
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

# Ensure src directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import SESSIONS_FILE, TASK_DB_PATH
from db.database import get_task_db


def load_sessions():
    """加载 session 映射 (兼容旧 JSON 文件)"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return {}
        return json.loads(content)


def save_sessions(sessions):
    """保存 session 映射 (兼容旧 JSON 文件)"""
    sessions_dir = os.path.dirname(SESSIONS_FILE)
    os.makedirs(sessions_dir, exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def get_session_id(excel_path):
    """获取 Excel 对应的 session ID"""
    task_db = get_task_db()

    # First find task by name (original excel_path)
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute(
            "SELECT id FROM tasks WHERE name = ? AND deleted_at IS NULL",
            (excel_path,)
        )
        row = cursor.fetchone()

    if row:
        session = task_db.get_session(row[0])
        return session["id"] if session else None
    return None


def save_session_id(excel_path, session_id, title=None, time_created=None, time_updated=None):
    """保存 session ID"""
    task_db = get_task_db()

    # Find task by name (which is the original excel_path)
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute(
            "SELECT id, result_file FROM tasks WHERE name = ? AND deleted_at IS NULL",
            (excel_path,)
        )
        row = cursor.fetchone()

    if not row:
        print(f"[WARN] No task found with name={excel_path}")
        return

    task_id, result_file = row

    # Check if session already exists for this task
    existing = task_db.get_session(task_id)
    if existing:
        task_db.update_session_last_used(task_id)
        print(f"[INFO] Updated last_used for session: {session_id}")
    else:
        # Use result_file as excel_path for the session record
        session_excel_path = result_file if result_file else excel_path
        task_db.create_session(task_id, session_id, session_excel_path,
                            title, time_created, time_updated)
        print(f"[INFO] Created session: {session_id} for task: {task_id}")


def list_sessions():
    """列出所有保存的 session"""
    task_db = get_task_db()
    sessions = task_db.list_sessions()
    return {
        "status": "success",
        "sessions": sessions
    }
