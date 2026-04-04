# Task Download Feature Design

## Overview

Add download functionality for completed tasks. Generated Excel files are stored in a fixed directory (`backend/test_cases/`).

## File Path Rules

- All generated files saved to `backend/test_cases/`
- Example: `test_cases/google.xlsx`
- `result_file` stores relative path from `backend/` directory

## Backend API

### `GET /download/:task_id`

Downloads the Excel file for a completed task.

**Response:**
- `200`: File stream with `Content-Disposition` header
- `404`: Task not found
- `400`: File not in `test_cases/` directory (security check)
- `404`: File does not exist on disk

**Implementation:**
1. Get task from database by `task_id`
2. Validate `result_file` is within `test_cases/` directory (path traversal protection)
3. Construct full path: `backend/` + `result_file`
4. Return file stream using `FileResponse` or streaming

## Frontend

### TaskList Changes

1. **TaskData interface** - Add `result_file?: string` field
2. **Download button** - Only show when `status === 'completed'` AND `result_file` exists
3. **Download handler**:
   ```typescript
   const handleDownload = (task: TaskData) => {
     window.open(`/api/download/${task.id}`, '_blank');
   };
   ```

### useTasks Sync

Ensure `result_file` is synced from backend Task to local TaskData.

## Security

- Only allow downloads from `test_cases/` directory
- Reject any path containing `..` or absolute paths
- Validate file exists on disk before serving

## Files to Modify

### Backend
- `backend/src/api.py` - Add `/download/:task_id` endpoint

### Frontend
- `src/components/TaskList.tsx` - Add download handler and button logic
- `src/services/types.ts` - TaskData interface (already has result_file via Task type)
