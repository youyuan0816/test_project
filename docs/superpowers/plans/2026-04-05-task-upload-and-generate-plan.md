# Task 上传 Excel 和生成代码功能实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为每个 Task 添加上传 Excel 替换文件和手动触发生成测试代码的功能

**Architecture:** 后端新增 `/upload/:task_id` 接口接收文件并替换 task 的 Excel，然后触发 `continue_session`；前端 TaskList 每行添加「上传 Excel」和「生成代码」两个按钮

**Tech Stack:** FastAPI, React + Ant Design, axios

---

## 文件结构

- `backend/src/api.py` - 新增 `/upload/:task_id` 端点
- `frontend/src/services/api.ts` - 新增 `uploadExcel` 方法
- `frontend/src/components/TaskList.tsx` - 添加上传和生成代码按钮

---

## Task 1: 后端添加上传接口

**Files:**
- Modify: `backend/src/api.py:42-50` (在 ContinueRequest class 后添加新接口)

- [ ] **Step 1: 添加 UploadRequest model**

```python
class UploadRequest(BaseModel):
    file: UploadFile  # FastAPI 的上传文件类型
```

- [ ] **Step 2: 添加 run_upload_session 后台 worker**

```python
def run_upload_session(task_id: str, excel_file: str):
    """Background worker for uploading new Excel and generating code"""
    try:
        task_db.update_task_status(task_id, "running")
        result = continue_session(excel_file)
        status = "completed" if result["status"] in ("success", "warning") else "failed"
        task_db.update_task_status(task_id, status, result_file=excel_file, result_message=result["message"])
    except Exception as e:
        task_db.update_task_status(task_id, "failed", result_message=str(e))
```

- [ ] **Step 3: 添加 POST /upload/:task_id 接口**

```python
from fastapi import UploadFile, File

@app.post("/upload/{task_id}")
def upload_task_file(task_id: str, file: UploadFile = File(...)):
    """上传 Excel 文件替换该 task 的文件，并触发生成测试代码"""
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=400, detail="No result file associated with this task")

    # 保存上传的文件到 result_file 路径
    normalized = os.path.normpath(result_file.replace('/', os.sep))
    full_dir = os.path.join(PROJECT_ROOT, normalized)

    # 如果是目录，找到目录下的 xlsx 文件路径
    if os.path.isdir(full_dir):
        # 获取目录下原来的 xlsx 文件名
        old_files = [f for f in os.listdir(full_dir) if f.endswith('.xlsx')]
        if old_files:
            full_path = os.path.join(full_dir, old_files[0])
        else:
            raise HTTPException(status_code=400, detail="No existing xlsx file to replace")
    else:
        full_path = full_dir

    # 写入新文件
    content = await file.read()
    with open(full_path, 'wb') as f:
        f.write(content)

    # 触发生成代码（异步）
    thread = threading.Thread(
        target=run_upload_session,
        args=(task_id, result_file)
    )
    thread.start()

    return {"task_id": task_id, "status": "pending", "message": "File uploaded, generating code in background"}
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/api.py
git commit -m "feat: add POST /upload/:task_id endpoint"
```

---

## Task 2: 前端添加 uploadExcel API

**Files:**
- Modify: `frontend/src/services/api.ts:32-36`

- [ ] **Step 1: 添加 uploadExcel 方法**

```typescript
uploadExcel: async (taskId: string, file: File): Promise<CreateTaskResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE}/upload/${taskId}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
},
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/services/api.ts
git commit -m "feat: add uploadExcel API method"
```

---

## Task 3: TaskList 添加操作按钮

**Files:**
- Modify: `frontend/src/components/TaskList.tsx:61-78` (Action 列)

- [ ] **Step 1: 添加 Upload 组件和相关状态**

```typescript
import { useState } from 'react';
import { Upload, Button, Space, message } from 'antd';
import { api } from '@/services/api';
import type { UploadFile } from 'antd/es/upload/interface';

// TaskData interface 保持不变...

export function TaskList() {
  const { tasks, removeTask } = useTaskStore();
  const [uploadingTasks, setUploadingTasks] = useState<Set<string>>(new Set());
  const [generatingTasks, setGeneratingTasks] = useState<Set<string>>(new Set());

  const handleDownload = (task: TaskData) => {
    if (task.result_file) {
      window.open(`/api/download/${task.id}`, '_blank');
    }
  };

  const handleUpload = async (task: TaskData, file: File) => {
    setUploadingTasks(prev => new Set(prev).add(task.id));
    try {
      await api.uploadExcel(task.id, file);
      message.success('File uploaded, generating code...');
    } catch (error) {
      message.error('Upload failed: ' + (error as Error).message);
    } finally {
      setUploadingTasks(prev => {
        const next = new Set(prev);
        next.delete(task.id);
        return next;
      });
    }
  };

  const handleGenerate = async (task: TaskData) => {
    setGeneratingTasks(prev => new Set(prev).add(task.id));
    try {
      await api.continueSession({ excel_file: task.result_file! });
      message.success('Generating code...');
    } catch (error) {
      message.error('Generate failed: ' + (error as Error).message);
    } finally {
      setGeneratingTasks(prev => {
        const next = new Set(prev);
        next.delete(task.id);
        return next;
      });
    }
  };
```

- [ ] **Step 2: 修改 Action 列，添加上传和生成按钮**

```typescript
{
  title: 'Action',
  key: 'action',
  render: (_: unknown, record: TaskData) => (
    <Space>
      {record.status === 'completed' && record.result_file && (
        <Button
          size="small"
          type="primary"
          onClick={() => handleDownload(record)}
        >
          Download
        </Button>
      )}
      <Upload
        accept=".xlsx"
        showUploadList={false}
        beforeUpload={(file) => {
          handleUpload(record, file);
          return false; // 阻止自动上传
        }}
      >
        <Button size="small" loading={uploadingTasks.has(record.id)}>
          Upload Excel
        </Button>
      </Upload>
      <Button
        size="small"
        onClick={() => handleGenerate(record)}
        loading={generatingTasks.has(record.id)}
        disabled={!record.result_file}
      >
        Generate Code
      </Button>
      <Button size="small" danger onClick={() => removeTask(record.id)}>
        Remove
      </Button>
    </Space>
  ),
},
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/TaskList.tsx
git commit -m "feat: add upload and generate buttons to TaskList"
```

---

## 自检清单

1. **Spec 覆盖**：
   - [x] 上传 Excel 替换文件 → Task 1, 2, 3
   - [x] 上传后立即生成 → Task 1 (run_upload_session 调用 continue_session)
   - [x] 手动生成代码按钮 → Task 3 (Generate Code 按钮)

2. **类型一致性**：taskId 参数在 api.ts 和 TaskList.tsx 中一致使用

3. **无占位符**：所有步骤都包含完整实现代码
