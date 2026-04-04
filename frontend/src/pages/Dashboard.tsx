import { useState } from 'react';
import { Layout, Typography, Button, Card, Space } from 'antd';
import { PlusOutlined, UploadOutlined } from '@ant-design/icons';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';
import { UploadExcel } from '@/components/UploadExcel';

const { Header, Content } = Layout;
const { Title, Text } = Typography;

export function Dashboard() {
  const [showNewTask, setShowNewTask] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
        <Title level={3} style={{ color: 'white', margin: 0 }}>
          UI Test Generator
        </Title>
        <Space>
          <Button icon={<UploadOutlined />} onClick={() => setShowUpload(!showUpload)}>
            Upload Excel
          </Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setShowNewTask(!showNewTask)}>
            New Task
          </Button>
        </Space>
      </Header>

      <Content style={{ padding: '24px' }}>
        {showNewTask && (
          <Card
            title="New Task"
            extra={<Button onClick={() => setShowNewTask(false)}>Close</Button>}
            style={{ marginBottom: 16 }}
          >
            <Text type="secondary">Generate Excel test cases from a website</Text>
            <div style={{ marginTop: 16 }}>
              <NewTaskForm onClose={() => setShowNewTask(false)} />
            </div>
          </Card>
        )}

        {showUpload && (
          <Card
            title="Continue Session"
            extra={<Button onClick={() => setShowUpload(false)}>Close</Button>}
            style={{ marginBottom: 16 }}
          >
            <Text type="secondary">Upload Excel to continue generating test code</Text>
            <div style={{ marginTop: 16 }}>
              <UploadExcel onClose={() => setShowUpload(false)} />
            </div>
          </Card>
        )}

        <Card title="Tasks">
          <TaskList />
        </Card>
      </Content>
    </Layout>
  );
}
