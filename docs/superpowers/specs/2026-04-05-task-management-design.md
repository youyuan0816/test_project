# Task Management System Design

## Overview

Add persistent task tracking with SQLite backend to replace the current in-memory task store.

## Database

**File**: `backend/tasks.db` (SQLite)

**Table**: `tasks`

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT PRIMARY KEY | Task ID (UUID) |
| name | TEXT NOT NULL | Task name / file path |
| task_type | TEXT NOT NULL | 'generate_excel' or 'generate_code' |
| url | TEXT | Target URL |
| description | TEXT | Task description |
| status | TEXT NOT NULL | pending / running / completed / failed |
| session_id | TEXT | Associated session ID |
| result_file | TEXT | Generated file path |
| result_message | TEXT | Success/error message |
| created_at | TEXT | ISO timestamp |
| completed_at | TEXT | ISO timestamp, nullable |

**Retention**: Auto-delete records older than 30 days (cleanup on startup)

## Backend API

### Endpoints

#### `GET /tasks`
Returns list of tasks (sorted by created_at DESC).

Response:
```json
{
  "tasks": [
    {
      "id": "uuid",
      "name": "test_cases/demo.xlsx",
      "task_type": "generate_excel",
      "url": "https://example.com",
      "description": "Test login flow",
      "status": "completed",
      "session_id": "ses_xxx",
      "result_file": "backend/test_cases/demo.xlsx",
      "result_message": "Excel generated successfully",
      "created_at": "2026-04-05T10:00:00",
      "completed_at": "2026-04-05T10:01:00"
    }
  ]
}
```

#### `GET /tasks/:id`
Returns single task details.

#### `POST /generate`
Create a new Excel generation task.

Request:
```json
{
  "url": "https://example.com",
  "filepath": "test_cases/demo.xlsx",
  "description": "Test login flow",
  "username": "",
  "password": ""
}
```

Response:
```json
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Task created"
}
```

#### `POST /continue`
Create a code generation task (continuing from Excel).

Request:
```json
{
  "excel_file": "test_cases/demo.xlsx"
}
```

Response:
```json
{
  "task_id": "uuid",
  "status": "pending",
  "message": "Task created"
}
```

## Frontend

### State Management
- Replace `taskStore.ts` with API polling
- `useTaskStore` → `useTasks` hook with React Query

### Polling
- Fetch `/tasks` every 5 seconds when Dashboard tab is active
- Stop polling when navigating away

### Task Status Display
- `pending`: gray tag
- `running`: blue tag + spinner
- `completed`: green tag
- `failed`: red tag

### UX Flow
1. User submits form → immediate redirect to TaskList view
2. Task appears in list with `pending` status
3. Poll updates status: pending → running → completed/failed
4. Completed tasks show result message

## Files to Modify

### Backend
- `backend/src/api.py` - Add /tasks endpoints
- `backend/src/db.py` - New: SQLite setup and helpers
- `backend/src/generator.py` - Update to create tasks and update status

### Frontend
- `src/stores/taskStore.ts` - Replace with `hooks/useTasks.ts`
- `src/components/NewTaskForm.tsx` - Redirect to TaskList on submit
- `src/pages/Dashboard.tsx` - Add polling logic
- `src/services/types.ts` - Update types for task_type and result_file

## Edge Cases
- Task cleanup runs on API startup (deletes records > 30 days)
- If backend is slow, task stays in "pending" until worker picks it up
- Network errors: React Query retry with exponential backoff
