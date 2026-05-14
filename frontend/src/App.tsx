import React, { useState, useEffect } from 'react';
import './App.css';
import { TopBar } from './components/layout/TopBar';
import { Sidebar } from './components/layout/Sidebar';
import { StatusStrip } from './components/layout/StatusStrip';
import { Dashboard } from './pages/Dashboard';
import { EventsPage } from './pages/EventsPage';
import { QAPage } from './pages/QAPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { useWebSocket } from './hooks/useWebSocket';
import { useAlerts } from './hooks/useAlerts';
import { useTelemetry } from './hooks/useTelemetry';
import { Play, Square, FileText, ChevronRight } from 'lucide-react';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [showSummaryModal, setShowSummaryModal] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const {
    currentFrame,
    allFrames,
    isConnected,
    startSession,
    stopSession,
    sessionActive,
    processing,
    sessionId
  } = useWebSocket();

  const { alerts, unacknowledgedCount, criticalCount, dispatch: alertDispatch } = useAlerts();
  const telemetry = useTelemetry(currentFrame);

  // Trigger alerts when a frame with alerts arrives
  useEffect(() => {
    if (currentFrame && currentFrame.alerts && currentFrame.alerts.length > 0) {
      currentFrame.alerts.forEach(alert => {
        alertDispatch({ type: 'ADD_ALERT', payload: { ...alert, acknowledged: false } });
      });
    }
  }, [currentFrame, alertDispatch]);

  const handleStopSession = () => {
    stopSession();
    setShowSummaryModal(true);
  };

  const sessionStatus = {
    active: sessionActive,
    duration: telemetry.sessionTime,
    threatLevel: currentFrame?.threat_level || 'NONE'
  };

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return (
          <Dashboard
            currentFrame={currentFrame}
            telemetry={telemetry}
            allFrames={allFrames}
            sessionActive={sessionActive}
            processing={processing}
            alerts={alerts}
            unacknowledgedCount={unacknowledgedCount}
            alertDispatch={alertDispatch}
          />
        );
      case 'events':
        return <EventsPage allFrames={allFrames} />;
      case 'qa':
        return <QAPage allFrames={allFrames} />;
      case 'analytics':
        return <AnalyticsPage allFrames={allFrames} alerts={alerts} />;
      default:
        return (
          <Dashboard
            currentFrame={currentFrame}
            telemetry={telemetry}
            allFrames={allFrames}
            sessionActive={sessionActive}
            processing={processing}
            alerts={alerts}
            unacknowledgedCount={unacknowledgedCount}
            alertDispatch={alertDispatch}
          />
        );
    }
  };

  return (
    <div className="app-container">
      <TopBar
        sessionActive={sessionActive}
        telemetry={telemetry}
        frameCount={allFrames.length}
        sessionId={sessionId}
      />

      <div className="main-layout">
        <Sidebar
          activePage={activePage}
          setActivePage={setActivePage}
          isCollapsed={sidebarCollapsed}
          sessionStatus={sessionStatus}
        />

        <main className="content-area">
          <div className="session-controls">
            {!sessionActive ? (
              <button className="ctrl-btn start" onClick={startSession}>
                <Play size={16} fill="currentColor" />
                <span className="font-display">START MISSION</span>
              </button>
            ) : (
              <button className="ctrl-btn stop" onClick={handleStopSession}>
                <Square size={16} fill="currentColor" />
                <span className="font-display">ABORT MISSION</span>
              </button>
            )}

            {sessionActive && (
              <div className="live-mission-stats mono">
                <div className="stat">ELAPSED: {telemetry.sessionTime}</div>
                <div className="stat">ALERTS: {alerts.length}</div>
                <div className="stat">CRITICAL: {criticalCount}</div>
              </div>
            )}
          </div>

          {renderPage()}
        </main>
      </div>

      <StatusStrip isConnected={isConnected} frameCount={allFrames.length} />

      {showSummaryModal && (
        <div className="modal-overlay">
          <div className="summary-modal page-enter">
            <div className="modal-header">
              <h2 className="font-display">MISSION DEBRIEF COMPLETE</h2>
              <div className="session-id mono">SESSION_ID: 882-X9</div>
            </div>

            <div className="summary-body">
              <div className="ai-summary-card">
                <div className="icon-wrap">
                  <FileText size={48} className="icon-cyan" />
                </div>
                <div className="summary-text">
                  <h3 className="font-display">ANALYST REPORT</h3>
                  <p>Session Alpha-7: {allFrames.length} frames processed. {alerts.length} potential threats identified. Security environment remains under tactical control after one neutralized intrusion event.</p>
                </div>
              </div>

              <div className="stats-grid">
                <div className="stat-box">
                  <div className="label mono">DURATION</div>
                  <div className="value font-display">{telemetry.sessionTime}</div>
                </div>
                <div className="stat-box">
                  <div className="label mono">ALERTS</div>
                  <div className="value font-display">{alerts.length}</div>
                </div>
                <div className="stat-box">
                  <div className="label mono">CRITICAL</div>
                  <div className="value font-display text-danger">{criticalCount}</div>
                </div>
                <div className="stat-box">
                  <div className="label mono">AVG_FPS</div>
                  <div className="value font-display">59.8</div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="modal-btn secondary" onClick={() => setShowSummaryModal(false)}>
                NEW MISSION
              </button>
              <button className="modal-btn primary" onClick={() => { setShowSummaryModal(false); setActivePage('analytics'); }}>
                VIEW FULL ANALYTICS
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        .app-container {
          display: flex;
          flex-direction: column;
          height: 100vh;
          width: 100vw;
          background-color: var(--bg-base);
          color: var(--text-primary);
          font-family: var(--font-body);
        }
        .main-layout {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        .content-area {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
          position: relative;
        }
        .session-controls {
          position: absolute;
          top: 32px;
          right: 360px; /* Aligned with AlertPanel edge */
          z-index: 50;
          display: flex;
          align-items: center;
          gap: 20px;
          pointer-events: none;
        }
        .ctrl-btn {
          pointer-events: auto;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 24px;
          border: none;
          border-radius: var(--radius-md);
          font-family: var(--font-display);
          font-weight: 800;
          font-size: 14px;
          cursor: pointer;
          transition: all 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          box-shadow: var(--shadow-md);
          letter-spacing: 0.05em;
        }
        .ctrl-btn:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
        .ctrl-btn:active { transform: scale(0.95); }
        .ctrl-btn.start {
          background-color: var(--cyan-bright);
          color: white;
        }
        .ctrl-btn.stop {
          background-color: var(--critical);
          color: white;
        }
        
        .live-mission-stats {
          background-color: var(--bg-surface);
          padding: 8px 20px;
          border-radius: 30px;
          border: 1px solid var(--border-normal);
          display: flex;
          gap: 20px;
          font-size: 11px;
          font-weight: 700;
          box-shadow: var(--shadow-sm);
        }
        .stat { color: var(--text-secondary); }
        .stat span { color: var(--cyan-mid); }
        
        .modal-overlay {
          position: fixed;
          inset: 0;
          background: rgba(15, 23, 42, 0.4);
          backdrop-filter: blur(8px);
          z-index: 1000;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 40px;
        }
        .summary-modal {
          background-color: var(--bg-surface);
          width: 100%;
          max-width: 640px;
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-lg);
          overflow: hidden;
          box-shadow: var(--shadow-lg);
        }
        .modal-header {
          padding: 32px;
          background-color: var(--bg-surface);
          border-bottom: 1px solid var(--border-subtle);
        }
        .modal-header h2 { color: var(--text-primary); font-weight: 800; margin-bottom: 4px; }
        .session-id { font-size: 11px; font-weight: 700; color: var(--cyan-mid); }
        
        .summary-body { padding: 32px; display: flex; flex-direction: column; gap: 32px; }
        .ai-summary-card { display: flex; gap: 24px; align-items: flex-start; }
        .icon-wrap { width: 64px; height: 64px; background: var(--cyan-glow); border-radius: 16px; display: flex; align-items: center; justify-content: center; color: var(--cyan-bright); }
        .summary-text h3 { font-size: 12px; color: var(--text-tertiary); font-weight: 800; margin-bottom: 8px; letter-spacing: 0.1em; }
        .summary-text p { font-size: 16px; color: var(--text-secondary); line-height: 1.6; font-weight: 500; }
        
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
        .stat-box {
          background-color: var(--bg-raised);
          padding: 20px 16px;
          border-radius: var(--radius-md);
          text-align: center;
          border: 1px solid var(--border-normal);
        }
        .stat-box .label { font-size: 10px; font-weight: 700; color: var(--text-tertiary); margin-bottom: 8px; letter-spacing: 0.05em; }
        .stat-box .value { font-size: 20px; font-weight: 800; color: var(--text-primary); }
        
        .modal-footer {
          padding: 24px 32px;
          background-color: var(--bg-raised);
          border-top: 1px solid var(--border-normal);
          display: flex;
          justify-content: flex-end;
          gap: 16px;
        }
        .modal-btn {
          padding: 12px 24px;
          border-radius: var(--radius-md);
          font-family: var(--font-display);
          font-weight: 800;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 10px;
          transition: all 0.2s;
        }
        .modal-btn.primary { background-color: var(--cyan-bright); color: white; border: none; box-shadow: 0 4px 12px var(--cyan-glow); }
        .modal-btn.secondary { background: white; border: 1px solid var(--border-normal); color: var(--text-secondary); }
        .modal-btn:hover { transform: translateY(-2px); opacity: 0.9; }
      `}} />
    </div>
  );
}

