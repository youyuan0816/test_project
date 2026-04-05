import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard key="dashboard" />} />
      <Route path="/dashboard" element={<Dashboard key="dashboard" />} />
      <Route path="/sessions" element={<Dashboard key="sessions" />} />
      <Route path="/testcases" element={<Dashboard key="testcases" />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
