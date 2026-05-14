import React from 'react';

export const TelemetryCard = ({ telemetry }) => {
  const cells = [
    { label: 'LOCATION', value: telemetry.location.replace('_', ' ') },
    { label: 'TIME', value: telemetry.timestamp.split('T')[1].split('.')[0] },
    { label: 'ALTITUDE', value: `${telemetry.altitude.toFixed(1)} m` },
    { label: 'HEADING', value: `${telemetry.heading}° ${getHeadingLabel(telemetry.heading)}` },
    { label: 'GPS', value: `${telemetry.lat.toFixed(4)}, ${telemetry.lon.toFixed(4)}` },
    { label: 'BATTERY', value: `${telemetry.battery}%`, render: (
      <div className="battery-gauge">
        <div className="battery-track">
           <div className={`battery-fill ${telemetry.battery < 30 ? 'low' : ''}`} style={{ width: `${telemetry.battery}%` }}></div>
        </div>
        <span className="mono">{telemetry.battery}%</span>
      </div>
    )}
  ];

  function getHeadingLabel(deg) {
    if (deg >= 337.5 || deg < 22.5) return 'N';
    if (deg >= 22.5 && deg < 67.5) return 'NE';
    if (deg >= 67.5 && deg < 112.5) return 'E';
    if (deg >= 112.5 && deg < 157.5) return 'SE';
    if (deg >= 157.5 && deg < 202.5) return 'S';
    if (deg >= 202.5 && deg < 247.5) return 'SW';
    if (deg >= 247.5 && deg < 292.5) return 'W';
    if (deg >= 292.5 && deg < 337.5) return 'NW';
    return '';
  }

  return (
    <div className="telemetry-card">
      <div className="telemetry-grid">
        {cells.map((cell, i) => (
          <div key={i} className="telemetry-cell">
            <span className="cell-label font-display">{cell.label}</span>
            {cell.render ? cell.render : <span className="cell-value mono">{cell.value}</span>}
          </div>
        ))}
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .telemetry-card {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-md);
          overflow: hidden;
        }
        .telemetry-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          grid-template-rows: auto auto auto;
        }
        .telemetry-cell {
          padding: 12px 16px;
          border: 0.5px solid var(--border-subtle);
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .cell-label {
          font-size: 10px;
          color: var(--text-tertiary);
          text-transform: uppercase;
        }
        .cell-value {
          font-size: 16px;
          color: var(--text-primary);
        }
        .battery-gauge {
          display: flex;
          align-items: center;
          gap: 10px;
        }
        .battery-track {
          flex: 1;
          height: 8px;
          background-color: var(--bg-raised);
          border-radius: 4px;
          overflow: hidden;
        }
        .battery-fill {
          height: 100%;
          background-color: var(--safe);
          transition: width 0.5s ease;
        }
        .battery-fill.low {
          background-color: var(--critical);
          animation: battery-warning 1s infinite;
        }
      `}} />
    </div>
  );
};
