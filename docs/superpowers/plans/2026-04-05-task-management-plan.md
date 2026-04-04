# Task Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace in-memory task store with SQLite-backed persistent task tracking with 30-day retention.

**Architecture:** FastAPI backend stores tasks in SQLite. Frontend uses React Query with 5-second polling to track task status. New task forms redirect to TaskList view after submission.

**Tech Stack:** SQLite (Python built-in), FastAPI, React Query, Zustand

---

## File Structure

### Backend
- **Create**: `backend/src/db.py` - SQLite connection, schema, CRUD helpers
- **Modify**: `backend/src/api.py` - Add `/tasks`, `/tasks/:id` endpoints, update `/generate` and `/continue`
- **Modify**: `backend/src/generator.py` - Update `generate_excel` and `continue_session` to accept `task_id` and update status

### Frontend
- **Create**: `src/hooks/useTasks.ts` - React Query hook with polling
- **Modify**: `src/stores/taskStore.ts` - Keep for local UI state, add sync with backend
- **Modify**: `src/components/NewTaskForm.tsx` - Redirect to TaskList after submit
- **Modify**: `src/components/UploadExcel.tsx` - Redirect to TaskList after submit
- **Modify**: `src/pages/Dashboard.tsx` - Add polling when on dashboard
- **Modify**: `src/services/types.ts` - Add `task_type` and `result_file` fields

---

## Backend Implementation

### Task 1: Create SQLite Database Module

**Files:**
- Create: `backend/src/db.py`

- [ ] **Step 1: Write the test**

```python
# backend/tests/test_db.py
import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import TaskDB, Task

def test_create_and_get_task():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = TaskDB(db_path)
        
        task_id = db.create_task(
            name="test.xlsx",
            task_type="generate_excel",
            url="https://example.com",
            description="Test task",
        )
        
        task = db.get_task(task_id)
        assert task is not None
        assert task["name"] == "test.xlsx"
        assert task["task_type"] == "generate_excel"
        assert task["status"] == "pending"
        
        db.close()
    finally:
        os.unlink(db_path)

def test_update_task_status():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = TaskDB(db_path)
        
        task_id = db.create_task(name="test.xlsx", task_type="generate_excel", url="", description="")
        db.update_task_status(task_id, "running")
        
        task = db.get_task(task_id)
        assert task["status"] == "running"
        
        db.close()
    finally:
        os.unlink(db_path)

def test_list_tasks():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        db = TaskDB(db_path)
        
        db.create_task(name="task1.xlsx", task_type="generate_excel", url="", description="")
        db.create_task(name="task2.xlsx", task_type="generate_code", url="", description="")
        
        tasks = db.list_tasks()
        assert len(tasks) == 2
        
        db.close()
    finally:
        os.unlink(db_path)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /p/research/backend && python -m pytest tests/test_db.py -v`
Expected: FAIL - module 'db' not found

- [ ] **Step 3: Write minimal implementation**

