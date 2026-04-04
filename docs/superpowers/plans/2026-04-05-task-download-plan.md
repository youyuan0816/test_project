# Task Download Feature Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add download functionality for completed tasks. Users can download generated Excel files from the TaskList.

**Architecture:** Backend serves files via `/download/:task_id` endpoint with security checks. Frontend opens download URL in new tab.

**Tech Stack:** FastAPI (Python), React, Ant Design

---

## File Structure

### Backend
- Modify: `backend/src/api.py` - Add `/download/:task_id` endpoint

### Frontend
- Modify: `src/components/TaskList.tsx` - Add download handler and button logic
- Modify: `src/services/types.ts` - TaskData interface needs `result_file` field (already exists in Task type)

---

## Backend Implementation

### Task 1: Add Download Endpoint

**Files:**
- Modify: `backend/src/api.py`

- [ ] **Step 1: Read current api.py**

```bash
# Read the file to understand current structure
```

- [ ] **Step 2: Add download endpoint**

Add this endpoint to `backend/src/api.py`:

```python
from fastapi.responses import FileResponse
import os

# Project root directory (parent of src/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

@app.get("/download/{task_id}")
def download_task_file(task_id: str):
    """Download the Excel file for a completed task"""
    # Get task from database
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed yet")
    
    result_file = task.get("result_file")
    if not result_file:
        raise HTTPException(status_code=404, detail="No file associated with this task")
    
    # Security check: ensure file is within test_cases/ directory
    if ".." in result_file or result_file.startswith("/") or not result_file.startswith("test_cases/"):
        raise HTTPException(status_code=400, detail="Invalid file path")
    
    # Construct full path
    full_path = os.path.join(PROJECT_ROOT, result_file)
    
    # Verify file exists
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    # Return file
    filename = os.path.basename(result_file)
    return FileResponse(
        path=full_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
```

- [ ] **Step 3: Test the endpoint**

Start backend and test:
```bash
# Start backend
cd /p/research/backend && python src/api.py

# In another terminal, test downloading a completed task
# First create a task and complete it, then:
curl -O http://localhost:8000/download/{task_id}
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/api.py
git commit -m "feat(api: add /download/:task_id endpoint for Excel files"
```

---

## Frontend Implementation

### Task 2: Update TaskList with Download Button

**Files:**
- Modify: `src/components/TaskList.tsx`
- Modify: `src/services/types.ts` (TaskData needs `result_file` field)

- [ ] **Step 1: Update TaskData interface in types.ts**

```typescript
// Add result_file to TaskData interface in types.ts
export interface TaskData {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  result?: string;
  result_file?: string;  // Add this field
}
```

- [ ] **Step 2: Update TaskList component**

Read current `src/components/TaskList.tsx`:

```typescript
// Current TaskList.tsx - need to update:
```

Update the columns to include `result_file` in the Action render:

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
      <Button size="small" danger onClick={() => removeTask(record.id)}>
        Remove
      </Button>
    </Space>
  ),
}
```

Add the download handler function:

```typescript
const handleDownload = (task: TaskData) => {
  if (task.result_file) {
    window.open(`/api/download/${task.id}`, '_blank');
  }
};
```

- [ ] **Step 3: Verify useTasks syncs result_file**

Check `src/hooks/useTasks.ts` - the sync function should already sync `result_file`:

```typescript
// In syncToLocalStore:
addTask({
  name: task.name,
  url: task.url,
  description: task.description,
  status: task.status,
  result: task.result_message,  // This is correct
  // result_file should also be synced
});
```

If not, add `result_file: task.result_file` to the addTask call.

- [ ] **Step 4: Build and test**

```bash
cd /p/research/frontend && npm run build 2>&1 | tail -10
```

Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
git add src/components/TaskList.tsx src/services/types.ts
git commit -m "feat(frontend): add download button to TaskList"
```

---

## Verification

1. Create a new task via the frontend
2. Wait for it to complete (status = completed)
3. Verify `result_file` field is populated in the task
4. Click "Download" button
5. File should download or open in new tab

---

## Spec Coverage Checklist

- [x] GET /download/:task_id endpoint - Task 1
- [x] Security check (test_cases/ directory) - Task 1
- [x] File existence check - Task 1
- [x] Frontend download button - Task 2
- [x] result_file sync in useTasks - Task 2
