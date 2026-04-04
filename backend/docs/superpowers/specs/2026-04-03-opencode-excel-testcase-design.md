# Design: OpenCode 生成 Excel 测试用例

## Context
测试人员输入测试需求描述，OpenCode 分析后生成 Excel 测试用例供人工审核。

## 流程设计
```
用户输入描述 → main.py → OpenCode API
                              ↓
                     OpenCode 生成 Python 代码
                              ↓
                     OpenCode 执行代码
                              ↓
                     Excel 文件生成 → 人工审核
```

## Excel 格式
| 列名 | 说明 |
|------|------|
| 用例编号 | 唯一标识，如 TC-001 |
| 用例名称 | 测试用例名称 |
| 模块/功能 | 所属模块 |
| 优先级 | P0/P1/P2/P3 |
| 预置条件 | 测试前准备 |
| 测试步骤 | 具体操作步骤 |
| 预期结果 | 期望的输出/行为 |

## main.py 修改

### 输入（交互式提示）
1. UI 地址：如 https://www.baidu.com
2. 文件保存路径：如 test_cases/baidu_search.xlsx
3. 登录账号（可选）：如 admin
4. 登录密码（可选）：如 password123
5. 测试描述：如 搜索功能测试

### 处理
1. 引导用户依次输入各字段
2. 构造 prompt 发送给 OpenCode
3. 等待执行完成

### Prompt 模板
```
分析以下需求，生成 Excel 测试用例，保存到指定路径。

目标网站：{url}
保存路径：{filepath}
登录账号：{username}（如需登录）
登录密码：{password}（如需登录）
需求描述：{description}

Excel 格式要求：
- 用例编号：用 TC-序号 格式
- 用例名称：简洁明确
- 模块/功能：所属功能模块
- 优先级：P0/P1/P2/P3
- 预置条件：测试前需要满足的条件
- 测试步骤：详细的操作步骤
- 预期结果：每步的期望输出

请使用 openpyxl 库生成 Excel 文件。
```

## 目录结构
```
ui_test/
├── main.py              # 主入口
├── test_cases/          # 测试用例输出目录
├── requirements.txt     # 添加 openpyxl
└── ...
```

## 依赖
- openpyxl：用于生成 Excel 文件

## 验证
```bash
opencode serve
python main.py
# 按提示输入：
# UI 地址：https://www.baidu.com
# 保存路径：test_cases/baidu_search.xlsx
# 登录账号：（回车跳过）
# 登录密码：（回车跳过）
# 描述：百度搜索功能测试
# 检查 test_cases/baidu_search.xlsx 是否生成
```
