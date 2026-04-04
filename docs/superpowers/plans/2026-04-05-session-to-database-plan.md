# Session 存储迁移到数据库实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 Session 存储从 JSON 文件迁移到 SQLite 数据库，与 Task 关联管理

**Architecture:** 在 TaskDB 添加 sessions 表和 CRUD 方法，改造 services/session.py 调用 TaskDB，新增 Session API 端点

**Tech Stack:** Python, FastAPI, SQLite

---

## File Structure

| 文件 | 变更 |
|------|------|
| `backend/src/db/database.py` | 新增 sessions 表，_migrate_sessions()，create_session() 等方法 |
| `backend/src/services/session.py` | 内部调用改为 TaskDB 方法 |
| `backend/src/api/routes.py` | 新增 Session API 端点 |
| `backend/src/main.py` | 新增迁移命令 `--migrate-sessions` |

---

## Task 1: 数据库层 - 添加 sessions 表和迁移

**Files:**
- Modify: `backend/src/db/database.py`

- [ ] **Step 1: 添加 SESSION_COLUMNS 常量**

在 `TASK_COLUMNS` 后添加：

```python
# Column names for sessions table (in order)
SESSION_COLUMNS = [
    "id", "task_id", "excel_path", "title",
    "time_created", "time_updated", "last_used",
    "status", "created_at", "deleted_at"
]
```

- [ ] **Step 2: 添加 _migrate_sessions 方法**

在 `_migrate_deleted_at` 方法后添加：

```python
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
```

- [ ] **Step 3: 在 _init_db 中调用 _migrate_sessions**

修改 `_init_db` 方法，在 `self._migrate_deleted_at()` 后添加：

```python
self._migrate_deleted_at()
self._migrate_sessions()  # 新增
self._cleanup_old_tasks()
```

- [ ] **Step 4: 添加 create_session 方法**

在 `_row_to_dict` 方法后添加：

```python
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
```

- [ ] **Step 5: 添加 get_session 方法**

```python
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
    return {col: row[i] for i, col in enumerate(SESSION_COLUMNS)}
```

- [ ] **Step 6: 添加 get_session_by_excel 方法**

```python
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
    return {col: row[i] for i, col in enumerate(SESSION_COLUMNS)}
```

- [ ] **Step 7: 添加 update_session_last_used 方法**

```python
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
```

- [ ] **Step 8: 添加 soft_delete_session 方法**

```python
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
```

- [ ] **Step 9: 添加 restore_session 方法**

```python
def restore_session(self, task_id: str) -> bool:
    """Restore a soft-deleted session."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            "UPDATE sessions SET deleted_at = NULL WHERE task_id = ? AND deleted_at IS NOT NULL",
            (task_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
```

- [ ] **Step 10: 添加 get_deleted_sessions 方法**

```python
def get_deleted_sessions(self) -> List[dict]:
    """Get all soft-deleted sessions."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
        )
        rows = cursor.fetchall()
    return [{col: row[i] for i, col in enumerate(SESSION_COLUMNS)} for row in rows]
```

- [ ] **Step 11: 添加 list_sessions 方法**

```python
def list_sessions(self) -> List[dict]:
    """List all active sessions."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE deleted_at IS NULL ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
    return [{col: row[i] for i, col in enumerate(SESSION_COLUMNS)} for row in rows]
```

- [ ] **Step 12: Commit**

```bash
git add backend/src/db/database.py
git commit -m "feat: add sessions table and CRUD methods to TaskDB"
```

---

## Task 2: services/session.py 改造

**Files:**
- Modify: `backend/src/services/session.py`

- [ ] **Step 1: 更新 get_session_id 函数**

将 `get_session_id` 改为调用 TaskDB：

```python
def get_session_id(excel_path):
    """获取 Excel 对应的 session ID"""
    task_db = get_task_db()
    session = task_db.get_session_by_excel(excel_path)
    return session["id"] if session else None
```

- [ ] **Step 2: 更新 save_session_id 函数**

```python
def save_session_id(excel_path, session_id, title=None, time_created=None, time_updated=None):
    """保存 session ID"""
    task_db = get_task_db()

    # Check if session exists for this excel_path
    existing = task_db.get_session_by_excel(excel_path)
    if existing:
        # Update last_used
        # Find task_id by excel_path in tasks table
        with sqlite3.connect(task_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE result_file = ? AND deleted_at IS NULL",
                (excel_path,)
            )
            row = cursor.fetchone()
        if row:
            task_db.update_session_last_used(row[0])
    else:
        # Try to find task by excel_path
        with sqlite3.connect(task_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE result_file = ? AND deleted_at IS NULL",
                (excel_path,)
            )
            row = cursor.fetchone()
        task_id = row[0] if row else None

        if task_id:
            task_db.create_session(task_id, session_id, excel_path,
                                title, time_created, time_updated)
```

- [ ] **Step 3: 更新 list_sessions 函数**

```python
def list_sessions():
    """列出所有保存的 session"""
    task_db = get_task_db()
    sessions = task_db.list_sessions()
    return {
        "status": "success",
        "sessions": sessions
    }
```

- [ ] **Step 4: 添加必要的 import**

```python
import sqlite3
from db.database import get_task_db
```

- [ ] **Step 5: Commit**

```bash
git add backend/src/services/session.py
git commit -m "refactor: services/session.py now uses TaskDB"
```

---

## Task 3: API 路由 - 添加 Session 端点

**Files:**
- Modify: `backend/src/api/routes.py`

