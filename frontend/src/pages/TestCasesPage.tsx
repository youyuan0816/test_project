import { Layout, Typography, Card } from 'antd';
import { useTranslation } from 'react-i18next';
import { TestCases } from '@/components/TestCases';

const { Content, Header } = Layout;
const { Title } = Typography;

export function TestCasesPage() {
  const { t } = useTranslation('global');
  const { t: tPage } = useTranslation('pages');

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff' }}>
        <Title level={4} style={{ margin: 0 }}>{t('nav.testcases')}</Title>
      </Header>

      <Content style={{ padding: '24px', background: '#f0f2f5' }}>
        <Card title={tPage('testcases.card.testCases')}>
          <TestCases />
        </Card>
      </Content>
    </Layout>
  );
}
