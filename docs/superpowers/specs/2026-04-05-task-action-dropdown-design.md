# Task Action 下拉菜单设计

## 目标

将 TaskList 的 Action 列多个按钮改为下拉菜单，优化 UI 布局。

## UI 设计

将多个操作按钮合并为一个下拉菜单：

```
[操作 ▼]
  ├─ Download
  ├─ Upload Excel
  ├─ Generate Code
  └─ Remove
```

## 组件选择

使用 Ant Design 的 Dropdown + Button 组件：

```tsx
import { Dropdown, Button, Menu } from 'antd';
import type { MenuProps } from 'antd';

const items: MenuProps['items'] = [
  { key: 'download', label: 'Download', disabled: !record.result_file },
  { key: 'upload', label: 'Upload Excel', disabled: !record.result_file },
  { key: 'generate', label: 'Generate Code', disabled: !record.result_file },
  { type: 'divider' },
  { key: 'remove', label: 'Remove', danger: true },
];

<Dropdown menu={{ items }} trigger={['click']}>
  <Button>操作 <DownOutlined /></Button>
</Dropdown>
```

## 操作条件

- Download：record.result_file 存在时可用
- Upload Excel：record.result_file 存在时可用
- Generate Code：record.result_file 存在时可用
- Remove：始终可用

## 文件修改

- `frontend/src/components/TaskList.tsx`
