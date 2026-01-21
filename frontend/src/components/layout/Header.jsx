import NotificationBell from './NotificationBell';
import LanguageToggle from '../common/LanguageToggle';
import RoleSwitcher from '../common/RoleSwitcher';

const Header = ({ title, subtitle, showNotifications = true, user, onRoleSwitch }) => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
            {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
          </div>

          {showNotifications && (
            <div className="flex items-center space-x-4">
              {user && onRoleSwitch && <RoleSwitcher user={user} onRoleSwitch={onRoleSwitch} />}
              <LanguageToggle />
              <NotificationBell />
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