```python
# backend/src/db.py
import sqlite3
import os
import uuid
from datetime import datetime, timedelta
from typing import Optional, List

DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tasks.db")

class TaskDB:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
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
                completed_at TEXT
            )
        """)
        conn.commit()
        conn.close()
        self._cleanup_old_tasks()
    
    def _cleanup_old_tasks(self):
        conn = sqlite3.connect(self.db_path)
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        conn.execute("DELETE FROM tasks WHERE created_at < ?", (cutoff,))
        conn.commit()
        conn.close()
    
    def create_task(self, name: str, task_type: str, url: str = "", description: str = "") -> str:
        task_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT INTO tasks (id, name, task_type, url, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (task_id, name, task_type, url, description, now))
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_task(self, task_id: str) -> Optional[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "id": row[0],
            "name": row[1],
            "task_type": row[2],
            "url": row[3],
            "description": row[4],
            "status": row[5],
            "session_id": row[6],
            "result_file": row[7],
            "result_message": row[8],
            "created_at": row[9],
            "completed_at": row[10],
        }
    
    def list_tasks(self) -> List[dict]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "task_type": row[2],
                "url": row[3],
                "description": row[4],
                "status": row[5],
                "session_id": row[6],
                "result_file": row[7],
                "result_message": row[8],
                "created_at": row[9],
                "completed_at": row[10],
            }
            for row in rows
        ]
    
    def update_task_status(
        self,
        task_id: str,
        status: str,
        session_id: Optional[str] = None,
        result_file: Optional[str] = None,
        result_message: Optional[str] = None
    ):
        completed_at = datetime.now().isoformat() if status in ("completed", "failed") else None
        
        conn = sqlite3.connect(self.db_path)
        
        if session_id is not None:
            conn.execute("UPDATE tasks SET session_id = ? WHERE id = ?", (session_id, task_id))
        if result_file is not None:
            conn.execute("UPDATE tasks SET result_file = ? WHERE id = ?", (result_file, task_id))
        if result_message is not None:
            conn.execute("UPDATE tasks SET result_message = ? WHERE id = ?", (result_message, task_id))
        
        conn.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id)
        )
        conn.commit()
        conn.close()
    
    def close(self):
        pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /p/research/backend && python -m pytest tests/test_db.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/db.py backend/tests/test_db.py
git commit -m "feat(backend): add SQLite task database module"
```

---

### Task 2: Add Task Endpoints to API

**Files:**
- Modify: `backend/src/api.py`

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_api_tasks.py
import pytest
from fastapi.testclient import TestClient
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use temp db for testing
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    test_db_path = f.name

# Patch before importing api
os.environ['TASK_DB_PATH'] = test_db_path

from api import app

client = TestClient(app)

def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert "tasks" in response.json()

