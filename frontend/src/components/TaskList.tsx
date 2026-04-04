import { useTaskStore } from '@/stores/taskStore';
import { Table, Tag, Button, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';

interface TaskData {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  result?: string;
}

export function TaskList() {
  const { tasks, removeTask } = useTaskStore();

  const columns: ColumnsType<TaskData> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'URL',
      dataIndex: 'url',
      key: 'url',
      render: (url: string) => url || '-',
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const color = status === 'completed' ? 'green' : status === 'failed' ? 'red' : 'blue';
        return <Tag color={color}>{status}</Tag>;
      },
    },
    {
      title: 'Created',
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: 'Action',
      key: 'action',
      render: (_: unknown, record: TaskData) => (
        <Space>
          {record.status === 'completed' && (
            <Button size="small">Download</Button>
          )}
          <Button size="small" danger onClick={() => removeTask(record.id)}>
            Remove
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={tasks}
      rowKey="id"
      pagination={false}
      locale={{ emptyText: 'No tasks yet. Create a new task to get started.' }}
    />
  );
}
