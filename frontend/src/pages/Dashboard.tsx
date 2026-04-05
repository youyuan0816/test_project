import { useState } from 'react';
import { Layout, Typography, Button, Card } from 'antd';
import { DashboardOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import { TaskList } from '@/components/TaskList';
import { NewTaskForm } from '@/components/NewTaskForm';

const { Content, Header } = Layout;
const { Title, Text } = Typography;

export function Dashboard() {
  const { t } = useTranslation('global');
  const { t: tPage } = useTranslation('pages');
  const [showNewTask, setShowNewTask] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff', justifyContent: 'space-between' }}>
        <Title level={4} style={{ margin: 0 }}>{t('nav.dashboard')}</Title>
        <Button
          type="primary"
          icon={<DashboardOutlined />}
          onClick={() => setShowNewTask(!showNewTask)}
        >
          {t('button.newTask')}
        </Button>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        {showNewTask && (
          <Card
            title={tPage('dashboard.card.newTask')}
            extra={<Button onClick={() => setShowNewTask(false)}>{t('button.close')}</Button>}
            style={{ marginBottom: 16 }}
          >
            <Text type="secondary">{tPage('dashboard.card.generateExcelDesc')}</Text>
            <div style={{ marginTop: 16 }}>
              <NewTaskForm onClose={() => setShowNewTask(false)} />
            </div>
          </Card>
        )}

        <Card title={tPage('dashboard.card.tasks')}>
          <TaskList />
        </Card>
      </Content>
    </Layout>
  );
}
