import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import globalEn from '../locales/en/global.json';
import globalZh from '../locales/zh/global.json';
import dashboardEn from '../locales/en/pages/dashboard.json';
import dashboardZh from '../locales/zh/pages/dashboard.json';
import sessionsEn from '../locales/en/pages/sessions.json';
import sessionsZh from '../locales/zh/pages/sessions.json';
import testcasesEn from '../locales/en/pages/testcases.json';
import testcasesZh from '../locales/zh/pages/testcases.json';

const LANGUAGE_KEY = 'language';
const savedLanguage = localStorage.getItem(LANGUAGE_KEY) || 'zh';

i18n.use(initReactI18next).init({
  resources: {
    en: {
      global: globalEn,
      pages: {
        dashboard: dashboardEn,
        sessions: sessionsEn,
        testcases: testcasesEn,
      },
    },
    zh: {
      global: globalZh,
      pages: {
        dashboard: dashboardZh,
        sessions: sessionsZh,
        testcases: testcasesZh,
      },
    },
  },
  lng: savedLanguage,
  fallbackLng: 'zh',
  ns: ['global', 'pages'],
  defaultNS: 'global',
  interpolation: {
    escapeValue: false,
  },
});

i18n.on('languageChanged', (lng) => {
  localStorage.setItem(LANGUAGE_KEY, lng);
});

export default i18n;
