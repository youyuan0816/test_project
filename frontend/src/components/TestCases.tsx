import { useState, useEffect } from 'react';
import { Table, Button, Tag, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { DownloadOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { api } from '@/services/api';
import type { TestCase } from '@/services/types';
import { TestExecutionModal } from './TestExecutionModal';

export function TestCases() {
  const { t } = useTranslation();
  const [testcases, setTestcases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [executionModal, setExecutionModal] = useState<{ open: boolean; taskId: string; taskName: string }>({
    open: false,
    taskId: '',
    taskName: ''
  });

  useEffect(() => {
    setLoading(true);
    api.getTestCases()
      .then((res) => setTestcases(res.testcases))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const getActionItems = (record: TestCase): MenuProps['items'] => {
    const items: MenuProps['items'] = [];
    if (record.test_code_dir) {
      items.push({
        key: 'run',
        icon: <PlayCircleOutlined />,
        label: t('testcase.runTest'),
        onClick: () => setExecutionModal({ open: true, taskId: record.task_id, taskName: record.name }),
      });
      items.push({
        key: 'download',
        icon: <DownloadOutlined />,
        label: t('testcase.downloadCode'),
        onClick: () => api.downloadTestCode(record.task_id),
      });
    }
    return items;
  };

  const columns = [
    {
      title: t('testcase.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: t('testcase.excel'),
      dataIndex: 'excel_file',
      key: 'excel_file',
      render: (file: string) => file ? <Tag color="blue">{file}</Tag> : '-',
    },
    {
      title: t('testcase.testCode'),
      dataIndex: 'test_code_dir',
      key: 'test_code_dir',
      render: (dir: string) => dir ? <Tag color="purple">{dir}</Tag> : '-',
    },
    {
      title: t('testcase.createdAt'),
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => date ? new Date(date).toLocaleString() : '-',
    },
    {
      title: t('common.action'),
      key: 'action',
      render: (_: unknown, record: TestCase) => (
        <Dropdown
          menu={{ items: getActionItems(record) }}
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
      <Table
        dataSource={testcases}
        columns={columns}
        rowKey="task_id"
        pagination={false}
        loading={loading}
        locale={{ emptyText: t('testcase.empty') }}
      />
      <TestExecutionModal
        open={executionModal.open}
        taskId={executionModal.taskId}
        taskName={executionModal.taskName}
        onClose={() => setExecutionModal({ open: false, taskId: '', taskName: '' })}
      />
    </>
  );
}