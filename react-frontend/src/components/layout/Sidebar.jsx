import { Link, useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';

/**
 * Sidebar Navigation Component
 */
function Sidebar({ isOpen, onClose }) {
  const location = useLocation();

  // TODO: Filter navigation based on user role from auth context
  const navigationItems = [
    { path: '/home', label: 'Home', roles: ['administrator', 'manager', 'accountant'] },
    { path: '/users', label: 'Manage Users', roles: ['administrator'] },
    { path: '/manage-registrations', label: 'Manage Registrations', roles: ['administrator'] },
    { path: '/expiring-passwords', label: 'Expiring Passwords', roles: ['administrator'] },
    { path: '/chart-of-accounts', label: 'Chart of Accounts', roles: ['administrator', 'manager', 'accountant'] },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Overlay - click to close sidebar on mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-40 z-[10000] lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <nav
        className={`
          fixed top-0 left-0 w-64 h-screen bg-gray-700 text-white
          transition-transform duration-300 ease-in-out z-[10001]
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
        aria-label="Main navigation"
      >
        <ul className="list-none p-0 m-0">
          {navigationItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`
                  block px-4 py-4 font-semibold transition-colors
                  ${isActive(item.path)
                    ? 'bg-primary text-gray-900'
                    : 'text-white hover:bg-gray-600'
                  }
                `}
                onClick={onClose}
              >
                {item.label}
              </Link>
            </li>
          ))}
          
          {/* Sign Out */}
          <li className="mt-4 border-t border-gray-600 pt-4">
            <button
              onClick={() => {
                // TODO: Implement sign out logic
                console.log('Sign out clicked');
                onClose();
              }}
              className="block w-full text-left px-4 py-4 font-semibold text-white hover:bg-gray-600 transition-colors"
            >
              Sign Out
            </button>
          </li>
        </ul>
      </nav>
    </>
  );
}

Sidebar.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
};

export default Sidebar;
