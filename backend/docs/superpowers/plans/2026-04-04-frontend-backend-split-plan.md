# Frontend-Backend Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `ui_test` 项目拆分为前后端分离架构 - 后端迁移到 `backend/`，前端新建 React 项目

**Architecture:** 并行结构 - `backend/` 和 `frontend/` 平级，前端通过 HTTP 调用后端 API

**Tech Stack:**
- Frontend: React + Vite + TypeScript + Shadcn/ui + Tailwind CSS + Zustand + React Query
- Backend: FastAPI + OpenCode + Playwright

---

## Phase 1: Backend Migration

### Task 1: 创建 backend 目录结构

**Files:**
- Create: `backend/` (directory)
- Modify: N/A

- [ ] **Step 1: 创建 backend 目录**

```bash
cd P:/research/ui_test
mkdir -p backend
```

### Task 2: 移动文件到 backend/

**Files:**
- Create: `backend/src/`, `backend/templates/`, `backend/tests/`, `backend/pages/`, `backend/test_cases/`, `backend/sessions/`, `backend/docs/`
- Move: All contents from `ui_test/` root to `backend/`

- [ ] **Step 1: 移动所有文件到 backend/**

```bash
cd P:/research/ui_test
# 移动所有文件和目录（除了 backend 和 frontend）
mv src templates tests pages test_cases sessions docs requirements.txt pytest.ini conftest.py opencode.json AGENTS.md CLAUDE.md backend/
# 移动根目录的配置文件
mv *.md *.json backend/ 2>/dev/null || true
```

### Task 3: 验证后端 FastAPI 启动

**Files:**
- Test: `backend/src/api.py`

- [ ] **Step 1: 启动 FastAPI 验证**

```bash
cd P:/research/ui_test/backend
python -m uvicorn src.api:app --host 0.0.0.0 --port 8000
```

Expected: "Application startup complete" message

- [ ] **Step 2: 测试 health 端点**

```bash
curl http://localhost:8000/health
```

Expected: `{"status":"ok"}`

### Task 4: 更新 backend 内部路径引用

**Files:**
- Modify: `backend/src/generator.py:16` (OPENCODE_CMD)
- Modify: `backend/src/generator.py:17` (PROJECT_DIR)
- Modify: `backend/src/sessions.py:7-8` (PROJECT_DIR, SESSIONS_FILE)
- Modify: `backend/src/api.py:10` (sys.path)

- [ ] **Step 1: 检查并更新 OPENCODE_CMD 路径**

`P:\\nodejs\\opencode.cmd` - 这个路径可能需要保持不变

- [ ] **Step 2: 检查 PROJECT_DIR 计算逻辑**

```python
# 确认 PROJECT_DIR = backend/ 的父目录 = research/
# 当前: os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 这应该是正确的，因为它从 src/ 向上两层
```

- [ ] **Step 3: 验证 sessions.py 路径**

```python
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# backend/src/sessions.py -> backend/ -> research/
SESSIONS_FILE = os.path.join(PROJECT_DIR, "sessions", "session.json")
# 应该是: research/sessions/session.json
```

### Task 5: 更新根目录 CLAUDE.md

**Files:**
- Modify: `backend/CLAUDE.md`

- [ ] **Step 1: 更新 CLAUDE.md 中的路径引用**

将所有 `src/` 引用改为 `backend/src/`
将 `test_cases/` 改为 `backend/test_cases/`
将 `sessions/` 改为 `backend/sessions/`

### Task 6: 创建 frontend 目录（占位）

**Files:**
- Create: `frontend/` (empty directory for now)

- [ ] **Step 1: 创建 frontend 目录**

```bash
mkdir frontend
```

---

## Phase 2: Frontend Creation

### Task 7: Vite 创建 React + TypeScript 项目

**Files:**
- Create: `frontend/` (Vite project structure)
- Modify: N/A

- [ ] **Step 1: 使用 Vite 创建项目**

```bash
cd P:/research
npm create vite@latest frontend -- --template react-ts
```

- [ ] **Step 2: 安装依赖**

```bash
cd frontend
npm install
```

### Task 8: 安装 Tailwind CSS

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/tailwind.config.js`, `frontend/postcss.config.js`
- Modify: `frontend/src/index.css`

- [ ] **Step 1: 安装 Tailwind CSS**

```bash
cd frontend
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

- [ ] **Step 2: 配置 tailwind.config.js**

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

- [ ] **Step 3: 更新 src/index.css**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Task 9: 安装 Shadcn/ui

**Files:**
- Create: `frontend/components/ui/` (shadcn components)
- Modify: `frontend/components.json`, `frontend/package.json`, `frontend/tailwind.config.js`

- [ ] **Step 1: 初始化 Shadcn/ui**

```bash
cd frontend
npx shadcn@latest init
```

选择默认值:
- Style: Default
- Base Color: Slate
- CSS file: src/index.css
- CSS variables: yes

- [ ] **Step 2: 安装常用组件**

```bash
cd frontend
npx shadcn@latest add button card input label textarea table badge toast
```

### Task 10: 安装状态管理和 API 调用库

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: 安装 Zustand 和 React Query**

```bash
cd frontend
npm install zustand @tanstack/react-query axios
```

### Task 11: 创建 API 服务层

**Files:**
- Create: `frontend/src/services/api.ts`
- Create: `frontend/src/services/types.ts`

- [ ] **Step 1: 创建 API 类型定义**

```typescript
// frontend/src/services/types.ts
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

- [ ] **Step 2: 创建 API 服务**

```typescript
// frontend/src/services/api.ts
import axios from 'axios';
import type { GenerateRequest, ContinueRequest, GenerateResponse, SessionsResponse } from './types';

const API_BASE = 'http://localhost:8000';

export const api = {
  generate: async (data: GenerateRequest): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE}/generate`, data);
    return response.data;
  },

  continueSession: async (data: ContinueRequest): Promise<GenerateResponse> => {
    const response = await axios.post(`${API_BASE}/continue`, data);
    return response.data;
  },

  getSessions: async (): Promise<SessionsResponse> => {
    const response = await axios.get(`${API_BASE}/sessions`);
    return response.data;
  },

  health: async (): Promise<{ status: string }> => {
    const response = await axios.get(`${API_BASE}/health`);
    return response.data;
  },
};
```

### Task 12: 创建 Zustand Store

**Files:**
- Create: `frontend/src/stores/taskStore.ts`

- [ ] **Step 1: 创建任务状态 Store**

```typescript
// frontend/src/stores/taskStore.ts
import { create } from 'zustand';

export interface Task {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  result?: string;
}

interface TaskStore {
  tasks: Task[];
  addTask: (task: Omit<Task, 'id' | 'createdAt'>) => string;
  updateTask: (id: string, updates: Partial<Task>) => void;
  removeTask: (id: string) => void;
  clearTasks: () => void;
}

export const useTaskStore = create<TaskStore>((set) => ({
  tasks: [],

  addTask: (task) => {
    const id = `task-${Date.now()}`;
    const newTask: Task = {
      ...task,
      id,
      createdAt: new Date().toISOString(),
    };
    set((state) => ({ tasks: [...state.tasks, newTask] }));
    return id;
  },

  updateTask: (id, updates) => {
    set((state) => ({
      tasks: state.tasks.map((t) => (t.id === id ? { ...t, ...updates } : t)),
    }));
  },

  removeTask: (id) => {
    set((state) => ({
      tasks: state.tasks.filter((t) => t.id !== id),
    }));
  },

  clearTasks: () => {
    set({ tasks: [] });
  },
}));
```

### Task 13: 创建 Dashboard 页面组件

**Files:**
- Create: `frontend/src/pages/Dashboard.tsx`
- Create: `frontend/src/components/TaskList.tsx`
- Create: `frontend/src/components/NewTaskForm.tsx`
- Create: `frontend/src/components/UploadExcel.tsx`

- [ ] **Step 1: 创建 Dashboard 主页面**

```tsx
// frontend/src/pages/Dashboard.tsx
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';
import { UploadExcel } from '@/components/UploadExcel';

export function Dashboard() {
  const [showNewTask, setShowNewTask] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  return (
    <div className="container mx-auto py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold">UI Test Generator</h1>
          <p className="text-muted-foreground">Generate test cases with OpenCode</p>
        </div>
        <div className="flex gap-4">
          <Button variant="outline" onClick={() => setShowUpload(!showUpload)}>
            Upload Excel
          </Button>
          <Button onClick={() => setShowNewTask(!showNewTask)}>
            New Task
          </Button>
        </div>
      </div>

      {showNewTask && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>New Task</CardTitle>
            <CardDescription>Generate Excel test cases from a website</CardDescription>
          </CardHeader>
          <CardContent>
            <NewTaskForm onClose={() => setShowNewTask(false)} />
          </CardContent>
        </Card>
      )}

      {showUpload && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Continue Session</CardTitle>
            <CardDescription>Upload Excel to continue generating test code</CardDescription>
          </CardHeader>
          <CardContent>
            <UploadExcel onClose={() => setShowUpload(false)} />
          </CardContent>
        </Card>
      )}

      <TaskList />
    </div>
  );
}
```

- [ ] **Step 2: 创建 TaskList 组件**

```tsx
// frontend/src/components/TaskList.tsx
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export function TaskList() {
  const { tasks, removeTask } = useTaskStore();

  if (tasks.length === 0) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-muted-foreground">
          No tasks yet. Create a new task to get started.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {tasks.map((task) => (
        <Card key={task.id}>
          <CardHeader className="pb-2">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-lg">{task.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{task.url}</p>
              </div>
              <Badge
                variant={
                  task.status === 'completed'
                    ? 'default'
                    : task.status === 'failed'
                    ? 'destructive'
                    : 'secondary'
                }
              >
                {task.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-sm mb-4">{task.description}</p>
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground">
                Created: {new Date(task.createdAt).toLocaleString()}
              </span>
              <div className="flex gap-2">
                {task.status === 'completed' && (
                  <Button size="sm" variant="outline">
                    Download
                  </Button>
                )}
                <Button size="sm" variant="ghost" onClick={() => removeTask(task.id)}>
                  Remove
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
```

- [ ] **Step 3: 创建 NewTaskForm 组件**

```tsx
// frontend/src/components/NewTaskForm.tsx
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface NewTaskFormProps {
  onClose: () => void;
}

export function NewTaskForm({ onClose }: NewTaskFormProps) {
  const [url, setUrl] = useState('');
  const [filepath, setFilepath] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [description, setDescription] = useState('');

  const { addTask, updateTask } = useTaskStore();

  const mutation = useMutation({
    mutationFn: api.generate,
    onSuccess: (data, variables) => {
      const taskId = addTask({
        name: variables.filepath,
        url: variables.url,
        description: variables.description,
        status: 'completed',
        result: data.message,
      });
      onClose();
    },
    onError: (error) => {
      console.error('Generation failed:', error);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({
      url,
      filepath: filepath || `test_cases/${Date.now()}.xlsx`,
      username,
      password,
      description,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="url">URL *</Label>
        <Input
          id="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com"
          required
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="filepath">Save Path</Label>
        <Input
          id="filepath"
          value={filepath}
          onChange={(e) => setFilepath(e.target.value)}
          placeholder="test_cases/my_test.xlsx"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="username">Username</Label>
          <Input
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">Description *</Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Describe what you want to test..."
          required
        />
      </div>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? 'Generating...' : 'Generate'}
        </Button>
      </div>
    </form>
  );
}
```

- [ ] **Step 4: 创建 UploadExcel 组件**

```tsx
// frontend/src/components/UploadExcel.tsx
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { api } from '@/services/api';
import { useTaskStore } from '@/stores/taskStore';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface UploadExcelProps {
  onClose: () => void;
}

export function UploadExcel({ onClose }: UploadExcelProps) {
  const [file, setFile] = useState<File | null>(null);
  const { addTask } = useTaskStore();

  const mutation = useMutation({
    mutationFn: api.continueSession,
    onSuccess: (data) => {
      console.log('Session continued:', data);
      onClose();
    },
    onError: (error) => {
      console.error('Upload failed:', error);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    // In a real app, you would upload the file to backend
    // For now, we'll just pass the filename
    const filepath = `test_cases/${file.name}`;

    addTask({
      name: file.name,
      url: '',
      description: 'Continue session from Excel',
      status: 'running',
    });

    mutation.mutate({ excel_file: filepath });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="file">Excel File</Label>
        <input
          id="file"
          type="file"
          accept=".xlsx"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm border rounded p-2"
        />
      </div>

      <div className="flex justify-end gap-4">
        <Button type="button" variant="outline" onClick={onClose}>
          Cancel
        </Button>
        <Button type="submit" disabled={!file || mutation.isPending}>
          {mutation.isPending ? 'Processing...' : 'Upload & Continue'}
        </Button>
      </div>
    </form>
  );
}
```

### Task 14: 配置 React Query Provider

**Files:**
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: 配置 React Query**

```tsx
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

### Task 15: 更新 App.tsx

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 更新 App.tsx**

```tsx
// frontend/src/App.tsx
import { Dashboard } from './pages/Dashboard';

function App() {
  return <Dashboard />;
}

export default App;
```

---

## Phase 3: CORS Configuration (After Frontend is Ready)

### Task 16: 配置后端 CORS

**Files:**
- Modify: `backend/src/api.py`

- [ ] **Step 1: 添加 CORS 中间件**

```python
# 在 backend/src/api.py 的 app = FastAPI() 后添加
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Task 17: 配置前端代理（开发环境）

**Files:**
- Modify: `frontend/vite.config.ts`

- [ ] **Step 1: 配置 Vite 代理**

```typescript
// frontend/vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
});
```

---

## Verification Checklist

- [ ] FastAPI 启动正常: `cd backend && ./venv/Scripts/python -m uvicorn src.api:app --port 8000`
- [ ] Health 端点可用: `curl http://localhost:8000/health`
- [ ] Sessions 端点可用: `curl http://localhost:8000/sessions`
- [ ] Frontend 启动正常: `cd frontend && npm run dev`
- [ ] Frontend 页面可访问: http://localhost:5173
- [ ] API 调用成功（跨域）: 从前端调用后端 API

---

## Files Summary

| File | Action |
|------|--------|
| `frontend/` | Create (Vite init) |
| `frontend/src/services/api.ts` | Create |
| `frontend/src/services/types.ts` | Create |
| `frontend/src/stores/taskStore.ts` | Create |
| `frontend/src/pages/Dashboard.tsx` | Create |
| `frontend/src/components/TaskList.tsx` | Create |
| `frontend/src/components/NewTaskForm.tsx` | Create |
| `frontend/src/components/UploadExcel.tsx` | Create |
| `frontend/src/App.tsx` | Modify |
| `frontend/src/main.tsx` | Modify |
| `frontend/vite.config.ts` | Modify |
| `backend/src/api.py` | Modify (add CORS) |
| `backend/CLAUDE.md` | Modify (update paths) |
