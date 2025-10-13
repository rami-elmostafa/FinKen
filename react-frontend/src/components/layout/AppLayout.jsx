import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import { useState } from 'react';

/**
 * AppLayout - Main application layout with header, sidebar, and content area
 * Used for authenticated pages
 */
function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);
  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-300">
      {/* Header */}
      <Header onToggleSidebar={toggleSidebar} />
      
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      
      {/* Main Content */}
      <main className="pt-4">
        <Outlet />
      </main>
    </div>
  );
}

export default AppLayout;
