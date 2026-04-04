import { useState, useRef } from 'react';
import { useTaskStore } from '@/stores/taskStore';
import { Table, Tag, Button, Dropdown, Upload, message } from 'antd';
import type { MenuProps } from 'antd';
import { api } from '@/services/api';
import type { ColumnsType } from 'antd/es/table';
import type { UploadFile } from 'antd/es/upload/interface';

interface TaskData {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: string;
  result?: string;
  result_file?: string;
}

export function TaskList() {
  const { tasks, removeTask } = useTaskStore();
  const [uploadingTasks, setUploadingTasks] = useState<Set<string>>(new Set());
  const [generatingTasks, setGeneratingTasks] = useState<Set<string>>(new Set());
  const [uploadTargetTask, setUploadTargetTask] = useState<TaskData | null>(null);
  const uploadRef = useRef<any>(null);

  const handleDownload = (task: TaskData) => {
    if (task.result_file) {
      window.open(`/api/download/${task.id}`, '_blank');
    }
  };

  const handleUpload = async (task: TaskData, file: File) => {
    setUploadingTasks(prev => new Set(prev).add(task.id));
    try {
      await api.uploadExcel(task.id, file);
      message.success('File uploaded, generating code...');
    } catch (error) {
      message.error('Upload failed: ' + (error as Error).message);
    } finally {
      setUploadingTasks(prev => {
        const next = new Set(prev);
        next.delete(task.id);
        return next;
      });
    }
  };

  const handleGenerate = async (task: TaskData) => {
    if (!task.result_file) return;
    setGeneratingTasks(prev => new Set(prev).add(task.id));
    try {
      await api.continueSession({ excel_file: task.result_file });
      message.success('Generating code...');
    } catch (error) {
      message.error('Generate failed: ' + (error as Error).message);
    } finally {
      setGeneratingTasks(prev => {
        const next = new Set(prev);
        next.delete(task.id);
        return next;
      });
    }
  };

  const handleMenuClick = (key: string, record: TaskData) => {
    switch (key) {
      case 'download':
        handleDownload(record);
        break;
      case 'upload':
        setUploadTargetTask(record);
        // Trigger the hidden upload input
        uploadRef.current?.click();
        break;
      case 'generate':
        handleGenerate(record);
        break;
      case 'remove':
        removeTask(record.id);
        break;
    }
  };

  const getActionItems = (record: TaskData): MenuProps['items'] => [
    {
      key: 'download',
      label: 'Download',
      disabled: !record.result_file,
    },
    {
      key: 'upload',
      label: 'Upload Excel',
      disabled: !record.result_file || uploadingTasks.has(record.id),
    },
    {
      key: 'generate',
      label: 'Generate Code',
      disabled: !record.result_file || generatingTasks.has(record.id),
    },
    { type: 'divider' as const },
    {
      key: 'remove',
      label: 'Remove',
      danger: true,
    },
  ];

  const handleUploadChange = (info: { file: UploadFile }) => {
    if (uploadTargetTask && info.file.originFileObj) {
      handleUpload(uploadTargetTask, info.file.originFileObj);
      setUploadTargetTask(null);
    }
  };

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
        const color =
          status === 'completed' ? 'green' :
          status === 'failed' ? 'red' :
          status === 'running' ? 'blue' : 'default';
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
        <Dropdown
          menu={{
            items: getActionItems(record),
            onClick: ({ key }) => handleMenuClick(key, record),
          }}
          trigger={['click']}
        >
          <Button size="small">
            操作
          </Button>
        </Dropdown>
      ),
    },
  ];

  return (
    <>
      <Upload
        ref={uploadRef}
        accept=".xlsx"
        showUploadList={false}
        beforeUpload={() => false}
        onChange={handleUploadChange}
        style={{ display: 'none' }}
      />
      <Table
        columns={columns}
        dataSource={tasks}
        rowKey="id"
        pagination={false}
        locale={{ emptyText: 'No tasks yet. Create a new task to get started.' }}
      />
    </>
  );
}