- [ ] **Step 1: 添加 SessionResponse 模型**

在 `DeletedTasksListResponse` 后添加：

```python
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
```

- [ ] **Step 2: 添加 GET /tasks/{task_id}/session 端点**

在 `get_task` 后添加：

```python
@app.get("/tasks/{task_id}/session", response_model=SessionResponse)
def get_task_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """获取 Task 关联的 Session"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return SessionResponse(**session)
```

- [ ] **Step 3: 添加 DELETE /sessions/{task_id} 端点**

在 `get_task_session` 后添加：

```python
@app.delete("/sessions/{task_id}", status_code=204)
def delete_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除 Task 的 Session（软删除）"""
    session = task_db.get_session(task_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    task_db.soft_delete_session(task_id)
    return None
```

- [ ] **Step 4: 添加 POST /sessions/{task_id}/restore 端点**

```python
@app.post("/sessions/{task_id}/restore", response_model=SessionResponse)
def restore_session(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复 Session"""
    # Check if session exists and is deleted
    with sqlite3.connect(task_db.db_path) as conn:
        cursor = conn.execute(
            "SELECT * FROM sessions WHERE task_id = ? AND deleted_at IS NOT NULL",
            (task_id,)
        )
        row = cursor.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    task_db.restore_session(task_id)
    session = task_db.get_session(task_id)
    return SessionResponse(**session)
```

- [ ] **Step 5: 更新 GET /sessions 端点**

修改现有的 `/sessions` 端点使用 `SessionsListResponse`：

```python
@app.get("/sessions")
def get_sessions(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取所有 Session 列表"""
    sessions = task_db.list_sessions()
    return SessionsListResponse(sessions=sessions)
```

- [ ] **Step 6: Commit**

```bash
git add backend/src/api/routes.py
git commit -m "feat: add session API endpoints"
```

---

## Task 4: main.py - 添加迁移命令

**Files:**
- Modify: `backend/src/main.py`

- [ ] **Step 1: 添加迁移函数**

在文件顶部添加：

```python
def migrate_sessions():
    """从 session.json 迁移到数据库"""
    import json
    from db.database import get_task_db

    json_file = os.path.join(os.path.dirname(__file__), "..", "sessions", "session.json")
    if not os.path.exists(json_file):
        print("No session.json found, skipping migration")
        return

    with open(json_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            print("session.json is empty, skipping migration")
            return
        sessions_data = json.loads(content)

    task_db = get_task_db()
    migrated = 0
    skipped = 0

    for excel_path, info in sessions_data.items():
        # Check if task exists for this excel_path
        with sqlite3.connect(task_db.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM tasks WHERE result_file = ? AND deleted_at IS NULL",
                (excel_path,)
            )
            row = cursor.fetchone()

        if not row:
            print(f"Skipping {excel_path}: no associated task")
            skipped += 1
            continue

        task_id = row[0]
        existing = task_db.get_session(task_id)
        if existing:
            print(f"Skipping {excel_path}: session already exists")
            skipped += 1
            continue

        success = task_db.create_session(
            task_id=task_id,
            session_id=info.get("session_id"),
            excel_path=excel_path,
            title=info.get("title"),
            time_created=info.get("time_created"),
            time_updated=info.get("time_updated")
        )
        if success:
            print(f"Migrated {excel_path}")
            migrated += 1
        else:
            print(f"Failed to migrate {excel_path}")
            skipped += 1

    print(f"Migration complete: {migrated} migrated, {skipped} skipped")
```

- [ ] **Step 2: 更新 argparse**

修改 `main()` 函数：

```python
def main():
    parser = argparse.ArgumentParser(description='OpenCode Session Manager')
    parser.add_argument('--generate', action='store_true', help='生成 Excel 测试用例')
    parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE',
                        help='继续 session，读取 Excel 生成测试代码')
    parser.add_argument('--migrate-sessions', action='store_true',
                        help='从 session.json 迁移到数据库')
    args = parser.parse_args()

    if args.migrate_sessions:
        migrate_sessions()
    elif args.generate:
        # ... existing code
```

- [ ] **Step 3: 添加 sqlite3 import**

```python
import sqlite3
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/main.py
git commit -m "feat: add --migrate-sessions command"
```

---

## Task 5: 数据迁移

- [ ] **Step 1: 运行迁移命令**

```bash
cd backend && python -m src.main --migrate-sessions
```

预期输出：显示迁移了多少条，跳过了多少条

- [ ] **Step 2: 验证迁移结果**

```bash
cd backend && python -c "
from src.db.database import get_task_db
db = get_task_db()
sessions = db.list_sessions()
print(f'Total sessions in DB: {len(sessions)}')
for s in sessions:
    print(f\"  {s['excel_path']}: {s['id']}\")
"
```

- [ ] **Step 3: 验证 API**

```bash
curl http://localhost:8000/sessions
```

- [ ] **Step 4: Commit 迁移**

```bash
git add -A && git commit -m "data: migrate sessions from JSON to database"
```

---

## 自检清单

1. **Spec 覆盖**：
   - [x] sessions 表创建
   - [x] _migrate_sessions 迁移
   - [x] create_session, get_session, get_session_by_excel
   - [x] update_session_last_used, soft_delete_session, restore_session
   - [x] get_deleted_sessions, list_sessions
   - [x] services/session.py 改造
   - [x] Session API 端点
   - [x] --migrate-sessions 命令

2. **无循环依赖**：API → TaskDB → SQLite，单向依赖

3. **接口一致性**：Session 通过 TaskDB 管理
