# Frontend 多语言支持实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为前端添加 react-i18next 多语言支持，支持中文/英文切换

**Architecture:** 使用 react-i18next 实现国际化，在 Header 添加语言切换按钮

**Tech Stack:** react-i18next, i18next, Ant Design

---

## Task 1: 安装 i18n 依赖

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: 安装依赖**

Run: `cd frontend && npm install react-i18next i18next`

---

## Task 2: 创建翻译文件

**Files:**
- Create: `frontend/src/locales/zh.json`
- Create: `frontend/src/locales/en.json`

- [ ] **Step 1: 创建 zh.json**

```json
{
  "header": {
    "title": "UI 测试生成器"
  },
  "nav": {
    "dashboard": "仪表盘",
    "sessions": "会话"
  },
  "task": {
    "name": "名称",
    "url": "URL",
    "description": "描述",
    "status": "状态",
    "created": "创建时间",
    "action": "操作"
  },
  "status": {
    "pending": "等待中",
    "running": "运行中",
    "completed": "已完成",
    "failed": "失败"
  },
  "action": {
    "download": "下载",
    "upload": "上传Excel",
    "generate": "生成代码",
    "remove": "删除"
  },
  "button": {
    "newTask": "新建任务",
    "uploadExcel": "上传Excel"
  },
  "form": {
    "url": "URL",
    "filepath": "保存路径",
    "username": "用户名",
    "password": "密码",
    "description": "描述"
  },
  "message": {
    "uploadSuccess": "文件上传成功，正在生成代码...",
    "uploadFailed": "上传失败",
    "generateSuccess": "正在生成代码...",
    "generateFailed": "生成失败",
    "taskCreated": "任务创建成功"
  }
}
```

- [ ] **Step 2: 创建 en.json**

```json
{
  "header": {
    "title": "UI Test Generator"
  },
  "nav": {
    "dashboard": "Dashboard",
    "sessions": "Sessions"
  },
  "task": {
    "name": "Name",
    "url": "URL",
    "description": "Description",
    "status": "Status",
    "created": "Created",
    "action": "Action"
  },
  "status": {
    "pending": "Pending",
    "running": "Running",
    "completed": "Completed",
    "failed": "Failed"
  },
  "action": {
    "download": "Download",
    "upload": "Upload Excel",
    "generate": "Generate Code",
    "remove": "Remove"
  },
  "button": {
    "newTask": "New Task",
    "uploadExcel": "Upload Excel"
  },
  "form": {
    "url": "URL",
    "filepath": "Save Path",
    "username": "Username",
    "password": "Password",
    "description": "Description"
  },
  "message": {
    "uploadSuccess": "File uploaded, generating code...",
    "uploadFailed": "Upload failed",
    "generateSuccess": "Generating code...",
    "generateFailed": "Generate failed",
    "taskCreated": "Task created successfully"
  }
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/locales/zh.json frontend/src/locales/en.json
git commit -m "feat: add zh and en translation files"
```

---

## Task 3: 创建 i18n 配置文件

**Files:**
- Create: `frontend/src/i18n.ts`

- [ ] **Step 1: 创建 i18n.ts**

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zh from './locales/zh.json';
import en from './locales/en.json';

i18n.use(initReactI18next).init({
  resources: {
    zh: { translation: zh },
    en: { translation: en },
  },
  lng: 'zh',
  fallbackLng: 'zh',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/i18n.ts
git commit -m "feat: add i18n configuration"
```

---

## Task 4: 在 main.tsx 引入 i18n

**Files:**
- Modify: `frontend/src/main.tsx`

- [ ] **Step 1: 查看当前 main.tsx**

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 2: 添加 i18n 引入**

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import './i18n';  // 添加这行

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/main.tsx
git commit -m "feat: import i18n in main.tsx"
```

---

## Task 5: 在 Header 添加语言切换

**Files:**
- Modify: `frontend/src/App.tsx`

- [ ] **Step 1: 查看当前 App.tsx**

```tsx
import { Layout, Menu } from 'antd';
import { Dashboard, Sessions } from './pages';

function App() {
  return (
    <Layout>
      <Layout.Header>UI Test Generator</Layout.Header>
      <Layout.Content>
        <Dashboard />
      </Layout.Content>
    </Layout>
  );
}
```

- [ ] **Step 2: 添加语言切换按钮**

```tsx
import { Layout, Menu, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { Dashboard, Sessions } from './pages';

function App() {
  const { t, i18n } = useTranslation();

  return (
    <Layout>
      <Layout.Header>
        <span>{t('header.title')}</span>
        <Select
          value={i18n.language}
          onChange={(lng) => i18n.changeLanguage(lng)}
          style={{ width: 80, float: 'right' }}
        >
          <Select.Option value="zh">中文</Select.Option>
          <Select.Option value="en">EN</Select.Option>
        </Select>
      </Layout.Header>
      <Layout.Content>
        <Dashboard />
      </Layout.Content>
    </Layout>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat: add language switcher to Header"
```

---

## Task 6: 在 TaskList 中使用 i18n

**Files:**
- Modify: `frontend/src/components/TaskList.tsx`

- [ ] **Step 1: 添加 useTranslation**

```tsx
import { useTranslation } from 'react-i18next';
```

- [ ] **Step 2: 使用 t() 替换文本**

在 TaskList 中：
- `columns` 标题：title: t('task.name') 等
- `actionItems` label：label: t('action.download') 等
- message：message.success(t('message.uploadSuccess')) 等
- Button text：{t('action.upload')} 等

---

## 自检清单

1. **Spec 覆盖**：
   - [x] 安装依赖
   - [x] 创建翻译文件
   - [x] i18n 配置
   - [x] Header 语言切换
   - [x] TaskList 使用 i18n

2. **类型一致性**：MenuProps['items'] 中的 label 都是 string 类型（t() 返回 string）

3. **无占位符**：所有翻译 key 都是完整的
