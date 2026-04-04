# Task 阶段显示实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Task 添加 phase 字段，在 Status 区域显示不同颜色和阶段信息

**Architecture:** 后端添加 phase 字段，前端根据 phase 显示不同的颜色和标签

**Tech Stack:** SQLite, React, Ant Design

---

## Task 1: 后端添加 phase 字段

**Files:**
- Modify: `backend/src/db.py`

- [ ] **Step 1: 更新 TASK_COLUMNS 常量**

```python
TASK_COLUMNS = [
    "id", "name", "task_type", "url", "description",
    "status", "session_id", "result_file", "result_message",
    "created_at", "completed_at", "phase"  # 添加 phase
]
```

- [ ] **Step 2: 添加 Phase 常量**

```python
# Phase constants
PHASE_EXCEL = "excel_generation"
PHASE_CODE = "code_generation"
```

- [ ] **Step 3: 更新 _init_db 创建表语句**

```python
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
        completed_at TEXT,
        phase TEXT DEFAULT 'excel_generation'
    )
""")
```

- [ ] **Step 4: 添加 ALTER TABLE 迁移（如果表已存在）**

```python
# 检查并添加 phase 列（向后兼容）
def _migrate_phase(self):
    with sqlite3.connect(self.db_path) as conn:
        cursor = conn.execute("PRAGMA table_info(tasks)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'phase' not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN phase TEXT DEFAULT 'excel_generation'")
            conn.commit()
```

在 `_init_db` 末尾调用 `self._migrate_phase()`

- [ ] **Step 5: 添加 update_task_phase 方法**

```python
def update_task_phase(self, task_id: str, phase: str):
    with sqlite3.connect(self.db_path) as conn:
        conn.execute("UPDATE tasks SET phase = ? WHERE id = ?", (phase, task_id))
        conn.commit()
```

- [ ] **Step 6: Commit**

```bash
git add backend/src/db.py
git commit -m "feat: add phase field to Task model"
```

---

## Task 2: 后端 API 设置 phase

**Files:**
- Modify: `backend/src/api.py`

- [ ] **Step 1: 添加 phase 常量导入**

```python
from db import TaskDB, PHASE_EXCEL, PHASE_CODE
```

- [ ] **Step 2: 在 generate_excel_api 中设置 phase=excel_generation**

```python
# Create task
task_id = task_db.create_task(...)
task_db.update_task_phase(task_id, PHASE_EXCEL)
```

- [ ] **Step 3: 在 upload_excel_api 中设置 phase=code_generation**

```python
# 上传后设置阶段为代码生成
task_db.update_task_phase(task_id, PHASE_CODE)
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/api.py
git commit -m "feat: set task phase in API endpoints"
```

---

## Task 3: 前端添加翻译

**Files:**
- Modify: `frontend/src/locales/zh.json`
- Modify: `frontend/src/locales/en.json`

- [ ] **Step 1: 添加 phase 翻译**

zh.json:
```json
"phase": {
  "excel_generation": "Excel生成中",
  "code_generation": "代码生成中"
}
```

en.json:
```json
"phase": {
  "excel_generation": "Generating Excel",
  "code_generation": "Generating Code"
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/locales/zh.json frontend/src/locales/en.json
git commit -m "feat: add phase translation keys"
```

---

## Task 4: 前端显示阶段标签

**Files:**
- Modify: `frontend/src/components/TaskList.tsx`

- [ ] **Step 1: 更新 TaskData 接口**

```typescript
interface TaskData {
  // ... 现有字段
  phase?: 'excel_generation' | 'code_generation';
}
```

- [ ] **Step 2: 修改 Status 列渲染**

```tsx
{
  title: t('task.status'),
  dataIndex: 'status',
  key: 'status',
  render: (status: string, record: TaskData) => {
    const phase = record.phase || 'excel_generation';
    const phaseColor = phase === 'excel_generation' ? 'blue' : 'purple';
    const statusColor =
      status === 'completed' ? 'green' :
      status === 'failed' ? 'red' :
      status === 'running' ? phaseColor : 'default';

    return (
      <Space>
        <Tag color={phaseColor}>{t(`phase.${phase}`)}</Tag>
        <Tag color={statusColor}>{t(`status.${status}`)}</Tag>
      </Space>
    );
  },
},
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/TaskList.tsx
git commit -m "feat: display task phase in status column"
```

---

## 自检清单

1. **Spec 覆盖**：
   - [x] phase 字段添加
   - [x] API 设置 phase
   - [x] 翻译添加
   - [x] 前端显示

2. **类型一致性**：phase 值在前后端一致

3. **无占位符**：所有代码完整
