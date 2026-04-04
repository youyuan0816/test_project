# Task Action 下拉菜单实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 TaskList 的 Action 列多个按钮改为下拉菜单

**Architecture:** 使用 Ant Design Dropdown + Menu 组件替换多个 Button

**Tech Stack:** React, Ant Design

---

## Task 1: 修改 TaskList 为下拉菜单

**Files:**
- Modify: `frontend/src/components/TaskList.tsx`

- [ ] **Step 1: 查看当前 TaskList 代码**

```tsx
// 当前 Action 列 (lines 97-140)
{
  title: 'Action',
  key: 'action',
  render: (_: unknown, record: TaskData) => (
    <Space>
      {record.status === 'completed' && record.result_file && (
        <>
          <Upload ...><Button>Upload Excel</Button></Upload>
          <Button onClick={() => handleGenerate(record)}>Generate Code</Button>
        </>
      )}
      {record.status === 'completed' && record.result_file && (
        <Button type="primary" onClick={() => handleDownload(record)}>Download</Button>
      )}
      <Button danger onClick={() => removeTask(record.id)}>Remove</Button>
    </Space>
  ),
}
```

- [ ] **Step 2: 添加 Dropdown 导入**

```tsx
import { Dropdown, Menu } from 'antd';
import { DownOutlined } from '@ant-design/icons';
```

- [ ] **Step 3: 创建 Menu items 配置**

```tsx
const actionItems: MenuProps['items'] = [
  {
    key: 'download',
    label: 'Download',
    disabled: !record.result_file,
  },
  {
    key: 'upload',
    label: 'Upload Excel',
    disabled: !record.result_file,
  },
  {
    key: 'generate',
    label: 'Generate Code',
    disabled: !record.result_file,
  },
  { type: 'divider' },
  {
    key: 'remove',
    label: 'Remove',
    danger: true,
  },
];
```

- [ ] **Step 4: 添加点击处理函数**

```tsx
const handleMenuClick = (key: string, record: TaskData) => {
  switch (key) {
    case 'download':
      handleDownload(record);
      break;
    case 'upload':
      // Trigger upload - need file input ref or state
      break;
    case 'generate':
      handleGenerate(record);
      break;
    case 'remove':
      removeTask(record.id);
      break;
  }
};
```

- [ ] **Step 5: 替换 Action 列渲染**

```tsx
{
  title: 'Action',
  key: 'action',
  render: (_: unknown, record: TaskData) => (
    <Dropdown
      menu={{
        items: actionItems,
        onClick: ({ key }) => handleMenuClick(key, record),
      }}
      trigger={['click']}
    >
      <Button size="small">
        操作 <DownOutlined />
      </Button>
    </Dropdown>
  ),
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/TaskList.tsx
git commit -m "feat: convert TaskList actions to dropdown menu"
```
