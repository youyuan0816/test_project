# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述
Python UI 自动化测试项目，使用 Playwright 进行 Web 应用测试。

## 常用命令

### 安装依赖
```bash
pip install -r requirements.txt
playwright install chromium
```

### 运行测试
```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/test_example.py

# 运行单个测试
pytest tests/test_example.py::test_example -v

# 带 GUI 浏览器运行（调试模式）
pytest --headed
```

## 技术栈
- **Playwright**: 浏览器自动化
- **pytest**: 测试框架
- **pytest-playwright**: Pytest 集成

## 项目结构
```
backend/                    # 后端根目录
├── src/
│   ├── main.py           # CLI 入口
│   ├── generator.py      # OpenCode 调用逻辑
│   ├── api.py           # FastAPI 服务
│   └── sessions.py       # Session 管理
├── templates/            # OpenCode 生成脚本模板
│   └── generate_test_cases.py
├── tests/               # pytest 测试用例目录
├── pages/               # Page Object 模型目录
├── sessions/             # Session 存储
│   └── session.json
└── test_cases/          # Excel 测试用例
```

## OpenCode 集成
通过 OpenCode 生成 Excel 测试用例：

```bash
# 生成 Excel 测试用例
python src/main.py --generate
# 输入: URL, 保存路径, 账号密码(可选), 测试描述

# 人工审核 Excel...

# 根据 Excel 生成测试代码（需要指定 Excel 文件）
python src/main.py --continue test_cases/demo.xlsx
```

### API 服务
使用 FastAPI 提供 REST API：

```bash
# 启动 API 服务
cd backend
python src/api.py
# 或
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

**API 端点：**
- `POST /generate` - 生成 Excel 测试用例
  - Body: `{"url": "https://xxx.com", "filepath": "test_cases/xxx.xlsx", "username": "", "password": "", "description": "测试描述"}`
- `POST /continue` - 读取 Excel 生成测试代码
  - Body: `{"excel_file": "test_cases/xxx.xlsx"}`
- `GET /health` - 健康检查

**目录：**
- `src/` - Python 源代码
- `templates/` - OpenCode 生成脚本模板
- `test_cases/` - Excel 测试用例
- `tests/` - pytest 测试代码
