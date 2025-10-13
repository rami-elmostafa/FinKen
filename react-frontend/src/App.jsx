import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from './components/layout/AppLayout';

// Placeholder page components - will be created during migration
import LoginPage from './pages/LoginPage';
// import HomePage from './pages/HomePage';
// import CreateNewUserPage from './pages/CreateNewUserPage';
// ... more pages will be added during migration

function App() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LoginPage />} />
        <Route path="/login" element={<Navigate to="/" replace />} />
        
        {/* Protected Routes with Layout - will be uncommented as we migrate pages */}
        {/* <Route element={<AppLayout />}>
          <Route path="/home" element={<HomePage />} />
          <Route path="/create-new-user" element={<CreateNewUserPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/chart-of-accounts" element={<ChartOfAccountsPage />} />
          <Route path="/manage-registrations" element={<ManageRegistrationsPage />} />
          <Route path="/expiring-passwords" element={<ExpiringPasswordsPage />} />
        </Route> */}
        
        {/* Catch-all redirect to login */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