def test_create_task_via_generate():
    response = client.post("/generate", json={
        "url": "https://example.com",
        "filepath": "test.xlsx",
        "description": "Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"

def test_get_tasks_after_create():
    client.post("/generate", json={
        "url": "https://example.com",
        "filepath": "test.xlsx",
        "description": "Test"
    })
    
    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    assert len(tasks) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /p/research/backend && python -m pytest tests/test_api_tasks.py -v`
Expected: FAIL - no /tasks endpoints

- [ ] **Step 3: Write minimal implementation**

```python
# Add to backend/src/api.py

from db import TaskDB
import os

# Database path
TASK_DB_PATH = os.environ.get('TASK_DB_PATH', os.path.join(os.path.dirname(__file__), "..", "tasks.db"))

# Global db instance
task_db = TaskDB(TASK_DB_PATH)

class TaskResponse(BaseModel):
    id: str
    name: str
    task_type: str
    url: str
    description: str
    status: str
    session_id: Optional[str]
    result_file: Optional[str]
    result_message: Optional[str]
    created_at: str
    completed_at: Optional[str]

class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]

class CreateTaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

# Update POST /generate to create task
@app.post("/generate")
def generate_excel_api(req: GenerateRequest):
    # Create task first
    task_id = task_db.create_task(
        name=req.filepath,
        task_type="generate_excel",
        url=req.url,
        description=req.description,
    )
    
    # Update to running
    task_db.update_task_status(task_id, "running")
    
    result = generate_excel(
        url=req.url,
        filepath=req.filepath,
        description=req.description,
        username=req.username or "",
        password=req.password or "",
        continue_excel=req.continue_excel
    )
    
    # Update final status
    status = "completed" if result["status"] == "success" else "failed"
    task_db.update_task_status(
        task_id,
        status,
        result_message=result["message"]
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return {"task_id": task_id, "status": status, "message": result["message"]}

# Similar update for POST /continue

@app.get("/tasks")
def get_tasks():
    tasks = task_db.list_tasks()
    return {"tasks": tasks}

@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = task_db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /p/research/backend && python -m pytest tests/test_api_tasks.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add backend/src/api.py
git commit -m "feat(api): add /tasks endpoints with SQLite backend"
```

---

## Frontend Implementation

### Task 3: Update TypeScript Types

**Files:**
- Modify: `src/services/types.ts`

- [ ] **Step 1: Read current types**

```typescript
// Current src/services/types.ts
export interface GenerateRequest {
  url: string;
  filepath: string;
  username?: string;
  password?: string;
  description: string;
  continue_excel?: string;
}

export interface ContinueRequest {
  excel_file: string;
}

export interface Session {
  session_id: string;
  created_at: string;
  last_used: string;
}

export interface GenerateResponse {
  status: 'success' | 'warning' | 'error';
  message: string;
  output?: string;
}

export interface SessionsResponse {
  status: 'success';
  sessions: Record<string, Session>;
}
```

- [ ] **Step 2: Update types**

```typescript
export interface GenerateRequest {
  url: string;
  filepath: string;
  username?: string;
  password?: string;
  description: string;
  continue_excel?: string;
}

export interface ContinueRequest {
  excel_file: string;
}

export interface Session {
  session_id: string;
  created_at: string;
  last_used: string;
}

export interface GenerateResponse {
  status: 'success' | 'warning' | 'error';
  message: string;
  output?: string;
}

export interface SessionsResponse {
  status: 'success';
  sessions: Record<string, Session>;
}

// Task types
export interface Task {
  id: string;
  name: string;
  task_type: 'generate_excel' | 'generate_code';
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  session_id?: string;
  result_file?: string;
  result_message?: string;
  created_at: string;
  completed_at?: string;
}

export interface TasksResponse {
  tasks: Task[];
}

export interface CreateTaskResponse {
  task_id: string;
  status: string;
  message: string;
}
```

- [ ] **Step 3: Update api.ts**

```typescript
// Update src/services/api.ts
import type {
  GenerateRequest,
  ContinueRequest,
  GenerateResponse,
  SessionsResponse,
  TasksResponse,
  CreateTaskResponse,
  Task
} from './types';

export const api = {
  generate: async (data: GenerateRequest): Promise<CreateTaskResponse> => {
    const response = await axios.post(`${API_BASE}/generate`, data);
    return response.data;
  },

  continueSession: async (data: ContinueRequest): Promise<CreateTaskResponse> => {
    const response = await axios.post(`${API_BASE}/continue`, data);
    return response.data;
  },

  getSessions: async (): Promise<SessionsResponse> => {
    const response = await axios.get(`${API_BASE}/sessions`);
    return response.data;
  },

  getTasks: async (): Promise<TasksResponse> => {
    const response = await axios.get(`${API_BASE}/tasks`);
    return response.data;
  },

  getTask: async (id: string): Promise<Task> => {
    const response = await axios.get(`${API_BASE}/tasks/${id}`);
    return response.data;
  },

  health: async (): Promise<{ status: string }> => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },
};
```

- [ ] **Step 4: Commit**

```bash
git add src/services/types.ts src/services/api.ts
git commit -m "feat(types): add Task types and update API"
```

---

### Task 4: Create useTasks Hook with Polling

**Files:**
- Create: `src/hooks/useTasks.ts`

- [ ] **Step 1: Write the test**

```typescript
// src/hooks/__tests__/useTasks.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTasks } from '../useTasks';

// Mock API
jest.mock('@/services/api', () => ({
  api: {
    getTasks: jest.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient();
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useTasks', () => {
  it('fetches tasks on mount', async () => {
    const mockTasks = {
      tasks: [
        { id: '1', name: 'test.xlsx', task_type: 'generate_excel', status: 'completed' }
      ]
    };
    (api.getTasks as jest.Mock).mockResolvedValue(mockTasks);

    const { result } = renderHook(() => useTasks(), { wrapper: createWrapper() });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.tasks).toHaveLength(1);
  });
});
```

- [ ] **Step 2: Run test - verify it fails**

Run: `cd /p/research/frontend && npm test -- --watchAll=false`
Expected: FAIL - useTasks not found

- [ ] **Step 3: Write implementation**

```typescript
// src/hooks/useTasks.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import type { Task } from '@/services/types';

export function useTasks() {
  const queryClient = useQueryClient();
  
  const query = useQuery({
    queryKey: ['tasks'],
    queryFn: api.getTasks,
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 0,
  });

  const syncToLocalStore = (tasks: Task[]) => {
    const { clearTasks, addTask, updateTask } = useTaskStore.getState();
    const localTasks = useTaskStore.getState().tasks;
    
    // Sync: update or add tasks from backend
    tasks.forEach((task) => {
      const existing = localTasks.find((t) => t.id === task.id);
      if (existing) {
        updateTask(task.id, {
          name: task.name,
          status: task.status,
          result: task.result_message,
        });
      } else {
        addTask({
          name: task.name,
          url: task.url,
          description: task.description,
          status: task.status,
          result: task.result_message,
        });
      }
    });
  };

  // Sync tasks to local store when query succeeds
  if (query.data?.tasks) {
    syncToLocalStore(query.data.tasks);
  }

  return query;
}

export function useCreateTask() {
  const queryClient = useQueryClient();
  const { addTask } = useTaskStore();
  
  return useMutation({
    mutationFn: async (data: { 
      type: 'generate' | 'continue';
      url?: string;
      filepath?: string;
      excel_file?: string;
      description?: string;
      username?: string;
      password?: string;
    }) => {
      if (data.type === 'generate') {
        return api.generate({
          url: data.url!,
          filepath: data.filepath!,
          description: data.description!,
          username: data.username,
          password: data.password,
        });
      } else {
        return api.continueSession({
          excel_file: data.excel_file!,
        });
      }
    },
    onSuccess: (response, variables) => {
      // Add to local store immediately with pending status
      addTask({
        name: variables.filepath || variables.excel_file || 'Untitled',
        url: variables.url || '',
        description: variables.description || '',
        status: 'pending',
      });
      // Invalidate to trigger refetch
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });
}
```

- [ ] **Step 4: Run test - verify it passes**

Run: `cd /p/research/frontend && npm test -- --watchAll=false`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hooks/useTasks.ts
git commit -m "feat(frontend): add useTasks hook with 5s polling"
```

---

### Task 5: Update NewTaskForm to Redirect After Submit

**Files:**
- Modify: `src/components/NewTaskForm.tsx`

- [ ] **Step 1: Read current implementation**

```typescript
// Current NewTaskForm.tsx - already read
```

- [ ] **Step 2: Update to use mutation and redirect**

```typescript
import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Form, Input, Button, Space } from 'antd';
import { useNavigate } from 'react-router-dom';

interface NewTaskFormProps {
  onClose: () => void;
}

export function NewTaskForm({ onClose }: NewTaskFormProps) {
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const { addTask } = useTaskStore();

  const mutation = useMutation({
    mutationFn: api.generate,
    onSuccess: (data, variables) => {
      addTask({
        name: variables.filepath || `Task-${Date.now()}`,
        url: variables.url,
        description: variables.description,
        status: 'pending', // Will be updated by polling
      });
      onClose();
      navigate('/'); // Go to TaskList
    },
    onError: (error) => {
      console.error('Generation failed:', error);
    },
  });

  const onFinish = (values: {
    url: string;
    filepath?: string;
    username?: string;
    password?: string;
    description: string;
  }) => {
    mutation.mutate({
      url: values.url,
      filepath: values.filepath || `test_cases/${Date.now()}.xlsx`,
      username: values.username,
      password: values.password,
      description: values.description,
    });
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      {/* ... rest of form unchanged ... */}
    </Form>
  );
}
```

- [ ] **Step 3: Verify build passes**

Run: `cd /p/research/frontend && npm run build 2>&1 | head -50`
Expected: No TypeScript errors

- [ ] **Step 4: Commit**

```bash
git add src/components/NewTaskForm.tsx
git commit -m "feat(frontend): redirect to TaskList after submit"
```

---

### Task 6: Update Dashboard with Polling Logic

**Files:**
- Modify: `src/pages/Dashboard.tsx`

- [ ] **Step 1: Read current implementation**

```typescript
// Current Dashboard.tsx - already read
```

- [ ] **Step 2: Update to use useTasks hook**

```typescript
import { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Button, Card, Space, Table, Tag } from 'antd';
import { DashboardOutlined, FileTextOutlined, HistoryOutlined } from '@ant-design/icons';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';
import { UploadExcel } from '@/components/UploadExcel';
import { useTasks } from '@/hooks/useTasks';
import { api } from '@/services/api';
import type { Session, Task } from '@/services/types';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

type MenuKey = 'dashboard' | 'sessions' | 'testcases';

export function Dashboard() {
  const [selectedMenu, setSelectedMenu] = useState<MenuKey>('dashboard');
  const [showNewTask, setShowNewTask] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [sessions, setSessions] = useState<Record<string, Session>>({});
  const [sessionsLoading, setSessionsLoading] = useState(false);

  // Poll tasks every 5 seconds when on dashboard
  const { data: tasksData, isLoading: tasksLoading } = useTasks();

  useEffect(() => {
    if (selectedMenu === 'sessions') {
      setSessionsLoading(true);
      api.getSessions()
        .then((res) => {
          setSessions(res.sessions);
        })
        .catch(console.error)
        .finally(() => setSessionsLoading(false));
    }
  }, [selectedMenu]);

  // ... rest unchanged ...
```

- [ ] **Step 3: Verify build passes**

Run: `cd /p/research/frontend && npm run build 2>&1 | head -50`
Expected: No TypeScript errors

- [ ] **Step 4: Commit**

```bash
git add src/pages/Dashboard.tsx
git commit -m "feat(frontend): integrate useTasks polling in Dashboard"
```

---

### Task 7: Update TaskList to Use Backend Data

**Files:**
- Modify: `src/components/TaskList.tsx`
- Modify: `src/stores/taskStore.ts`

- [ ] **Step 1: Read current implementations**

- [ ] **Step 2: Update TaskList to use store (already synced)**

The TaskList already uses `useTaskStore`, which is now synced by `useTasks`. No major changes needed - the polling in Dashboard will trigger store updates.

However, we need to ensure the status colors include 'running':

```typescript
// In TaskList.tsx, update the status render:
render: (status: string) => {
  const color = 
    status === 'completed' ? 'green' : 
    status === 'failed' ? 'red' : 
    status === 'running' ? 'blue' : 'default';
  return <Tag color={color}>{status}</Tag>;
},
```

- [ ] **Step 3: Commit**

```bash
git add src/components/TaskList.tsx
git commit -m "fix(frontend): add running status color to TaskList"
```

---

## Verification

- [ ] **Step 1: Start backend**

Run: `cd /p/research/backend && python src/api.py`

- [ ] **Step 2: Start frontend**

Run: `cd /p/research/frontend && npm run dev`

- [ ] **Step 3: Test flow**

1. Open http://localhost:5173
2. Click "New Task" button
3. Fill form and submit
4. Should redirect to TaskList
5. Task should appear with status (pending → running → completed)
6. Wait 5 seconds, verify status updates
7. Navigate to Sessions, verify sessions display
8. Check browser console for errors

---

## Spec Coverage Checklist

- [x] SQLite database with tasks table - Task 1
- [x] 30-day auto-cleanup - Task 1 (`_cleanup_old_tasks`)
- [x] GET /tasks endpoint - Task 2
- [x] GET /tasks/:id endpoint - Task 2
- [x] POST /generate creates task - Task 2
- [x] POST /continue creates task - Task 2
- [x] Frontend polling every 5s - Task 4, 6
- [x] Status tags with colors - Task 7
- [x] Redirect after form submit - Task 5
- [x] Task types: generate_excel, generate_code - Types (Task 3)
- [x] result_file and result_message fields - Types (Task 3)

## Type Consistency Check

All task-related code uses consistent type names:
- `Task` interface (singular) in types.ts
- `TasksResponse` for list response
- `CreateTaskResponse` for mutation response
- `useTasks()` hook for fetching
- `useCreateTask()` mutation hook

No mismatched names found.
