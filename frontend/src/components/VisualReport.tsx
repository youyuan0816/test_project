import { useState, useEffect } from 'react';
import { Card, Table, Tag, Typography, Space, Collapse, Empty } from 'antd';
import { PieChart } from './PieChart';
import { api } from '@/services/api';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;

interface VisualReportProps {
  taskId: string;
}

interface TestCase {
  name: string;
  status: string;
  duration: string;
  message: string | null;
}

export function VisualReport({ taskId }: VisualReportProps) {
  const { t } = useTranslation('pages');
  const [data, setData] = useState<{
    summary: { total: number; passed: number; failed: number; skipped: number };
    test_cases: TestCase[];
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeKey, setActiveKey] = useState<string>('summary');

  useEffect(() => {
    api.getReportData(taskId)
      .then(setData)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [taskId]);

  if (loading) return <Text>{t('testcases.visualReport.loading')}</Text>;
  if (!data) return <Empty description={t('testcases.visualReport.noData')} />;

  const { summary, test_cases } = data;
  const hasFailures = summary.failed > 0;

  const pieData = [
    { type: t('testcases.visualReport.passed'), value: summary.passed },
    { type: t('testcases.visualReport.failed'), value: summary.failed },
    { type: t('testcases.visualReport.skipped'), value: summary.skipped },
  ].filter(item => item.value > 0);

  const columns = [
    {
      title: t('testcases.visualReport.testCase'),
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: t('testcases.visualReport.status'),
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'passed' ? 'green' : status === 'failed' ? 'red' : 'orange'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: t('testcases.visualReport.duration'),
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
    },
  ];

  const failedCases = test_cases.filter(tc => tc.status === 'failed');
  const failedColumns = [
    ...columns,
    {
      title: t('testcases.visualReport.error'),
      key: 'error',
      width: 150,
      render: (_: unknown, record: TestCase) => (
        <Collapse
          items={[{
            key: '1',
            label: t('testcases.visualReport.viewError'),
            children: <pre style={{ fontSize: 12, whiteSpace: 'pre-wrap' }}>{record.message}</pre>
          }]}
        />
      ),
    },
  ];

  const items = [
    {
      key: 'summary',
      label: t('testcases.visualReport.summary'),
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Card>
            <PieChart data={pieData} width={400} height={300} />
          </Card>
          <Card title={t('testcases.visualReport.statistics')}>
            <Space size="large">
              <div><Text type="secondary">{t('testcases.visualReport.total')}:</Text> <Text strong>{summary.total}</Text></div>
              <div><Text type="secondary">{t('testcases.visualReport.passed')}:</Text> <Text strong style={{ color: '#52c41a' }}>{summary.passed}</Text></div>
              <div><Text type="secondary">{t('testcases.visualReport.failed')}:</Text> <Text strong style={{ color: '#ff4d4f' }}>{summary.failed}</Text></div>
              <div><Text type="secondary">{t('testcases.visualReport.skipped')}:</Text> <Text strong style={{ color: '#faad14' }}>{summary.skipped}</Text></div>
            </Space>
          </Card>
        </Space>
      ),
    },
    {
      key: 'cases',
      label: `${t('testcases.visualReport.cases')} (${summary.total})`,
      children: <Table dataSource={test_cases} columns={columns} rowKey="name" pagination={false} size="small" />,
    },
    ...(hasFailures ? [{
      key: 'failures',
      label: `${t('testcases.visualReport.failures')} (${summary.failed})`,
      children: <Table dataSource={failedCases} columns={failedColumns} rowKey="name" pagination={false} size="small" />,
    }] : []),
  ];

  return (
    <Collapse
      activeKey={activeKey}
      onChange={(keys) => setActiveKey(Array.isArray(keys) ? keys[0] : keys)}
      items={items}
      defaultActiveKey="summary"
    />
  );
}
