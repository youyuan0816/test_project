import { DashboardOutlined, FileTextOutlined, HistoryOutlined } from '@ant-design/icons';
import type { ReactElement } from 'react';

export interface RouteConfig {
  path: string;
  labelKey: string;
  icon: ReactElement;
}

export const routes: RouteConfig[] = [
  { path: '/', labelKey: 'nav.dashboard', icon: <DashboardOutlined /> },
  { path: '/sessions', labelKey: 'nav.sessions', icon: <HistoryOutlined /> },
  { path: '/testcases', labelKey: 'nav.testcases', icon: <FileTextOutlined /> },
];
