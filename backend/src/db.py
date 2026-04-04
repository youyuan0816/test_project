import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tasks.db")

class TaskDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                task_type TEXT NOT NULL,
                url TEXT DEFAULT '',
                description TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                session_id TEXT,
                result_file TEXT,
                result_message TEXT,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        self._cleanup_old_tasks()

    def _cleanup_old_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        conn.execute("DELETE FROM tasks WHERE created_at < ?", (cutoff,))
        conn.commit()
        conn.close()

    def create_task(self, name: str, task_type: str, url: str = "", description: str = "") -> str:
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO tasks (id, name, task_type, url, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (task_id, name, task_type, url, description, now))
        conn.commit()
        conn.close()

        return task_id

    def get_task(self, task_id: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return {
            "id": row[0],
            "name": row[1],
            "task_type": row[2],
            "url": row[3],
            "description": row[4],
            "status": row[5],
            "session_id": row[6],
            "result_file": row[7],
            "result_message": row[8],
            "created_at": row[9],
            "completed_at": row[10],
        }

    def list_tasks(self) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "name": row[1],
                "task_type": row[2],
                "url": row[3],
                "description": row[4],
                "status": row[5],
                "session_id": row[6],
                "result_file": row[7],
                "result_message": row[8],
                "created_at": row[9],
                "completed_at": row[10],
            }
            for row in rows
        ]

    def update_task_status(
        self,
        task_id: str,
        status: str,
        session_id: Optional[str] = None,
        result_file: Optional[str] = None,
        result_message: Optional[str] = None
    ):
        completed_at = datetime.now().isoformat() if status in ("completed", "failed") else None

        conn = sqlite3.connect(self.db_path)

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
        conn.close()

    def close(self):
        pass