import { useState, useEffect } from 'react';
import { Card, Table, Button, Space, Tag } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { api } from '@/services/api';
import type { TestCase } from '@/services/types';

export function TestCases() {
  const { t } = useTranslation();
  const [testcases, setTestcases] = useState<TestCase[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getTestCases()
      .then((res) => setTestcases(res.testcases))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

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
        <Space>
          {record.excel_file && (
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => window.open(`/api/download/${record.task_id}`, '_blank')}
            >
              {t('testcase.downloadExcel')}
            </Button>
          )}
          {record.test_code_dir && (
            <Button
              size="small"
              icon={<DownloadOutlined />}
              onClick={() => api.downloadTestCode(record.task_id)}
            >
              {t('testcase.downloadCode')}
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <Card loading={loading}>
      {testcases.length === 0 ? (
        <span>{t('testcase.empty')}</span>
      ) : (
        <Table
          dataSource={testcases}
          columns={columns}
          rowKey="task_id"
          pagination={false}
        />
      )}
    </Card>
  );
}