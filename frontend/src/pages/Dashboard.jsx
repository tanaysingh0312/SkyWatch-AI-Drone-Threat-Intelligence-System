import React from 'react';
import { LiveFeed } from '../components/live/LiveFeed';
import { TelemetryCard } from '../components/telemetry/TelemetryCard';
import { MiniMap } from '../components/telemetry/MiniMap';
import { AlertPanel } from '../components/alerts/AlertPanel';

export const Dashboard = ({ currentFrame, telemetry, allFrames, sessionActive, processing, alerts, unacknowledgedCount, alertDispatch }) => {
  return (
    <div className="dashboard-page page-enter">
      <div className="dashboard-main">
        <div className="dashboard-center">
          <LiveFeed frame={currentFrame} processing={processing} />
          
          <div className="dashboard-bottom-row">
            <div className="telemetry-section">
              <h3 className="section-label font-display">DRONE_TELEMETRY_STREAM // UAV-7A</h3>
              <TelemetryCard telemetry={telemetry} />
            </div>
            <div className="map-section">
              <h3 className="section-label font-display">SECTOR_MAP // TACTICAL</h3>
              <MiniMap telemetry={telemetry} />
            </div>
          </div>
        </div>

        <AlertPanel 
          alerts={alerts} 
          unacknowledgedCount={unacknowledgedCount} 
          dispatch={alertDispatch}
          currentThreat={currentFrame?.threat_level || 'NONE'}
        />
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .dashboard-page {
          height: 100%;
          width: 100%;
          display: flex;
          flex-direction: column;
        }
        .dashboard-main {
          display: flex;
          flex: 1;
          overflow: hidden;
        }
        .dashboard-center {
          flex: 1;
          padding: 32px;
          display: flex;
          flex-direction: column;
          gap: 32px;
          overflow-y: auto;
          background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
        }
        .dashboard-bottom-row {
          display: flex;
          gap: 32px;
        }
        .telemetry-section {
          flex: 2;
        }
        .map-section {
          flex: 1;
        }
        .section-label {
          font-size: 13px;
          font-weight: 800;
          color: var(--text-tertiary);
          margin-bottom: 16px;
          padding-left: 8px;
          border-left: 3px solid var(--cyan-bright);
          letter-spacing: 0.1em;
        }
      `}} />
    </div>
  );
};
