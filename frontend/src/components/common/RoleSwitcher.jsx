import React, { useState } from 'react';
import { ChevronDown, Shield, UserCog } from 'lucide-react';
import { useLanguage } from '../../context/LanguageContext';

const RoleSwitcher = ({ user, onRoleSwitch }) => {
  const { t } = useLanguage();
  const [showDropdown, setShowDropdown] = useState(false);

  // Check if user has multiple roles
  const availableRoles = JSON.parse(localStorage.getItem('availableRoles') || '[]');
  
  if (!availableRoles || availableRoles.length <= 1) {
    return null; // Don't show switcher if user has only one role
  }

  const getRoleIcon = (role) => {
    return role === 'admin' || role === 'sub_admin' ? <Shield className="w-4 h-4" /> : <UserCog className="w-4 h-4" />;
  };

  const getRoleLabel = (role) => {
    const labels = {
      'admin': t('admin') || 'Admin',
      'manager': t('manager') || 'Manager',
      'sub_admin': t('subAdmin') || 'Sub-Admin',
      'employee': t('employee') || 'Employee'
    };
    return labels[role] || role;
  };

  const handleRoleChange = (role) => {
    if (role === user.user_type) {
      setShowDropdown(false);
      return;
    }

    // Update user with new role
    const updatedUser = {
      ...user,
      user_type: role,
      selected_role: role
    };
    
    // Save to localStorage
    localStorage.setItem('user', JSON.stringify(updatedUser));
    
    // Call the callback to update state in App.jsx
    onRoleSwitch(role);
    
    // Redirect to home to load appropriate dashboard
    setShowDropdown(false);
    setTimeout(() => {
      window.location.href = '/';
    }, 100);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        title="Switch role"
      >
        <div className="flex items-center gap-2">
          {getRoleIcon(user.user_type)}
          <span className="text-sm font-medium">{getRoleLabel(user.user_type)}</span>
        </div>
        <ChevronDown className="w-4 h-4" />
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg z-50 border border-gray-200 dark:border-gray-700">
          <div className="p-2">
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 px-3 py-2 uppercase">
              {t('switchRole') || 'Switch Role'}
            </p>
            {availableRoles.map((role) => (
              <button
                key={role}
                onClick={() => handleRoleChange(role)}
                className={`w-full text-left px-3 py-2 rounded-lg mb-1 flex items-center gap-2 transition-colors ${
                  user.user_type === role
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-medium'
                    : 'hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}
              >
                {getRoleIcon(role)}
                {getRoleLabel(role)}
                {user.user_type === role && (
                  <span className="ml-auto text-xs">✓</span>
                )}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default RoleSwitcher;
