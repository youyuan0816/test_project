# Task 阶段显示设计

## 目标

区分 Task 的两种生成阶段，在 Status 区域显示不同颜色和阶段信息。

## 字段变更

**Task 表增加 `phase` 字段：**
- `phase: "excel_generation"` - Excel 测试用例生成阶段
- `phase: "code_generation"` - 测试代码生成阶段

**规则：**
- Task 创建时（generate_excel）→ phase = "excel_generation"
- 上传 Excel 或 Continue Session 触发生成 → phase = "code_generation"

## UI 显示

**Status 区域显示：**
- 阶段标签（彩色）+ 状态文字

**阶段颜色：**
- Excel生成中：蓝色 (#1677ff)
- 代码生成中：紫色 (#722ed1)

**状态颜色（保持）：**
- pending：灰色
- running：跟随阶段色（蓝/紫）
- completed：绿色
- failed：红色

**显示示例：**
```
┌─────────────────────────┐
│ [Excel生成中]  running  │  ← 蓝色阶段
└─────────────────────────┘

┌─────────────────────────┐
│ [代码生成中]  completed  │  ← 紫色阶段
└─────────────────────────┘

┌─────────────────────────┐
│ [代码生成中]  failed     │  ← 紫色阶段
└─────────────────────────┘
```

## 翻译 key

**zh.json:**
```json
{
  "phase": {
    "excel_generation": "Excel生成中",
    "code_generation": "代码生成中"
  }
}
```

**en.json:**
```json
{
  "phase": {
    "excel_generation": "Generating Excel",
    "code_generation": "Generating Code"
  }
}
```

## 文件修改

- `backend/src/db.py` - Task 表增加 phase 字段
- `backend/src/api.py` - 设置 phase 值
- `frontend/src/components/TaskList.tsx` - 显示阶段标签
- `frontend/src/locales/zh.json` - 添加翻译
- `frontend/src/locales/en.json` - 添加翻译
