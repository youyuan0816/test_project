import { useState, useRef } from 'react';
import { useTaskStore } from '@/stores/taskStore';
import { Table, Tag, Button, Dropdown, Upload, message, Space } from 'antd';
import type { MenuProps } from 'antd';
import { api } from '@/services/api';
import type { ColumnsType } from 'antd/es/table';
import type { UploadFile } from 'antd/es/upload/interface';
import { useTranslation } from 'react-i18next';

interface TaskData {
  id: string;
  name: string;
  url: string;
  description: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  phase?: 'excel_generation' | 'code_generation';
  createdAt: string;
  result?: string;
  result_file?: string;
}

export function TaskList() {
  const { t } = useTranslation();
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
      message.success(t('message.uploadSuccess'));
    } catch (error) {
      message.error(t('message.uploadFailed', { error: (error as Error).message }));
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
      // 传入 task_id 以复用现有 task，而不是创建新 task
      await api.continueSession({ excel_file: task.result_file, task_id: task.id });
      message.success(t('message.generatingCode'));
    } catch (error) {
      message.error(t('message.generateFailed', { error: (error as Error).message }));
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
      label: t('action.download'),
      disabled: !record.result_file,
    },
    {
      key: 'upload',
      label: t('action.upload'),
      disabled: !record.result_file || uploadingTasks.has(record.id),
    },
    {
      key: 'generate',
      label: t('action.generate'),
      disabled: !record.result_file || generatingTasks.has(record.id),
    },
    { type: 'divider' as const },
    {
      key: 'remove',
      label: t('action.remove'),
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
      title: t('task.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('task.url'),
      dataIndex: 'url',
      key: 'url',
      render: (url: string) => url || '-',
    },
    {
      title: t('task.description'),
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: t('task.status'),
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: TaskData) => {
        const phase = record.phase || 'excel_generation';
        const phaseColor = phase === 'excel_generation' ? 'blue' : 'purple';
        const statusColor =
          status === 'completed' ? 'green' :
          status === 'failed' ? 'red' :
          status === 'running' ? phaseColor : 'default';

        return (
          <Space>
            <Tag color={phaseColor}>{t(`phase.${phase}`)}</Tag>
            <Tag color={statusColor}>{t(`status.${status}`)}</Tag>
          </Space>
        );
      },
    },
    {
      title: t('task.createdAt'),
      dataIndex: 'createdAt',
      key: 'createdAt',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: t('common.action'),
      key: 'action',
      render: (_: unknown, record: TaskData) => (
        <Dropdown
          menu={{
            items: getActionItems(record),
            onClick: ({ key }) => handleMenuClick(key, record),
          }}
          trigger={['click']}
        >
          <Button type="text" size="small">
            {t('common.action')}
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
        locale={{ emptyText: t('message.noTasks') }}
      />
    </>
  );
}
