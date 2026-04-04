# Task 删除功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Task 管理添加软删除功能，只能删除 completed/failed 状态的任务

**Architecture:** 在 TaskDB 添加软删除方法（soft_delete_task, restore_task, get_deleted_tasks），API 层添加删除/恢复接口，查询时默认过滤已删除任务

**Tech Stack:** Python, FastAPI, SQLite

---

## File Structure

| 文件 | 变更 |
|------|------|
| `backend/src/db/database.py` | TASK_COLUMNS 新增 deleted_at，新增 _migrate_deleted_at()，新增 soft_delete_task(), restore_task(), get_deleted_tasks() 方法 |
| `backend/src/api/models.py` | TaskResponse 新增 deleted_at 字段 |
| `backend/src/api/routes.py` | 新增 DELETE /tasks/{task_id}，GET /tasks/deleted，POST /tasks/{task_id}/restore |

---

## Task 1: 数据库层 - 添加 deleted_at 字段和软删除方法

**Files:**
- Modify: `backend/src/db/database.py:18-23`
- Modify: `backend/src/db/database.py:63-79`
- Modify: `backend/src/db/database.py:87-89`
- Modify: `backend/src/db/database.py:114-119`

- [ ] **Step 1: 更新 TASK_COLUMNS 添加 deleted_at**

修改 `backend/src/db/database.py` 第 18-23 行，在 TASK_COLUMNS 列表末尾添加 `deleted_at`：

```python
TASK_COLUMNS = [
    "id", "name", "task_type", "url", "description",
    "status", "phase", "session_id", "result_file", "result_message",
    "created_at", "completed_at", "deleted_at"
]
```

- [ ] **Step 2: 更新 _init_db 创建表语句添加 deleted_at 列**

修改 `backend/src/db/database.py` 第 44-62 行，在 CREATE TABLE 语句中添加 `deleted_at TEXT`：

```python
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
```

- [ ] **Step 3: 添加 _migrate_deleted_at 迁移方法**

在 `_migrate_phase` 方法后添加新方法 `backend/src/db/database.py` 第 80 行后：

```python
def _migrate_deleted_at(self):
    """Add deleted_at column if it doesn't exist (for existing databases)."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if "deleted_at" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN deleted_at TEXT")
            conn.commit()
```

- [ ] **Step 4: 在 _init_db 中调用 _migrate_deleted_at**

修改 `backend/src/db/database.py` 第 63-64 行：

```python
self._migrate_phase()
self._migrate_deleted_at()  # 新增
self._cleanup_old_tasks()
```

- [ ] **Step 5: 更新 _cleanup_old_tasks 过滤已删除任务**

修改 `backend/src/db/database.py` 第 66-70 行，在 DELETE 语句中添加条件：

```python
def _cleanup_old_tasks(self):
    cutoff = (datetime.now() - timedelta(days=TASK_RETENTION_DAYS)).isoformat()
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("DELETE FROM tasks WHERE created_at < ? AND deleted_at IS NULL", (cutoff,))
        conn.commit()
```

- [ ] **Step 6: 更新 list_tasks 过滤已删除任务**

修改 `backend/src/db/database.py` 第 114-119 行：

```python
def list_tasks(self) -> List[dict]:
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY created_at DESC")
        rows = cursor.fetchall()

    return [self._row_to_dict(row) for row in rows]
```

- [ ] **Step 7: 添加 soft_delete_task 方法**

在 `update_task_phase` 方法后添加新方法 `backend/src/db/database.py` 第 85 行后：

```python
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
```

- [ ] **Step 8: 添加 restore_task 方法**

在 `soft_delete_task` 方法后添加新方法：

```python
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
```

- [ ] **Step 9: 添加 get_deleted_tasks 方法**

在 `restore_task` 方法后添加新方法：

```python
def get_deleted_tasks(self) -> List[dict]:
    """Get all soft-deleted tasks (for recycle bin)."""
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("SELECT * FROM tasks WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC")
        rows = cursor.fetchall()

    return [self._row_to_dict(row) for row in rows]
```

- [ ] **Step 10: Commit**

