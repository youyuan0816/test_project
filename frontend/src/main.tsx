import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import enUS from 'antd/locale/en_US';
import App from './App';
import './index.css';
import './i18n';
import { useTranslation } from 'react-i18next';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function AppWrapper() {
  const { i18n } = useTranslation();
  const [antLocale, setAntLocale] = useState(i18n.language === 'zh' ? zhCN : enUS);

  useEffect(() => {
    const updateLocale = () => {
      setAntLocale(i18n.language === 'zh' ? zhCN : enUS);
    };
    i18n.on('languageChanged', updateLocale);
    return () => {
      i18n.off('languageChanged', updateLocale);
    };
  }, [i18n]);

  return (
    <ConfigProvider locale={antLocale}>
      <QueryClientProvider client={queryClient}>
        <App />
      </QueryClientProvider>
    </ConfigProvider>
  );
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppWrapper />
  </React.StrictMode>
);
