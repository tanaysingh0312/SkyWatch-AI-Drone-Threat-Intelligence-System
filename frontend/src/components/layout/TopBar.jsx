import React from 'react';
import { Shield, Radio, Activity } from 'lucide-react';

export const TopBar = ({ sessionActive, telemetry, frameCount, sessionId }) => {
  return (
    <header className="topbar">
      <div className="topbar-left">
        <Shield className="icon-cyan" size={20} />
        <span className="logo-text">DRONE SECURITY <span className="logo-sep">|</span> <span className="logo-sub">ANALYST AGENT</span></span>
        <span className="version-badge">v1.0.0</span>
      </div>
      
      <div className="topbar-center mono">
        <span>SESSION: {sessionId || 'OFFLINE'}</span>
        <span className="dot-sep">•</span>
        <span>{new Date(telemetry.timestamp).toISOString().replace('T', ' ').split('.')[0]} UTC</span>
      </div>
      
      <div className="topbar-right">
        <div className="status-item">
          <div className={`status-led ${sessionActive ? 'pulse-green' : 'led-off'}`}></div>
          <span className="status-text">{sessionActive ? 'LIVE' : 'OFFLINE'}</span>
        </div>
        <div className="status-item mono">
          <Activity size={14} className="icon-muted" />
          <span>{frameCount.toLocaleString()} FRAMES</span>
        </div>
        <div className="status-item health">
          <Radio size={14} className="icon-safe" />
          <span className="status-text-small">SYSTEMS NOMINAL</span>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .topbar {
          height: 64px;
          border-bottom: 1px solid var(--border-normal);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 32px;
          background-color: var(--bg-surface);
          box-shadow: var(--shadow-sm);
          z-index: 100;
        }
        .topbar-left {
          display: flex;
          align-items: center;
          gap: 16px;
        }
        .icon-cyan { color: var(--cyan-bright); }
        .logo-text {
          font-family: var(--font-display);
          font-size: 20px;
          font-weight: 800;
          color: var(--text-primary);
        }
        .logo-sep { color: var(--border-strong); margin: 0 4px; }
        .logo-sub {
          font-size: 12px;
          font-weight: 500;
          color: var(--cyan-bright);
          letter-spacing: 0.1em;
        }
        .version-badge {
          font-size: 10px;
          padding: 2px 8px;
          background-color: var(--bg-raised);
          border: 1px solid var(--border-normal);
          border-radius: 20px;
          color: var(--text-secondary);
        }
        .topbar-center {
          font-size: 13px;
          font-weight: 600;
          color: var(--text-secondary);
          display: flex;
          align-items: center;
          background-color: var(--bg-raised);
          padding: 6px 16px;
          border-radius: 30px;
        }
        .dot-sep { margin: 0 12px; color: var(--border-strong); }
        .topbar-right {
          display: flex;
          align-items: center;
          gap: 24px;
        }
        .status-item {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
          font-weight: 600;
          color: var(--text-secondary);
        }
        .status-led {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }
        .pulse-green {
          background-color: var(--safe);
          position: relative;
        }
        .pulse-green::after {
          content: '';
          position: absolute;
          width: 100%;
          height: 100%;
          border-radius: 50%;
          border: 2px solid var(--safe);
          animation: pulse-ring 2s infinite;
        }
        .led-off { background-color: var(--border-strong); }
        .status-text-small { font-size: 11px; font-weight: 700; color: var(--safe); }
        .icon-muted { color: var(--text-tertiary); }
        .icon-safe { color: var(--safe); }
      `}} />
    </header>
  );
};
