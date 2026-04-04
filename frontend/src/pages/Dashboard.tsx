import { useState, useEffect } from 'react';
import { Layout, Menu, Typography, Button, Card, Space, Table, Tag } from 'antd';
import { DashboardOutlined, FileTextOutlined, HistoryOutlined } from '@ant-design/icons';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';
import { UploadExcel } from '@/components/UploadExcel';
import { useTasks } from '@/hooks/useTasks';
import { api } from '@/services/api';
import type { Session } from '@/services/types';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

type MenuKey = 'dashboard' | 'sessions' | 'testcases';

export function Dashboard() {
  const [selectedMenu, setSelectedMenu] = useState<MenuKey>('dashboard');
  const [showNewTask, setShowNewTask] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [sessions, setSessions] = useState<Record<string, Session>>({});
  const [sessionsLoading, setSessionsLoading] = useState(false);

  useTasks();

  useEffect(() => {
    if (selectedMenu === 'sessions') {
      setSessionsLoading(true);
      api.getSessions()
        .then((res) => {
          setSessions(res.sessions);
        })
        .catch(console.error)
        .finally(() => setSessionsLoading(false));
    }
  }, [selectedMenu]);

  const menuItems = [
    {
      key: 'dashboard' as MenuKey,
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'sessions' as MenuKey,
      icon: <HistoryOutlined />,
      label: 'Sessions',
    },
    {
      key: 'testcases' as MenuKey,
      icon: <FileTextOutlined />,
      label: 'Test Cases',
    },
  ];

  const renderContent = () => {
    switch (selectedMenu) {
      case 'sessions':
        return (
          <Card title="Sessions" loading={sessionsLoading}>
            {Object.keys(sessions).length === 0 && !sessionsLoading ? (
              <Text type="secondary">No sessions found</Text>
            ) : (
              <Table
                dataSource={Object.entries(sessions).map(([key, session]) => ({
                  key,
                  filename: key,
                  sessionId: session.session_id,
                  createdAt: session.created_at,
                  lastUsed: session.last_used,
                }))}
                columns={[
                  {
                    title: 'Excel File',
                    dataIndex: 'filename',
                    key: 'filename',
                  },
                  {
                    title: 'Session ID',
                    dataIndex: 'sessionId',
                    key: 'sessionId',
                    render: (text) => <Tag>{text}</Tag>,
                  },
                  {
                    title: 'Created At',
                    dataIndex: 'createdAt',
                    key: 'createdAt',
                  },
                  {
                    title: 'Last Used',
                    dataIndex: 'lastUsed',
                    key: 'lastUsed',
                  },
                ]}
                pagination={false}
              />
            )}
          </Card>
        );
      case 'testcases':
        return (
          <Card title="Test Cases">
            <Text type="secondary">View and manage your test cases</Text>
          </Card>
        );
      default:
        return (
          <>
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

            <Card
              title="Tasks"
              extra={
                <Space>
                  <Button icon={<HistoryOutlined />} onClick={() => setShowUpload(!showUpload)}>
                    Upload Excel
                  </Button>
                  <Button type="primary" icon={<DashboardOutlined />} onClick={() => setShowNewTask(!showNewTask)}>
                    New Task
                  </Button>
                </Space>
              }
            >
              <TaskList />
            </Card>
          </>
        );
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} style={{ background: '#001529' }}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Title level={4} style={{ color: 'white', margin: 0 }}>
            UI Test
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedMenu]}
          onClick={({ key }) => setSelectedMenu(key as MenuKey)}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff' }}>
          <Title level={4} style={{ margin: 0 }}>
            {menuItems.find(item => item.key === selectedMenu)?.label}
          </Title>
        </Header>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}
