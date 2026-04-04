# Task 删除功能设计

## 目标

为 Task 管理添加软删除功能，防止误删运行中的任务。

## 设计

### 1. 数据库变更

**Task 表新增字段：**
- `deleted_at TEXT` - 软删除时间戳，NULL 表示未删除

**Migration 逻辑：**
- `_migrate_deleted_at()` - 如果 `deleted_at` 字段不存在，执行 ALTER TABLE 添加

### 2. 删除接口

**DELETE /tasks/{task_id}**

**业务规则：**
- 只能删除 `completed` 或 `failed` 状态的任务
- `pending` 或 `running` 状态返回 400 错误：`"Cannot delete task in pending/running status"`
- 已删除的任务再次删除返回 404 错误

**返回：**
- 成功：204 No Content
- 任务不存在：404 Not Found
- 状态不允许删除：400 Bad Request

### 3. 查询过滤

**GET /tasks** - 默认不返回已删除任务
- WHERE `deleted_at IS NULL`

**GET /tasks/deleted** - 可选：查看已删除任务（回收站）
- WHERE `deleted_at IS NOT NULL`

### 4. 恢复接口（可选）

**POST /tasks/{task_id}/restore**

- 将 `deleted_at` 设回 NULL
- 只能恢复 `completed` 或 `failed` 状态的任务

## 实现文件

| 文件 | 变更 |
|------|------|
| `db/database.py` | 新增 `deleted_at` migration，`soft_delete_task()`，`restore_task()`，`get_deleted_tasks()` 方法 |
| `api/models.py` | `TaskResponse` 新增 `deleted_at` 字段 |
| `api/routes.py` | 新增 `DELETE /tasks/{task_id}`，`GET /tasks/deleted`，`POST /tasks/{task_id}/restore` |

## 数据流

```
DELETE /tasks/{task_id}
    → 检查任务是否存在
    → 检查任务状态 (completed/failed)
    → 设置 deleted_at = datetime.now()
    → 返回 204

GET /tasks
    → WHERE deleted_at IS NULL

GET /tasks/deleted
    → WHERE deleted_at IS NOT NULL
```