```bash
git add backend/src/db/database.py
git commit -m "feat: add soft delete to TaskDB with deleted_at field"
```

---

## Task 2: API 模型层 - 添加 deleted_at 字段

**Files:**
- Modify: `backend/src/api/models.py:18-30`

- [ ] **Step 1: 更新 TaskResponse 添加 deleted_at 字段**

修改 `backend/src/api/models.py` 第 18-30 行，在 `completed_at` 后添加 `deleted_at`：

```python
class TaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    url: str
    description: str
    status: str
    phase: str
    session_id: Optional[str]
    result_file: Optional[str]
    result_message: Optional[str]
    created_at: str
    completed_at: Optional[str]
    deleted_at: Optional[str]  # 新增
```

- [ ] **Step 2: Commit**

```bash
git add backend/src/api/models.py
git commit -m "feat: add deleted_at field to TaskResponse model"
```

---

## Task 3: API 路由层 - 添加删除/恢复/回收站接口

**Files:**
- Modify: `backend/src/api/routes.py`
- Create: 路由端点

- [ ] **Step 1: 添加 DeletedTasksListResponse 模型**

在 `backend/src/api/routes.py` 第 16 行后添加导入，在文件适当位置添加新模型：

```python
class DeletedTasksListResponse(BaseModel):
    tasks: List[TaskResponse]
```

- [ ] **Step 2: 添加 DELETE /tasks/{task_id} 接口**

在 `get_task` 路由后添加删除接口 `backend/src/api/routes.py` 第 213 行后：

```python
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """删除任务（软删除，只能删除 completed 或 failed 状态的任务）"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.get("deleted_at") is not None:
        raise HTTPException(status_code=404, detail="Task not found")

    # 检查任务状态，只能删除 completed 或 failed
    if task["status"] not in (STATUS_COMPLETED, STATUS_FAILED):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete task in pending/running status"
        )

    task_db.soft_delete_task(task_id)
    return None
```

- [ ] **Step 3: 添加 GET /tasks/deleted 接口**

在删除接口后添加回收站接口：

```python
@app.get("/tasks/deleted", response_model=DeletedTasksListResponse)
def get_deleted_tasks(task_db: TaskDB = Depends(get_task_db_dep)):
    """获取已删除的任务列表（回收站）"""
    tasks = task_db.get_deleted_tasks()
    return DeletedTasksListResponse(tasks=tasks)
```

- [ ] **Step 4: 添加 POST /tasks/{task_id}/restore 接口**

在回收站接口后添加恢复接口：

```python
@app.post("/tasks/{task_id}/restore", response_model=TaskResponse)
def restore_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    """恢复已删除的任务"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.get("deleted_at") is None:
        raise HTTPException(status_code=400, detail="Task is not deleted")

    success = task_db.restore_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")

    # 返回恢复后的任务
    restored_task = task_db.get_task(task_id)
    return TaskResponse(**restored_task)
```

- [ ] **Step 5: 更新 get_task 接口过滤已删除任务**

修改现有的 `get_task` 接口，在第 208-213 行处理已删除情况：

```python
@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: str, task_db: TaskDB = Depends(get_task_db_dep)):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.get("deleted_at") is not None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**task)
```

- [ ] **Step 6: Commit**

```bash
git add backend/src/api/routes.py
git commit -m "feat: add soft delete and restore API endpoints"
```

---

## 自检清单

1. **Spec 覆盖**：
   - [x] deleted_at 字段添加
   - [x] _migrate_deleted_at 迁移
   - [x] soft_delete_task 软删除方法
   - [x] restore_task 恢复方法
   - [x] get_deleted_tasks 回收站方法
   - [x] list_tasks 过滤已删除
   - [x] DELETE /tasks/{task_id} 接口
   - [x] GET /tasks/deleted 回收站接口
   - [x] POST /tasks/{task_id}/restore 恢复接口
   - [x] TaskResponse.deleted_at 字段

2. **无循环依赖**：API → DB，单向依赖

3. **接口一致性**：使用 STATUS_COMPLETED, STATUS_FAILED 常量
