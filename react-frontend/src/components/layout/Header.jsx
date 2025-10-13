import { Link } from 'react-router-dom';
import PropTypes from 'prop-types';

/**
 * Header Component - Top navigation bar with branding and user info
 */
function Header({ onToggleSidebar }) {
  // TODO: Get user info from auth context when implemented
  const userName = 'Guest User';
  const userRole = 'accountant';
  const userProfilePicture = '/default_profile.webp';

  return (
    <header className="min-h-[200px] px-10 flex justify-between items-center">
      {/* Navigation Toggle Button */}
      <button
        onClick={onToggleSidebar}
        className="fixed top-4 left-4 z-[10000] px-4 py-2 bg-primary hover:bg-primary-dark text-secondary font-semibold rounded-md transition-colors"
        aria-label="Toggle navigation menu"
      >
        ☰ Menu
      </button>

      {/* Branding - Centered */}
      <div className="flex-1 flex justify-center">
        <Link to="/home" className="flex items-center gap-3">
          <div className="text-left">
            <h1 className="text-4xl font-semibold mb-1">
              <span className="text-black">Fin</span>
              <span className="text-primary-dark">Ken</span>
            </h1>
            <p className="text-black text-base font-normal">
              Financial Accounting System
            </p>
          </div>
          <img 
            src="/finkenlogo.png" 
            alt="FinKen Logo" 
            className="h-40 w-auto object-contain"
          />
        </Link>
      </div>

      {/* User Info */}
      <div className="flex items-center gap-4 bg-gray-50 px-5 py-3 rounded-full shadow-elevated border border-gray-200">
        <div className="flex flex-col items-end text-right">
          <span className="text-base font-semibold text-gray-900">{userName}</span>
          <span className="text-xs bg-blue-600 text-white px-2 py-0.5 rounded-xl font-medium uppercase tracking-wide">
            {userRole}
          </span>
        </div>
        <div className="flex items-center">
          <img 
            src={userProfilePicture} 
            alt={`${userName}'s profile`}
            className="w-11 h-11 rounded-full object-cover border-2 border-blue-600 shadow-sm"
          />
        </div>
      </div>
    </header>
  );
}

Header.propTypes = {
  onToggleSidebar: PropTypes.func.isRequired,
};

export default Header;
