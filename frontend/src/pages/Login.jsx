import React, { useState } from 'react';
import { AlertCircle, LogIn, Shield } from 'lucide-react';
import { login } from '../services/api';
import Button from '../components/common/Button';
import Card from '../components/common/Card';
import LanguageToggle from '../components/common/LanguageToggle';
import { useLanguage } from '../context/LanguageContext';

const Login = ({ onLogin }) => {
  const { t } = useLanguage();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [availableRoles, setAvailableRoles] = useState([]);
  const [loginResponse, setLoginResponse] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      console.log('Attempting login with username:', username);
      const response = await login(username, password);
      console.log('Login successful:', response);
      
      // Check if user has multiple roles
      if (response.user.available_roles && response.user.available_roles.length > 1) {
        // Show role selection interface
        setLoginResponse(response);
        setAvailableRoles(response.user.available_roles);
        setSelectedRole(response.user.available_roles[0]); // Default to first role
        setLoading(false);
        return;
      }
      
      // Single role - proceed directly
      onLogin(response.user, response.access_token);
      // Redirect after a short delay to allow state to update
      setTimeout(() => {
        window.location.href = '/';
      }, 100);
    } catch (err) {
      console.error('Login error details:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data,
      });
      const errorMessage = err.response?.data?.detail || err.message || t('loginFailed');
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleRoleSelect = (role) => {
    const userWithRole = {
      ...loginResponse.user,
      user_type: role,
      selected_role: role,
      available_roles: loginResponse.user.available_roles
    };
    onLogin(userWithRole, loginResponse.access_token);
    setTimeout(() => {
      window.location.href = '/';
    }, 100);
  };

  // Role selection UI
  if (loginResponse && availableRoles.length > 1) {
    const roleLabels = {
      'admin': t('admin') || 'Admin',
      'manager': t('manager') || 'Manager',
      'sub_admin': t('subAdmin') || 'Sub-Admin',
      'employee': t('employee') || 'Employee'
    };

    const roleDescriptions = {
      'admin': t('adminDescription') || 'Full system access',
      'manager': t('managerDescription') || 'Department management access',
      'sub_admin': t('subAdminDescription') || 'Proxy admin access',
      'employee': t('employeeDescription') || 'Employee self-service access'
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="absolute top-4 right-4">
            <LanguageToggle />
          </div>

          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-4">
              <img 
                src="../images/Logo.png" 
                alt="Thirdwave Group Logo"
                className="w-12 h-12 -ml-3"
              />
              <div>
                <h1 className="text-5xl font-bold text-white mb-2 -ml-3">{t('thirdwaveGroup')}</h1>
              </div>
            </div>
            <p className="text-blue-100">{t('employeeManagementSystem')}</p>
          </div>

          <Card padding={false}>
            <div className="p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-2 text-center flex items-center justify-center gap-2">
                <Shield className="w-6 h-6 text-blue-600" />
                {t('selectRole') || 'Select Your Role'}
              </h2>
              <p className="text-sm text-gray-600 text-center mb-6">
                {t('multipleRolesMessage') || 'You have access to multiple roles. Please select one:'}
              </p>

              <div className="space-y-3">
                {availableRoles.map((role) => (
                  <button
                    key={role}
                    onClick={() => handleRoleSelect(role)}
                    className={`w-full p-4 rounded-lg border-2 transition-all text-left ${
                      selectedRole === role
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 bg-white hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        selectedRole === role
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300'
                      }`}>
                        {selectedRole === role && (
                          <div className="w-2 h-2 bg-white rounded-full"></div>
                        )}
                      </div>
                      <div>
                        <div className="font-semibold text-gray-900">{roleLabels[role]}</div>
                        <div className="text-xs text-gray-500">{roleDescriptions[role]}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <Button
                type="button"
                fullWidth
                onClick={() => handleRoleSelect(selectedRole)}
                className="mt-6"
              >
                <div className="flex items-center justify-center">
                  <Shield className="w-5 h-5 mr-2" />
                  {t('continue') || 'Continue'}
                </div>
              </Button>

              <button
                onClick={() => {
                  setLoginResponse(null);
                  setAvailableRoles([]);
                  setSelectedRole(null);
                  setUsername('');
                  setPassword('');
                  setError('');
                }}
                className="w-full mt-3 text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                {t('backToLogin') || 'Back to Login'}
              </button>
            </div>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="absolute top-4 right-4">
          <LanguageToggle />
        </div>

        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-4">
            <img 
              src="../images/Logo.png" 
              alt="Thirdwave Group Logo"
              className="w-12 h-12 -ml-3"
            />
            <div>
              <h1 className="text-5xl font-bold text-white mb-2 -ml-3">{t('thirdwaveGroup')}</h1>
            </div>
          </div>
          <p className="text-blue-100">{t('employeeManagementSystem')}</p>
        </div>

        <Card padding={false}>
          <div className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">{t('signIn')}</h2>

            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-red-700">{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('username')}
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder={t('enterYourUsername')}
                  required
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  {t('password')}
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  placeholder={t('enterYourPassword')}
                  required
                  disabled={loading}
                />
              </div>

              <Button
                type="submit"
                fullWidth
                disabled={loading}
                className="mt-6"
              >
                <div className="flex items-center justify-center">
                  <LogIn className="w-5 h-5 mr-2" />
                  {loading ? t('signingIn') : t('signIn')}
                </div>
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-xs text-gray-500 text-center">{t('demoCredentials')}:</p>
              <div className="mt-2 space-y-1 text-xs text-gray-600">
                <p><strong>{t('admin')}:</strong> admin / admin123</p>
                <p><strong>{t('manager')}:</strong> manager1 / manager123</p>
                <p><strong>{t('employee')}:</strong> john.smith / employee123</p>
              </div>
            </div>
          </div>
        </Card>

        <p className="text-center text-white text-sm mt-6">
          Thirdwave v5.1.0
        </p>
      </div>
    </div>
  );
};

export default Login;
