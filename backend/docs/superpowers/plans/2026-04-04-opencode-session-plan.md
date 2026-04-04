# OpenCode Session 持久化实现计划

**目标：** 保存 OpenCode session 以支持后续在同一上下文中继续操作（读取 Excel 生成测试代码）

**架构：** 使用 `opencode run --session <name>` 创建命名 session，通过 JSON 文件持久化 session 映射

**技术栈：** Python, subprocess, JSON, openpyxl

---

## 文件结构

```
ui_test/
├── main.py                    # CLI 入口，支持 --generate 和 --continue
├── sessions/
│   └── session.json           # session ID 映射
├── test_cases/                # Excel 文件目录
│   └── *.xlsx
└── tests/                    # 测试代码输出目录
```

---

### Task 1: 创建 sessions 目录和 session.json 初始化

**Files:**
- Create: `sessions/session.json`

- [ ] **Step 1: 创建 sessions 目录和初始化文件**

```bash
mkdir -p sessions
echo "{}" > sessions/session.json
```

- [ ] **Step 2: 验证文件创建**

```bash
cat sessions/session.json
# 预期输出: {}
```

---

### Task 2: 创建 main.py CLI 框架

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 编写 CLI 参数解析框架**

```python
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='OpenCode Session Manager')
    parser.add_argument('--generate', action='store_true', help='生成 Excel 测试用例')
    parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE',
                        help='继续 session，读取 Excel 生成测试代码')
    args = parser.parse_args()

    if args.generate:
        from generator import generate_excel
        generate_excel()
    elif args.continue_file:
        from generator import continue_session
        continue_session(args.continue_file)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试 CLI 帮助**

```bash
python main.py --help
# 预期输出: 显示 --generate 和 --continue 帮助信息
```

---

### Task 3: 创建 sessions 管理模块

**Files:**
- Create: `sessions.py`

- [ ] **Step 1: 编写 session 管理函数**

```python
import json
import os
from datetime import datetime

SESSIONS_FILE = "sessions/session.json"

def load_sessions():
    """加载 session 映射"""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions(sessions):
    """保存 session 映射"""
    os.makedirs("sessions", exist_ok=True)
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

def get_session_id(excel_path):
    """获取 Excel 对应的 session ID"""
    sessions = load_sessions()
    entry = sessions.get(excel_path)
    return entry["session_id"] if entry else None

def save_session_id(excel_path, session_id):
    """保存 session ID"""
    sessions = load_sessions()
    sessions[excel_path] = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat()
    }
    save_sessions(sessions)
```

- [ ] **Step 2: 测试 session 保存和读取**

```python
# 在 Python 中测试
from sessions import save_session_id, get_session_id
save_session_id("test.xlsx", "abc123")
assert get_session_id("test.xlsx") == "abc123"
```

---

### Task 4: 实现 --generate 模式

**Files:**
- Create: `generator.py`

- [ ] **Step 1: 编写 generate_excel 函数**

```python
import subprocess
import os
from sessions import save_session_id

OPENCODE_CMD = "P:\\nodejs\\opencode.cmd"
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_excel():
    """交互式生成 Excel 测试用例"""
    url = input("UI 地址: ").strip()
    if not url:
        print("UI 地址不能为空")
        return

    filepath = input("保存路径: ").strip()
    username = input("登录账号（可选）: ").strip()
    password = input("登录密码（可选）: ").strip()
    description = input("测试描述: ").strip()

    login_info = f"登录账号：{username}，密码：{password}" if username else "无需登录"

    # 生成唯一 session name
    session_name = f"excel_{os.path.basename(filepath).replace('.xlsx', '')}"

    prompt = f"""请为以下网站生成 Excel 测试用例：
网站：{url}
{login_info}
测试需求：{description}
保存路径：{filepath}

Excel 格式：用例编号、名称、模块、优先级、预置条件、步骤、预期结果
使用 openpyxl 生成，保存到 {filepath}"""

    print(f"[INFO] 正在执行 OpenCode，session: {session_name}...")

    # 调用 opencode run 并捕获 session ID
    cmd = f'{OPENCODE_CMD} run --session {session_name} "{prompt}"'
    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        timeout=120,
        shell=True
    )

    print(result.stdout.decode('utf-8', errors='replace')[:2000] if result.stdout else "")

    # 保存 session ID
    save_session_id(filepath, session_name)
    print(f"[INFO] Session 已保存: {session_name}")
