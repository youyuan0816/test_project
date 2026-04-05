import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/layouts/AppLayout';
import { Dashboard } from '@/pages/Dashboard';
import { Sessions } from '@/pages/Sessions';
import { TestCasesPage } from '@/pages/TestCasesPage';

function App() {
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/sessions" element={<Sessions />} />
          <Route path="/testcases" element={<TestCasesPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
