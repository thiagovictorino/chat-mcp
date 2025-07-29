import React, { useState, useEffect } from 'react';
import './Navigation.css';

interface NavigationProps {
  onNavigate: (section: string) => void;
  currentSection: string;
}

const Navigation: React.FC<NavigationProps> = ({ onNavigate, currentSection }) => {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'products', label: 'Products', icon: '📦', hasDropdown: true },
    { id: 'analytics', label: 'Analytics', icon: '📈', hasDropdown: true },
    { id: 'settings', label: 'Settings', icon: '⚙️' }
  ];

  const mobileNavItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'products', label: 'Products', icon: '📦' },
    { id: 'scan', label: 'Scan', icon: '📷', isSpecial: true },
    { id: 'reports', label: 'Reports', icon: '📈' },
    { id: 'more', label: 'More', icon: '⋯' }
  ];

  if (isMobile) {
    return (
      <nav className="mobile-nav">
        {mobileNavItems.map(item => (
          <button
            key={item.id}
            className={`mobile-nav-item ${currentSection === item.id ? 'active' : ''} ${item.isSpecial ? 'special' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
    );
  }

  return (
    <nav className="desktop-nav">
      <div className="nav-logo">MCP Chat</div>
      <div className="nav-items">
        {navItems.map(item => (
          <button
            key={item.id}
            className={`nav-item ${currentSection === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            {item.hasDropdown && <span className="dropdown-indicator">▼</span>}
          </button>
        ))}
      </div>
      <div className="nav-user">
        <img className="user-avatar" src="/api/placeholder/32/32" alt="User" />
        <span className="dropdown-indicator">▼</span>
      </div>
    </nav>
  );
};

export default Navigation;