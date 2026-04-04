# Fix Upload Excel 使用同一 Task 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复上传 Excel 功能，上传时复用同一个 Task 而不是创建新 Task

**Architecture:** 修改 `POST /upload/:task_id` 接口，删除创建新 Task 的代码，改为直接更新当前 Task 状态并运行 continue_session

**Tech Stack:** FastAPI, threading

---

## Task 1: 修改 upload_excel_api 使用同一 Task

**Files:**
- Modify: `backend/src/api.py:153-222`

- [ ] **Step 1: 查看当前代码**

当前代码在 lines 200-222 创建了新 Task：
```python
# Create a new task for generating test code
new_task_id = task_db.create_task(...)
thread = threading.Thread(target=run_continue_session, args=(new_task_id, excel_relative))
thread.start()
return {"task_id": new_task_id, ...}
```

- [ ] **Step 2: 修改为使用同一 Task**

删除创建新 Task 的代码，改为直接在当前 Task 中运行：

```python
# 直接在当前 Task 中运行 continue_session
task_db.update_task_status(task_id, "running")

# Start background worker to generate test code using SAME task_id
excel_relative = os.path.relpath(base_dir, PROJECT_ROOT)
excel_relative = excel_relative.replace(os.sep, '/')
thread = threading.Thread(
    target=run_continue_session,
    args=(task_id, excel_relative)  # 使用同一个 task_id
)
thread.start()

return {
    "task_id": task_id,  # 返回原来的 task_id
    "status": "pending",
    "message": "File uploaded and test code generation started in background"
}
```

- [ ] **Step 3: Commit**

```bash
git add backend/src/api.py
git commit -m "fix: upload uses same task_id instead of creating new task"
```
