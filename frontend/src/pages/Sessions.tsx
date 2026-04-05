import { useState, useEffect } from 'react';
import { Layout, Typography, Card, Table, Tag } from 'antd';
import { useTranslation } from 'react-i18next';
import { api } from '@/services/api';
import type { Session } from '@/services/types';

const { Content, Header } = Layout;
const { Title, Text } = Typography;

export function Sessions() {
  const { t } = useTranslation('global');
  const { t: tPage } = useTranslation('pages');
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    api.getSessions()
      .then((res) => setSessions(res.sessions))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff' }}>
        <Title level={4} style={{ margin: 0 }}>{t('nav.sessions')}</Title>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <Card title={tPage('sessions.card.sessions')} loading={loading}>
          {sessions.length === 0 && !loading ? (
            <Text type="secondary">{tPage('sessions.card.noSessions')}</Text>
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
                  title: tPage('sessions.session.excelFile'),
                  dataIndex: 'filename',
                  key: 'filename',
                },
                {
                  title: tPage('sessions.session.sessionId'),
                  dataIndex: 'sessionId',
                  key: 'sessionId',
                  render: (text: string) => <Tag>{text}</Tag>,
                },
                {
                  title: tPage('sessions.session.createdAt'),
                  dataIndex: 'createdAt',
                  key: 'createdAt',
                  render: (text: string) => text ? new Date(text).toLocaleString() : '-',
                },
                {
                  title: tPage('sessions.session.lastUsed'),
                  dataIndex: 'lastUsed',
                  key: 'lastUsed',
                  render: (text: string) => text ? new Date(text).toLocaleString() : '-',
                },
              ]}
              pagination={false}
            />
          )}
        </Card>
      </Content>
    </Layout>
  );
}
