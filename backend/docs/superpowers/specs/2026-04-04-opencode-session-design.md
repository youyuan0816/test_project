# Design: OpenCode Session 持久化

## Context
需要保存 OpenCode run 的 session，以便后续在同一个 session 中继续操作（读取 Excel 生成测试代码）。

## 流程设计

### 流程图
```
┌─────────────────────────────────────────────────────────────┐
│  python main.py --generate                                   │
│  输入: URL, filepath, credentials, description              │
│  输出: Excel 文件 + session 保存到 sessions/session.json      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  python main.py --continue <excel_file>                      │
│  输入: Excel 文件名                                          │
│  输出: 读取 session，继续执行 → 生成测试代码                  │
└─────────────────────────────────────────────────────────────┘
```

## 数据结构

### sessions/session.json
```json
{
  "test_cases/baidu_search.xlsx": {
    "session_id": "abc123",
    "created_at": "2026-04-04T10:00:00",
    "last_used": "2026-04-04T10:30:00"
  }
}
```

## CLI 设计

### --generate 模式
```bash
python main.py --generate
# 交互式输入：URL, filepath, credentials, description
# 生成 Excel，保存 session
```

### --continue 模式
```bash
python main.py --continue test_cases/baidu_search.xlsx
# 从 session.json 读取 session ID
# 继续 session：读取 Excel，生成测试代码
```

## 依赖
- `opencode run --session <name>` - 创建/继续 session
- `opencode run --continue -s <session_id>` - 继续指定 session

## 目录结构
```
ui_test/
├── main.py
├── sessions/
│   └── session.json    # session 映射
└── test_cases/
    └── baidu_search.xlsx
```