```

- [ ] **Step 2: 测试 --generate 模式**

```bash
cd P:/research/ui_test
python main.py --generate
# 输入: https://www.baidu.com, test_cases/demo.xlsx, , , 测试搜索
# 预期: 生成 Excel，保存 session
```

---

### Task 5: 实现 --continue 模式

**Files:**
- Modify: `generator.py` - 添加 continue_session 函数

- [ ] **Step 1: 编写 continue_session 函数**

```python
def continue_session(excel_file):
    """继续 session，读取 Excel 生成测试代码"""
    session_id = get_session_id(excel_file)
    if not session_id:
        print(f"错误：未找到 {excel_file} 对应的 session")
        print("请先使用 --generate 生成 Excel")
        return

    # 读取 Excel 内容
    from openpyxl import load_workbook
    wb = load_workbook(excel_file)
    ws = wb.active

    # 构建摘要
    rows = list(ws.iter_rows(values_only=True))
    headers = rows[0] if rows else []
    test_cases = rows[1:] if len(rows) > 1 else []

    test_summary = "\n".join([f"- {tc[0]}: {tc[1]}" for tc in test_cases[:10]])

    prompt = f"""请读取 Excel 文件 {excel_file} 中的测试用例，为其生成 pytest 测试代码。

测试用例摘要：
{test_summary}

请生成：
1. Page Object 类（封装页面元素和操作）
2. pytest 测试用例

输出到 tests/ 目录，文件名格式：test_{{module}}.py"""

    print(f"[INFO] 继续 session: {session_id}...")

    cmd = f'{OPENCODE_CMD} run --continue -s {session_id} "{prompt}"'
    result = subprocess.run(
        cmd,
        cwd=PROJECT_DIR,
        capture_output=True,
        timeout=120,
        shell=True
    )

    print(result.stdout.decode('utf-8', errors='replace')[:2000] if result.stdout else "")

    # 更新 last_used
    sessions = load_sessions()
    if excel_file in sessions:
        sessions[excel_file]["last_used"] = datetime.now().isoformat()
        save_sessions(sessions)
```

- [ ] **Step 2: 测试 --continue 模式**

```bash
cd P:/research/ui_test
python main.py --continue test_cases/demo.xlsx
# 预期: 读取 Excel，继续 session，生成测试代码
```

---

### Task 6: 更新 CLI 入口整合所有功能

**Files:**
- Modify: `main.py` - 整合 generator.py

- [ ] **Step 1: 更新 main.py 整合所有功能**

```python
import argparse
import sys
import os

def main():
    parser = argparse.ArgumentParser(description='OpenCode Session Manager')
    parser.add_argument('--generate', action='store_true', help='生成 Excel 测试用例')
    parser.add_argument('--continue', dest='continue_file', metavar='EXCEL_FILE',
                        help='继续 session，读取 Excel 生成测试代码')
    args = parser.parse_args()

    if args.generate:
        from generator import generate_excel
        generate_excel()
    elif args.continue_file:
        from generator import continue_session
        continue_session(args.continue_file)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 测试完整流程**

```bash
# 1. 生成 Excel
python main.py --generate
# 输入: https://www.baidu.com, test_cases/session_test.xlsx, , , 搜索测试

# 2. 继续生成代码
python main.py --continue test_cases/session_test.xlsx
```

---

### Task 7: 更新 CLAUDE.md 文档

**Files:**
- Modify: `CLAUDE.md` - 添加新功能说明

- [ ] **Step 1: 添加 session 功能说明**

```markdown
## OpenCode Session 持久化
```bash
# 生成 Excel 并保存 session
python main.py --generate
# 输入: URL, 保存路径, 账号密码(可选), 测试描述

# 继续 session，读取 Excel 生成测试代码
python main.py --continue test_cases/demo.xlsx
```
```

- [ ] **Step 2: 验证文档更新**

```bash
cat CLAUDE.md | grep -A 10 "OpenCode Session"
```

---

### Task 8: 验证完整流程

**Files:**
- 测试所有命令

- [ ] **Step 1: 完整流程测试**

```bash
# 清理
rm -rf sessions/test_session.xlsx tests/test_*.py

# 生成 Excel
echo -e "https://www.baidu.com\ntest_cases/session_test.xlsx\n\n\n百度搜索" | python main.py --generate

# 验证 session 保存
cat sessions/session.json

# 继续生成代码
python main.py --continue test_cases/session_test.xlsx

# 验证测试代码生成
ls tests/
```

---

## 验证清单

- [ ] `sessions/session.json` 文件存在且格式正确
- [ ] `python main.py --generate` 生成 Excel 文件
- [ ] `python main.py --continue <file>` 继续 session 并生成测试代码
- [ ] `CLAUDE.md` 更新了文档
