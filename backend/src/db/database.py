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

# Column names for tasks table (in order - must match actual DB schema)
TASK_COLUMNS = [
    "id", "name", "task_type", "url", "description",
    "status", "phase", "session_id", "result_file", "result_message",
    "created_at", "completed_at", "deleted_at", "test_code_file"
]

# Column names for sessions table (in order)
SESSION_COLUMNS = [
    "id", "task_id", "excel_path", "title",
    "time_created", "time_updated", "last_used",
    "status", "created_at", "deleted_at"
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
                    completed_at TEXT,
                    deleted_at TEXT
                )
            """)
            conn.commit()
        self._migrate_phase()
        self._migrate_deleted_at()
        self._migrate_sessions()
        self._migrate_test_code_file()
        self._cleanup_old_tasks()

    def _cleanup_old_tasks(self):
        cutoff = (datetime.now() - timedelta(days=TASK_RETENTION_DAYS)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM tasks WHERE created_at < ? AND deleted_at IS NULL", (cutoff,))
            conn.commit()

    def _migrate_phase(self):
        """Add phase column if it doesn't exist (for existing databases)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row[1] for row in cursor.fetchall()]
            if "phase" not in columns:
                conn.execute("ALTER TABLE tasks ADD COLUMN phase TEXT NOT NULL DEFAULT 'excel_generation'")
                conn.commit()

    def _migrate_deleted_at(self):
        """Add deleted_at column if it doesn't exist (for existing databases)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row[1] for row in cursor.fetchall()]
            if "deleted_at" not in columns:
                conn.execute("ALTER TABLE tasks ADD COLUMN deleted_at TEXT")
                conn.commit()

    def _migrate_sessions(self):
        """Create sessions table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    task_id TEXT NOT NULL UNIQUE,
                    excel_path TEXT,
                    title TEXT,
                    time_created INTEGER,
                    time_updated INTEGER,
                    last_used TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT NOT NULL,
                    deleted_at TEXT
                )
            """)
            conn.commit()

    def _migrate_test_code_file(self):
        """Add test_code_file column if it doesn't exist (for existing databases)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(tasks)")
            columns = [row[1] for row in cursor.fetchall()]
            if "test_code_file" not in columns:
                conn.execute("ALTER TABLE tasks ADD COLUMN test_code_file TEXT")
                conn.commit()

    def update_task_phase(self, task_id: str, phase: str):
        """Update the phase of a task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE tasks SET phase = ? WHERE id = ? AND deleted_at IS NULL", (phase, task_id))
            conn.commit()

    def soft_delete_task(self, task_id: str) -> bool:
        """Soft delete a task by setting deleted_at timestamp.
        Returns True if deleted, False if task not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id, status FROM tasks WHERE id = ? AND deleted_at IS NULL", (task_id,))
            row = cursor.fetchone()
            if not row:
                return False
            now = datetime.now().isoformat()
            conn.execute("UPDATE tasks SET deleted_at = ? WHERE id = ?", (now, task_id))
            conn.commit()
            return True

    def restore_task(self, task_id: str) -> bool:
        """Restore a soft-deleted task by clearing deleted_at.
        Returns True if restored, False if task not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT id FROM tasks WHERE id = ? AND deleted_at IS NOT NULL", (task_id,))
            if not cursor.fetchone():
                return False
            conn.execute("UPDATE tasks SET deleted_at = NULL WHERE id = ?", (task_id,))
            conn.commit()
            return True

    def get_deleted_tasks(self) -> List[dict]:
        """Get all soft-deleted tasks (for recycle bin)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC")
            rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def _row_to_dict(self, row):
        """Convert a row to a dict using column names."""
        return {col: row[i] for i, col in enumerate(TASK_COLUMNS)}

    def _session_row_to_dict(self, row):
        """Convert a session row to a dict using column names."""
        return {col: row[i] for i, col in enumerate(SESSION_COLUMNS)}

    def create_session(self, task_id: str, session_id: str, excel_path: str = None,
                       title: str = None, time_created: int = None,
                       time_updated: int = None) -> bool:
        """Create a session record (1:1 with Task)."""
        now = datetime.now().isoformat()
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO sessions (id, task_id, excel_path, title,
                                        time_created, time_updated, last_used, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)
                """, (session_id, task_id, excel_path, title,
                      time_created, time_updated, now, now))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Task already has a session

    def get_session(self, task_id: str) -> Optional[dict]:
        """Get session associated with a Task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE task_id = ? AND deleted_at IS NULL",
                (task_id,)
            )
            row = cursor.fetchone()
        if not row:
            return None
        return self._session_row_to_dict(row)

    def get_session_by_excel(self, excel_path: str) -> Optional[dict]:
        """Find session by excel_path (for migration)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE excel_path = ? AND deleted_at IS NULL",
                (excel_path,)
            )
            row = cursor.fetchone()
        if not row:
            return None
        return self._session_row_to_dict(row)

    def update_session_last_used(self, task_id: str) -> bool:
        """Update last_used timestamp."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE sessions SET last_used = ? WHERE task_id = ? AND deleted_at IS NULL",
                (now, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def soft_delete_session(self, task_id: str) -> bool:
        """Soft delete a session."""
        now = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE sessions SET deleted_at = ? WHERE task_id = ? AND deleted_at IS NULL",
                (now, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def restore_session(self, task_id: str) -> bool:
        """Restore a soft-deleted session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE sessions SET deleted_at = NULL WHERE task_id = ? AND deleted_at IS NOT NULL",
                (task_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_deleted_sessions(self) -> List[dict]:
        """Get all soft-deleted sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
            )
            rows = cursor.fetchall()
        return [self._session_row_to_dict(row) for row in rows]

    def list_sessions(self) -> List[dict]:
        """List all active sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE deleted_at IS NULL ORDER BY created_at DESC"
            )
            rows = cursor.fetchall()
        return [self._session_row_to_dict(row) for row in rows]

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
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE id = ? AND deleted_at IS NULL",
                (task_id,)
            )
            row = cursor.fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def list_tasks(self) -> List[dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY created_at DESC")
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
                conn.execute("UPDATE tasks SET session_id = ? WHERE id = ? AND deleted_at IS NULL", (session_id, task_id))
            if result_file is not None:
                conn.execute("UPDATE tasks SET result_file = ? WHERE id = ? AND deleted_at IS NULL", (result_file, task_id))
            if result_message is not None:
                conn.execute("UPDATE tasks SET result_message = ? WHERE id = ? AND deleted_at IS NULL", (result_message, task_id))

            conn.execute(
                "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ? AND deleted_at IS NULL",
                (status, completed_at, task_id)
            )
            conn.commit()

    def update_task_test_code(self, task_id: str, test_code_file: str) -> bool:
        """Update test_code_file field for a task."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "UPDATE tasks SET test_code_file = ? WHERE id = ? AND deleted_at IS NULL",
                (test_code_file, task_id)
            )
            conn.commit()
            return cursor.rowcount > 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False

    def close(self):
        pass
