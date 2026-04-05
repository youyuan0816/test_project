import { useState, useEffect } from 'react';
import { Table, Button, Tag, Dropdown } from 'antd';
import type { MenuProps } from 'antd';
import { DownloadOutlined, PlayCircleOutlined, EyeOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { api } from '@/services/api';
import type { TestCase } from '@/services/types';
import { TestExecutionModal } from './TestExecutionModal';

export function TestCases() {
  const { t } = useTranslation('global');
  const { t: tPage } = useTranslation('pages');
  const [testcases, setTestcases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [executionModal, setExecutionModal] = useState<{
    open: boolean;
    taskId: string;
    taskName: string;
  }>({
    open: false,
    taskId: '',
    taskName: ''
  });
  const [runningTasks, setRunningTasks] = useState<Set<string>>(new Set());
  const [detailModal, setDetailModal] = useState<{ open: boolean; taskId: string; taskName: string; logContent?: string; reportUrl?: string }>({
    open: false,
    taskId: '',
    taskName: '',
    logContent: '',
    reportUrl: undefined
  });

  useEffect(() => {
    setLoading(true);
    api.getTestCases()
      .then((res) => setTestcases(res.testcases))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleRunTest = (record: TestCase) => {
    setRunningTasks(prev => new Set(prev).add(record.task_id));
    setExecutionModal({ open: true, taskId: record.task_id, taskName: record.name });
  };

  const getActionItems = (record: TestCase): MenuProps['items'] => {
    const items: MenuProps['items'] = [];
    if (record.test_code_dir) {
      items.push({
        key: 'run',
        icon: <PlayCircleOutlined />,
        label: tPage('testcases.testcase.runTest'),
        disabled: runningTasks.has(record.task_id),
        onClick: () => handleRunTest(record),
      });
      items.push({
        key: 'details',
        icon: <EyeOutlined />,
        label: tPage('testcases.testcase.details'),
        onClick: async () => {
          try {
            const result = await api.getTestResult(record.task_id);
            setDetailModal({
              open: true,
              taskId: record.task_id,
              taskName: record.name,
              logContent: result.log_content,
              reportUrl: result.report_url ? `/api/test-result/${record.task_id}/report` : undefined
            });
          } catch (error) {
            console.error('Failed to fetch test result:', error);
            setDetailModal({ open: true, taskId: record.task_id, taskName: record.name, logContent: 'Failed to load log content' });
          }
        },
      });
      items.push({
        key: 'download',
        icon: <DownloadOutlined />,
        label: tPage('testcases.testcase.downloadCode'),
        onClick: () => api.downloadTestCode(record.task_id),
      });
    }
    return items;
  };

  const columns = [
    {
      title: tPage('testcases.testcase.name'),
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: tPage('testcases.testcase.excel'),
      dataIndex: 'excel_file',
      key: 'excel_file',
      render: (file: string) => file ? <Tag color="blue">{file}</Tag> : '-',
    },
    {
      title: tPage('testcases.testcase.testCode'),
      dataIndex: 'test_code_dir',
      key: 'test_code_dir',
      render: (dir: string) => dir ? <Tag color="purple">{dir}</Tag> : '-',
    },
    {
      title: tPage('testcases.testcase.createdAt'),
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
        locale={{ emptyText: tPage('testcases.testcase.empty') }}
      />
      <TestExecutionModal
        open={executionModal.open}
        taskId={executionModal.taskId}
        taskName={executionModal.taskName}
        onClose={() => setExecutionModal({ open: false, taskId: '', taskName: '' })}
        onComplete={(taskId) => {
          setRunningTasks(prev => {
            const next = new Set(prev);
            next.delete(taskId);
            return next;
          });
        }}
      />
      <TestExecutionModal
        open={detailModal.open}
        taskId={detailModal.taskId}
        taskName={detailModal.taskName}
        historyMode={true}
        initialContent={detailModal.logContent || ''}
        reportUrl={detailModal.reportUrl}
        onClose={() => setDetailModal({ open: false, taskId: '', taskName: '', logContent: '' })}
      />
    </>
  );
}
