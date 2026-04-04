# Session 存储迁移到数据库设计

## 目标

将 Session 存储从 `sessions/session.json` 迁移到 SQLite 数据库，与 Task 关联管理。

## 设计

### 1. 数据库表

**sessions 表：**
```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,           -- OpenCode session_id
    task_id TEXT NOT NULL UNIQUE,  -- 关联的 Task ID (1:1)
    excel_path TEXT,               -- 关联的 Excel 文件路径
    title TEXT,                   -- Session 标题
    time_created INTEGER,          -- OpenCode time_created (Unix timestamp)
    time_updated INTEGER,          -- OpenCode time_updated (Unix timestamp)
    last_used TEXT,               -- 最后使用时间 (ISO format)
    status TEXT DEFAULT 'active',  -- active/archived
    created_at TEXT NOT NULL,     -- 记录创建时间
    deleted_at TEXT               -- 软删除时间戳
);
```

**Migration：**
- `_migrate_sessions()` - 如果 sessions 表不存在则创建

### 2. 数据迁移

**迁移逻辑：**
1. 读取现有 `sessions/session.json`
2. 对于每个 entry：
   - 根据 excel_path 查找对应的 Task
   - 有 Task 则迁移：插入 sessions 表
   - 无 Task 则跳过
3. 迁移完成后标记成功

**迁移命令：** `python -m src.main --migrate-sessions`

### 3. Session 管理方法

**TaskDB 新增方法：**

```python
def create_session(task_id: str, session_id: str, excel_path: str = None,
                   title: str = None, time_created: int = None,
                   time_updated: int = None) -> bool:
    """创建 session 记录（1:1 关联 Task）"""

def get_session(task_id: str) -> Optional[dict]:
    """获取 Task 关联的 session"""

def update_session_last_used(task_id: str) -> bool:
    """更新最后使用时间"""

def soft_delete_session(task_id: str) -> bool:
    """软删除 session"""

def restore_session(task_id: str) -> bool:
    """恢复 session"""

def get_deleted_sessions() -> List[dict]:
    """获取已删除的 sessions（回收站）"""

def list_sessions() -> List[dict]:
    """列出所有 active sessions"""

def get_session_by_excel(excel_path: str) -> Optional[dict]:
    """根据 excel_path 查找 session（用于迁移时查找）"""
```

### 4. API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `GET /tasks/{task_id}/session` | GET | 获取 Task 关联的 Session |
| `GET /sessions` | GET | 列出所有 sessions（兼容） |
| `DELETE /sessions/{task_id}` | DELETE | 删除 Task 的 Session（软删除） |
| `POST /sessions/{task_id}/restore` | POST | 恢复 Session |

### 5. services/session.py 改造

**旧逻辑（移除）：**
- `load_sessions()` - 读 JSON
- `save_sessions()` - 写 JSON
- `save_session_id()` - 写 JSON

**新逻辑：**
- `get_session_id(excel_path)` → 调用 `TaskDB.get_session_by_excel()`
- `save_session_id()` → 调用 `TaskDB.create_session()` 或 `update_session_last_used()`

**兼容性：**
- `services/session.py` 保留现有函数签名
- 内部调用改为 TaskDB 方法
- JSON 文件迁移后只读

### 6. 数据流

```
generate_excel() 调用 save_session_id(excel_path, session_id)
    ↓
services/session.save_session_id()
    ↓
TaskDB.create_session() 或 update_session_last_used()
    ↓
sessions 表

get_session_id(excel_path) 调用
    ↓
services/session.get_session_id()
    ↓
TaskDB.get_session_by_excel()
    ↓
返回 session_id
```

### 7. 实现文件

| 文件 | 变更 |
|------|------|
| `db/database.py` | 新增 sessions 表，_migrate_sessions()，create_session() 等方法 |
| `services/session.py` | 内部调用改为 TaskDB 方法 |
| `api/routes.py` | 新增 Session API 端点 |
| `main.py` | 新增迁移命令 `--migrate-sessions` |
