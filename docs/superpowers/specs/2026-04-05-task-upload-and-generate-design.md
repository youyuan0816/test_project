# Task 上传 Excel 和生成代码功能设计

## 目标

为每个 Task 添加：
1. **上传 Excel** - 替换该 task 的 Excel 文件，并立即触发生成测试代码
2. **生成代码按钮** - 手动触发生成测试代码（不替换文件）

## 数据流

```
Task 创建 → Excel 生成 → [上传新 Excel 替换] → [点击生成代码] → 测试代码生成
                         ↑ 立即触发 continue_session
```

## 后端改动

### 新增 API

**POST /upload/:task_id**
- 接收 multipart/form-data，包含 Excel 文件
- 获取该 task 的 result_file 路径
- 用上传的文件替换现有 Excel
- 立即调用 continue_session 生成测试代码
- 返回 { task_id, status, message }

### 修改文件

- `backend/src/api.py`

## 前端改动

### TaskList 组件

每行操作列添加：
1. **上传 Excel 按钮** - 触发文件选择，上传后自动触发生成
2. **生成代码按钮** - 只触发生成，不上传文件

### 新增 API

**POST /upload/:task_id** - 上传 Excel 并触发生成

### 修改文件

- `frontend/src/components/TaskList.tsx` - 添加操作按钮
- `frontend/src/services/api.ts` - 添加 uploadExcel API

## 实现步骤

1. 后端：添加 `POST /upload/:task_id` 接口
2. 前端：api.ts 添加 uploadExcel 方法
3. 前端：TaskList 添加上传和生成按钮
4. 测试验证
