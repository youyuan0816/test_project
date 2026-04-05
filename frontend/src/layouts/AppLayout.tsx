import { useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Typography, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import type { ReactNode } from 'react';
import { routes } from '@/routers';

const { Sider, Header, Content } = Layout;
const { Title } = Typography;

interface AppLayoutProps {
  children: ReactNode;
}

export function AppLayout({ children }: AppLayoutProps) {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();

  const currentPath = location.pathname;
  const currentRoute = routes.find(r => r.path === currentPath);
  const selectedKey = currentRoute ? currentRoute.path : '/';

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
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
          selectedKeys={[selectedKey]}
          onClick={handleMenuClick}
          items={routes.map(route => ({
            key: route.path,
            icon: route.icon,
            label: t(route.labelKey),
          }))}
          style={{ borderRight: 0 }}
        />
      </Sider>

      <Layout>
        <Header style={{ display: 'flex', alignItems: 'center', padding: '0 24px', background: '#fff', justifyContent: 'space-between' }}>
          <Title level={4} style={{ margin: 0 }}>
            {currentRoute ? t(currentRoute.labelKey) : ''}
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
          {children}
        </Content>
      </Layout>
    </Layout>
  );
}
