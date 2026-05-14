import React from 'react';
import { LayoutDashboard, Bell, Table, BarChart3, MessageSquare, ShieldAlert, Cpu } from 'lucide-react';

export const Sidebar = ({ activePage, setActivePage, isCollapsed, sessionStatus }) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'alerts', label: 'Alert Log', icon: Bell },
    { id: 'events', label: 'Event History', icon: Table },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'qa', label: 'Q&A Agent', icon: MessageSquare },
  ];

  return (
    <aside className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-nav">
        {navItems.map(item => (
          <button 
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => setActivePage(item.id)}
          >
            <item.icon size={20} />
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </div>

      <div className="sidebar-footer">
        <div className="session-status-card">
          <div className="status-row">
            <Cpu size={14} className="icon-muted" />
            <span className="font-display">SESSION_INFO</span>
          </div>
          <div className="status-data mono">
            <div className="data-row">
              <span className="label">ACTIVE</span>
              <span className="value">{sessionStatus.active ? 'YES' : 'NO'}</span>
            </div>
            <div className="data-row">
              <span className="label">DUR</span>
              <span className="value">{sessionStatus.duration}</span>
            </div>
            <div className="data-row">
              <span className="label">THRT</span>
              <span className={`value ${sessionStatus.threatLevel.toLowerCase()}`}>{sessionStatus.threatLevel}</span>
            </div>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .sidebar {
          width: 240px;
          height: calc(100vh - 64px);
          background-color: var(--bg-surface);
          border-right: 1px solid var(--border-normal);
          display: flex;
          flex-direction: column;
          transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          z-index: 90;
        }
        .sidebar.collapsed { width: 80px; }
        .sidebar-nav {
          display: flex;
          flex-direction: column;
          padding: 24px 12px;
          flex: 1;
          gap: 4px;
        }
        .nav-item {
          display: flex;
          align-items: center;
          gap: 14px;
          padding: 12px 16px;
          background: none;
          border: none;
          border-radius: var(--radius-md);
          color: var(--text-secondary);
          cursor: pointer;
          transition: all 0.2s ease;
          text-align: left;
          width: 100%;
          font-weight: 600;
          font-size: 14px;
        }
        .nav-item:hover {
          color: var(--cyan-bright);
          background-color: var(--bg-raised);
        }
        .nav-item.active {
          color: var(--cyan-bright);
          background-color: var(--cyan-glow);
          box-shadow: inset 0 0 0 1px var(--cyan-border);
        }
        .collapsed .nav-label { display: none; }
        .collapsed .nav-item { padding: 12px; justify-content: center; }
        
        .sidebar-footer {
          padding: 20px;
          border-top: 1px solid var(--border-normal);
        }
        .session-status-card {
          background-color: var(--bg-raised);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-lg);
          padding: 16px;
          font-size: 11px;
        }
        .collapsed .session-status-card { display: none; }
        .status-row {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 12px;
          color: var(--text-tertiary);
          font-weight: 700;
        }
        .status-data {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        .data-row {
          display: flex;
          justify-content: space-between;
          padding-bottom: 4px;
          border-bottom: 1px solid var(--border-subtle);
        }
        .data-row:last-child { border-bottom: none; }
        .data-row .label { color: var(--text-tertiary); font-weight: 500; }
        .data-row .value { color: var(--text-primary); font-weight: 700; }
        .value.critical { color: var(--critical); }
        .value.high { color: var(--high); }
        .value.medium { color: var(--medium); }
        .value.low { color: var(--low); }
        .value.none { color: var(--safe); }
      `}} />
    </aside>
  );
};
