# Fix Upload Excel 使用同一 Task 和 Session 设计

## 目标

修复上传 Excel 功能：
1. 上传新 Excel 时，复用**同一个 Task**
2. 使用该 Task 保存的 session_id 继续生成代码

## 当前问题

`POST /upload/:task_id` 接口在上传后会创建**新 Task** 来运行 continue_session，而不是更新当前 Task。

## 修改方案

**后端 `backend/src/api.py` - upload_excel_api 函数**：

删除创建新 Task 的代码，直接在当前 Task 中运行：

```python
# 修改前（有问题的代码）
continue_task_id = task_db.create_task(...)
thread = threading.Thread(target=run_continue_session, args=(continue_task_id, result_file))

# 修改后
task_db.update_task_status(task_id, "running")
result = continue_session(result_file)
status = "completed" if result["status"] in ("success", "warning") else "failed"
task_db.update_task_status(task_id, status, result_file=result_file, result_message=result["message"])
```

## 数据流（修改后）

```
Task 创建 → session_id 保存到 sessions.json
    ↓
上传新 Excel → 复用同一 Task → 从 sessions.json 获取 session_id → continue_session
```

## 文件修改

- `backend/src/api.py` - 修改 upload_excel_api 函数
