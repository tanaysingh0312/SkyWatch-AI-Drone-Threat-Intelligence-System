import React from 'react';
import { Bell, CheckCircle2, ShieldAlert } from 'lucide-react';

export const AlertPanel = ({ alerts, unacknowledgedCount, dispatch, currentThreat }) => {
  return (
    <div className="alert-panel">
      <div className="alert-panel-header">
        <div className="header-title">
          <Bell size={16} className="icon-cyan" />
          <span className="font-display">SECURITY ALERTS</span>
          {unacknowledgedCount > 0 && <span className="alert-badge">{unacknowledgedCount}</span>}
        </div>
        <button className="clear-btn" onClick={() => dispatch({ type: 'ACKNOWLEDGE_ALL' })}>
          <CheckCircle2 size={14} />
          <span>ACK ALL</span>
        </button>
      </div>

      <div className="alert-list">
        {alerts.length === 0 ? (
          <div className="empty-alerts">
            <span className="mono">NO_ACTIVE_ALERTS</span>
          </div>
        ) : (
          alerts.map(alert => (
            <div 
              key={alert.id} 
              className={`alert-row ${alert.severity.toLowerCase()} ${alert.acknowledged ? 'acknowledged' : 'new'}`}
            >
              <div className="alert-status"></div>
              <div className="alert-content">
                <div className="alert-meta mono">
                  <span className={`severity-text ${alert.severity.toLowerCase()}`}>[{alert.severity}]</span>
                  <span className="alert-time">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                </div>
                <div className="alert-desc">{alert.description}</div>
                <div className="alert-footer">
                  <span className="alert-id mono">{alert.rule_id}</span>
                  {!alert.acknowledged && (
                    <button 
                      className="ack-btn"
                      onClick={() => dispatch({ type: 'ACKNOWLEDGE_ALERT', payload: alert.id })}
                    >
                      ACK
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="threat-indicator-box">
        <div className="threat-label font-display">CURRENT THREAT LEVEL</div>
        <div className={`threat-value font-display ${currentThreat.toLowerCase()}`}>
          {currentThreat}
        </div>
        <div className="threat-icon">
          <ShieldAlert size={24} className={currentThreat.toLowerCase()} />
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .alert-panel {
          width: 360px;
          height: 100%;
          background-color: var(--bg-surface);
          border-left: 1px solid var(--border-normal);
          display: flex;
          flex-direction: column;
          box-shadow: var(--shadow-lg);
          z-index: 80;
        }
        .alert-panel-header {
          padding: 24px;
          border-bottom: 1px solid var(--border-normal);
          display: flex;
          justify-content: space-between;
          align-items: center;
          background-color: var(--bg-surface);
        }
        .header-title {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 15px;
          font-weight: 800;
          color: var(--text-primary);
        }
        .alert-badge {
          background-color: var(--critical);
          color: white;
          font-size: 10px;
          padding: 2px 8px;
          border-radius: 20px;
          font-weight: 800;
          box-shadow: 0 2px 4px var(--critical-dim);
        }
        .clear-btn {
          background-color: var(--bg-raised);
          border: 1px solid var(--border-normal);
          color: var(--text-secondary);
          font-size: 10px;
          font-weight: 700;
          padding: 6px 12px;
          border-radius: 20px;
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .clear-btn:hover {
          border-color: var(--cyan-mid);
          color: var(--cyan-mid);
          background-color: var(--cyan-glow);
        }
        .alert-list {
          flex: 1;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          background-color: var(--bg-base);
        }
        .empty-alerts {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: var(--text-tertiary);
          font-size: 12px;
          gap: 12px;
          opacity: 0.6;
        }
        .alert-row {
          padding: 20px 24px;
          border-bottom: 1px solid var(--border-subtle);
          display: flex;
          gap: 16px;
          position: relative;
          background-color: var(--bg-surface);
          transition: transform 0.2s;
        }
        .alert-row:hover {
          background-color: var(--bg-raised);
        }
        .alert-row.critical.new {
          background-color: #fff1f2;
          border-bottom-color: #fecaca;
        }
        .alert-row.high.new { background-color: #fff7ed; border-bottom-color: #ffedd5; }
        .alert-row.acknowledged { opacity: 0.6; }
        
        .alert-status {
          width: 4px;
          height: 100%;
          position: absolute;
          left: 0;
          top: 0;
        }
        .alert-row.critical .alert-status { background-color: var(--critical); }
        .alert-row.high .alert-status { background-color: var(--high); }
        .alert-row.medium .alert-status { background-color: var(--medium); }
        .alert-row.low .alert-status { background-color: var(--low); }
        
        .alert-meta {
          display: flex;
          justify-content: space-between;
          font-size: 11px;
          margin-bottom: 6px;
        }
        .severity-text { font-weight: 800; letter-spacing: 0.05em; }
        .severity-text.critical { color: var(--critical); }
        .severity-text.high { color: var(--high); }
        .severity-text.medium { color: var(--medium); }
        .severity-text.low { color: var(--low); }
        .alert-time { color: var(--text-tertiary); font-weight: 600; }
        
        .alert-desc {
          font-size: 14px;
          color: var(--text-primary);
          margin-bottom: 12px;
          line-height: 1.5;
          font-weight: 500;
        }
        .alert-footer {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .alert-id {
          font-size: 10px;
          font-weight: 600;
          color: var(--text-tertiary);
          background-color: var(--bg-raised);
          padding: 2px 8px;
          border-radius: 4px;
        }
        .ack-btn {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          color: var(--cyan-mid);
          font-size: 10px;
          font-weight: 800;
          padding: 4px 12px;
          border-radius: 20px;
          cursor: pointer;
          transition: all 0.2s;
        }
        .ack-btn:hover {
          background-color: var(--cyan-bright);
          color: white;
          border-color: var(--cyan-bright);
        }
        
        .threat-indicator-box {
          padding: 32px 24px;
          background-color: var(--bg-surface);
          border-top: 1px solid var(--border-normal);
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 12px;
          box-shadow: 0 -4px 12px rgba(0,0,0,0.02);
        }
        .threat-label {
          font-size: 11px;
          font-weight: 800;
          color: var(--text-tertiary);
          letter-spacing: 0.1em;
        }
        .threat-value {
          font-size: 42px;
          font-weight: 900;
          line-height: 1;
        }
        .threat-value.critical { color: var(--critical); }
        .threat-value.high { color: var(--high); }
        .threat-value.medium { color: var(--medium); }
        .threat-value.low { color: var(--low); }
        .threat-value.none { color: var(--safe); }
        
        .threat-icon { margin-top: 4px; }
        .threat-icon .critical { color: var(--critical); }
        .threat-icon .high { color: var(--high); }
        .threat-icon .medium { color: var(--medium); }
        .threat-icon .low { color: var(--low); }
        .threat-icon .none { color: var(--safe); }
      `}} />
    </div>
  );
};
