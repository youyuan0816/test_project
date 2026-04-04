# UI Test Project Frontend-Backend Split Design

## Overview

将现有的 `ui_test` Python 项目拆分为前后端分离架构，前端使用 React + Shadcn/ui，后端保持 FastAPI。

## Project Structure

```
research/
├── backend/                    # 原 ui_test/ 重命名
│   ├── src/                   # FastAPI 应用
│   ├── templates/             # OpenCode 模板
│   ├── tests/                 # pytest 测试
│   ├── pages/                 # Page Object
│   ├── test_cases/            # 生成的 Excel 测试用例
│   ├── sessions/              # Session 存储
│   ├── requirements.txt
│   ├── main.py
│   └── api.py
│
├── frontend/                   # 新建 React 项目
│   ├── src/
│   │   ├── components/         # React 组件
│   │   ├── pages/              # 页面
│   │   ├── hooks/             # 自定义 Hooks
│   │   ├── services/           # API 调用
│   │   ├── stores/            # Zustand 状态
│   │   └── lib/               # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── docs/                      # 保留在根目录
├── README.md
└── CLAUDE.md
```

## Implementation Phases

### Phase 1: Backend Migration (User Choice: B - 后端优先)

1. 创建 `backend/` 目录
2. 移动所有内容到 `backend/`
3. 验证 FastAPI 正常启动 (`python -m uvicorn backend.src.api:app`)
4. 验证 OpenCode session 功能正常
5. 更新 `CLAUDE.md` 路径引用

### Phase 2: Frontend Creation

1. Vite 创建 React + TypeScript 项目
2. 安装 Tailwind CSS + Shadcn/ui
3. 配置 API 服务层（指向 `localhost:8000`）
4. 开发 Dashboard 页面
5. 配置 CORS（最后）

## Frontend Core Features

| Feature | Description |
|---------|-------------|
| 任务列表 | 展示历史生成任务 |
| 新建任务 | 输入 URL、描述、账号密码 |
| 上传 Excel | 继续之前的任务 |
| 查看进度 | 轮询 API 状态 |
| 下载结果 | 下载生成的脚本文件 |

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend Framework | React + Vite + TypeScript |
| UI Library | Shadcn/ui + Tailwind CSS |
| State Management | Zustand |
| API Calls | React Query |
| Backend | FastAPI + OpenCode |
| Communication | REST API |

## API Endpoints (Existing)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/generate` | POST | 生成 Excel 测试用例 |
| `/continue` | POST | 继续 session，生成测试代码 |
| `/sessions` | GET | 获取所有保存的 session |
| `/health` | GET | 健康检查 |

## Design Decisions

1. **Parallel Structure**: 前后端平级，通过 HTTP 通信
2. **No Authentication**: 当前版本作为内部工具，无需登录
3. **CORS Later**: 后端迁移完成后配置 CORS
4. **Vite**: React 项目使用 Vite 初始化
5. **Shadcn/ui**: 使用现代化的 UI 组件库
6. **Dashboard**: 主要界面为仪表盘式，展示任务列表

## Notes

- 后端移动后，OpenCode 命令路径需更新
- 前端 API 地址先写死 `localhost:8000`，后续可通过环境变量配置
- Session 存储在 backend/sessions/session.json
