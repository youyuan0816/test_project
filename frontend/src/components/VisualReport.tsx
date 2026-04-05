import { useState, useEffect } from 'react';
import { Card, Table, Tag, Typography, Space, Collapse, Empty } from 'antd';
import { PieChart } from './PieChart';
import { api } from '@/services/api';

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

  if (loading) return <Text>Loading...</Text>;
  if (!data) return <Empty description="No report data" />;

  const { summary, test_cases } = data;
  const hasFailures = summary.failed > 0;

  const pieData = [
    { type: 'Passed', value: summary.passed },
    { type: 'Failed', value: summary.failed },
    { type: 'Skipped', value: summary.skipped },
  ].filter(item => item.value > 0);

  const columns = [
    {
      title: 'Test Case',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Status',
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
      title: 'Duration',
      dataIndex: 'duration',
      key: 'duration',
      width: 100,
    },
  ];

  const failedCases = test_cases.filter(tc => tc.status === 'failed');
  const failedColumns = [
    ...columns,
    {
      title: 'Error',
      key: 'error',
      width: 150,
      render: (_: unknown, record: TestCase) => (
        <Collapse
          items={[{
            key: '1',
            label: 'View Error',
            children: <pre style={{ fontSize: 12, whiteSpace: 'pre-wrap' }}>{record.message}</pre>
          }]}
        />
      ),
    },
  ];

  const items = [
    {
      key: 'summary',
      label: 'Summary',
      children: (
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <Card>
            <PieChart data={pieData} width={400} height={300} />
          </Card>
          <Card title="Statistics">
            <Space size="large">
              <div><Text type="secondary">Total:</Text> <Text strong>{summary.total}</Text></div>
              <div><Text type="secondary">Passed:</Text> <Text strong style={{ color: '#52c41a' }}>{summary.passed}</Text></div>
              <div><Text type="secondary">Failed:</Text> <Text strong style={{ color: '#ff4d4f' }}>{summary.failed}</Text></div>
              <div><Text type="secondary">Skipped:</Text> <Text strong style={{ color: '#faad14' }}>{summary.skipped}</Text></div>
            </Space>
          </Card>
        </Space>
      ),
    },
    {
      key: 'cases',
      label: `Cases (${summary.total})`,
      children: <Table dataSource={test_cases} columns={columns} rowKey="name" pagination={false} size="small" />,
    },
    ...(hasFailures ? [{
      key: 'failures',
      label: `Failures (${summary.failed})`,
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