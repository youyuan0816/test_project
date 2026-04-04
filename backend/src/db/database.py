import sys
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path

# Ensure src directory is in Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from constants import (
    STATUS_PENDING, STATUS_RUNNING, STATUS_COMPLETED, STATUS_FAILED,
    PHASE_EXCEL, PHASE_CODE, TASK_RETENTION_DAYS
)
from config import TASK_DB_PATH

# Column names for tasks table (in order)
TASK_COLUMNS = [
    "id", "name", "task_type", "url", "description",
    "status", "phase", "session_id", "result_file", "result_message",
    "created_at", "completed_at"
]

# Singleton instance
_db_instance = None


def get_task_db():
    """Get singleton TaskDB instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TaskDB(str(TASK_DB_PATH))
    return _db_instance


class TaskDB:
    """Task database management class"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    url TEXT DEFAULT '',
                    description TEXT DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending',
                    phase TEXT NOT NULL DEFAULT 'excel_generation',
                    session_id TEXT,
                    result_file TEXT,
                    result_message TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                )
            """)
            conn.commit()
        self._migrate_phase()
        self._cleanup_old_tasks()

    def _cleanup_old_tasks(self):
        cutoff = (datetime.now() - timedelta(days=TASK_RETENTION_DAYS)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tasks WHERE created_at < ?", (cutoff,))
            conn.commit()

    def _migrate_phase(self):
        """Add phase column if it doesn't exist (for existing databases)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row[1] for row in cursor.fetchall()]
            if "phase" not in columns:
                conn.execute("ALTER TABLE tasks ADD COLUMN phase TEXT NOT NULL DEFAULT 'excel_generation'")
                conn.commit()

    def update_task_phase(self, task_id: str, phase: str):
        """Update the phase of a task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE tasks SET phase = ? WHERE id = ?", (phase, task_id))
            conn.commit()

    def _row_to_dict(self, row):
        """Convert a row to a dict using column names."""
        return {col: row[i] for i, col in enumerate(TASK_COLUMNS)}

    def create_task(self, name: str, task_type: str, url: str = "", description: str = "") -> str:
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO tasks (id, name, task_type, url, description, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task_id, name, task_type, url, description, STATUS_PENDING, now))
            conn.commit()

        return task_id

    def get_task(self, task_id: str) -> Optional[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def list_tasks(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            rows = cursor.fetchall()

        return [self._row_to_dict(row) for row in rows]

    def update_task_status(
        self,
        task_id: str,
        status: str,
        session_id: Optional[str] = None,
        result_file: Optional[str] = None,
        result_message: Optional[str] = None
    ):
        completed_at = datetime.now().isoformat() if status in (STATUS_COMPLETED, STATUS_FAILED) else None

        with sqlite3.connect(self.db_path) as conn:
            if session_id is not None:
                conn.execute("UPDATE tasks SET session_id = ? WHERE id = ?", (session_id, task_id))
            if result_file is not None:
                conn.execute("UPDATE tasks SET result_file = ? WHERE id = ?", (result_file, task_id))
            if result_message is not None:
                conn.execute("UPDATE tasks SET result_message = ? WHERE id = ?", (result_message, task_id))

            conn.execute(
                "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                (status, completed_at, task_id)
            )
            conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self):
        pass
