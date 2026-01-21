import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import EmployeeDashboard from './pages/Employee';
import ManagerDashboard from './pages/Manager';
import AdminDashboard from './pages/Admin';
import { LanguageProvider } from './context/LanguageContext';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('user');
    
    if (token && userData) {
      setUser(JSON.parse(userData));
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, token) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    // Store available roles for role switching
    if (userData.available_roles) {
      localStorage.setItem('availableRoles', JSON.stringify(userData.available_roles));
    }
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  const handleRoleSwitch = (newRole) => {
    const updatedUser = {
      ...user,
      user_type: newRole,
    };
    localStorage.setItem('user', JSON.stringify(updatedUser));
    setUser(updatedUser);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <LanguageProvider>
      <BrowserRouter>
        <Routes>
          <Route 
            path="/login" 
            element={
              user ? <Navigate to="/" /> : <Login onLogin={handleLogin} />
            } 
          />
          
          <Route
            path="/*"
            element={
              !user ? (
                <Navigate to="/login" />
              ) : user.user_type === 'admin' || user.user_type === 'sub_admin' ? (
                <AdminDashboard user={user} onLogout={handleLogout} onRoleSwitch={handleRoleSwitch} />
              ) : user.user_type === 'manager' ? (
                <ManagerDashboard user={user} onLogout={handleLogout} onRoleSwitch={handleRoleSwitch} />
              ) : (
                <EmployeeDashboard user={user} onLogout={handleLogout} onRoleSwitch={handleRoleSwitch} />
              )
            }
          />
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
