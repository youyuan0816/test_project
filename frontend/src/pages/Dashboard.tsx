import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Layout, Menu, Typography, Button, Card, Table, Tag, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DashboardOutlined, FileTextOutlined, HistoryOutlined } from '@ant-design/icons';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';
import { UploadExcel } from '@/components/UploadExcel';
import { TestCases } from '@/components/TestCases';
import { useTasks } from '@/hooks/useTasks';
import { api } from '@/services/api';
import type { Session } from '@/services/types';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;

type MenuKey = 'dashboard' | 'sessions' | 'testcases';

export function Dashboard() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const navigate = useNavigate();
  const [showNewTask, setShowNewTask] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);

  const getSelectedMenu = (): MenuKey => {
    const path = location.pathname.slice(1);
    if (path === 'sessions' || path === 'testcases') return path;
    return 'dashboard';
  };

  const selectedMenu = getSelectedMenu();

  const handleMenuClick = ({ key }: { key: string }) => {
    if (key === 'dashboard') {
      navigate('/dashboard');
    } else {
      navigate(`/${key}`);
    }
  };

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
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: t('nav.dashboard'),
    },
    {
      key: 'sessions',
      icon: <HistoryOutlined />,
      label: t('nav.sessions'),
    },
    {
      key: 'testcases',
      icon: <FileTextOutlined />,
      label: t('nav.testcases'),
    },
  ];

  const renderContent = () => {
    switch (selectedMenu) {
      case 'sessions':
        return (
          <Card title={t('card.sessions')} loading={sessionsLoading}>
            {sessions.length === 0 && !sessionsLoading ? (
              <Text type="secondary">{t('card.noSessions')}</Text>
            ) : (
              <Table
                dataSource={sessions.map((session) => ({
                  key: session.id,
                  filename: session.excel_path,
                  sessionId: session.id,
                  createdAt: session.created_at,
                  lastUsed: session.last_used,
                }))}
                columns={[
                  {
                    title: t('session.excelFile'),
                    dataIndex: 'filename',
                    key: 'filename',
                  },
                  {
                    title: t('session.sessionId'),
                    dataIndex: 'sessionId',
                    key: 'sessionId',
                    render: (text) => <Tag>{text}</Tag>,
                  },
                  {
                    title: t('session.createdAt'),
                    dataIndex: 'createdAt',
                    key: 'createdAt',
                    render: (text: string) => text ? new Date(text).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '-',
                  },
                  {
                    title: t('session.lastUsed'),
                    dataIndex: 'lastUsed',
                    key: 'lastUsed',
                    render: (text: string) => text ? new Date(text).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '-',
                  },
                ]}
                pagination={false}
              />
            )}
          </Card>
        );
      case 'testcases':
        return (
          <Card title={t('card.testCases')}>
            <TestCases />
          </Card>
        );
      default:
        return (
          <>
            {showNewTask && (
              <Card
                title={t('card.newTask')}
                extra={<Button onClick={() => setShowNewTask(false)}>{t('button.close')}</Button>}
                style={{ marginBottom: 16 }}
              >
                <Text type="secondary">{t('card.generateExcelDesc')}</Text>
                <div style={{ marginTop: 16 }}>
                  <NewTaskForm onClose={() => setShowNewTask(false)} />
                </div>
              </Card>
            )}

            {showUpload && (
              <Card
                title={t('card.continueSession')}
                extra={<Button onClick={() => setShowUpload(false)}>{t('button.close')}</Button>}
                style={{ marginBottom: 16 }}
              >
                <Text type="secondary">{t('card.uploadExcelDesc')}</Text>
                <div style={{ marginTop: 16 }}>
                  <UploadExcel onClose={() => setShowUpload(false)} />
                </div>
              </Card>
            )}

            {!showNewTask && !showUpload && (
              <Card
                title={t('card.tasks')}
                extra={
                  <Button type="primary" icon={<DashboardOutlined />} onClick={() => setShowNewTask(!showNewTask)}>
                    {t('button.newTask')}
                  </Button>
                }
              >
                <TaskList />
              </Card>
            )}
          </>
        );
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider width={200} style={{ background: '#001529' }}>
        <div style={{ height: 64, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Title level={4} style={{ color: 'white', margin: 0 }}>
            {t('header.title')}
          </Title>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedMenu === 'dashboard' ? 'dashboard' : selectedMenu]}
          onClick={handleMenuClick}
          items={menuItems}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            {menuItems.find(item => item.key === (selectedMenu === 'dashboard' ? 'dashboard' : selectedMenu))?.label}
          </Title>
          <Select
            value={i18n.language}
            onChange={(lng) => i18n.changeLanguage(lng)}
            bordered={false}
            style={{ width: 100, background: 'transparent' }}
            options={[
              { value: 'zh', label: '中文' },
              { value: 'en', label: 'English' },
            ]}
          />
        </Header>

        <Content style={{ padding: '24px', background: '#f0f2f5' }}>
          {renderContent()}
        </Content>
      </Layout>
    </Layout>
  );
}
