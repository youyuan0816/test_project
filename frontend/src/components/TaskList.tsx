import { useState } from 'react';
import { useTaskStore } from '@/stores/taskStore';
import { Table, Tag, Button, Space, Upload, message } from 'antd';
import { api } from '@/services/api';
import type { ColumnsType } from 'antd/es/table';

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
        <Space>
          {record.status === 'completed' && record.result_file && (
            <>
              <Upload
                accept=".xlsx"
                showUploadList={false}
                beforeUpload={(file) => {
                  handleUpload(record, file);
                  return false;
                }}
                disabled={uploadingTasks.has(record.id)}
              >
                <Button size="small" loading={uploadingTasks.has(record.id)}>
                  Upload Excel
                </Button>
              </Upload>
              <Button
                size="small"
                onClick={() => handleGenerate(record)}
                disabled={!record.result_file}
                loading={generatingTasks.has(record.id)}
              >
                Generate Code
              </Button>
            </>
          )}
          {record.status === 'completed' && record.result_file && (
            <Button
              size="small"
              type="primary"
              onClick={() => handleDownload(record)}
            >
              Download
            </Button>
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
