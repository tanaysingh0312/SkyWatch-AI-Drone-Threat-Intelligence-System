import React from 'react';

export const MiniMap = ({ telemetry }) => {
  // Normalize lon/lat to map coords (very simplified)
  // Base at 26.8475, 75.803
  const mapX = 100 + (telemetry.lon - 75.803) * 5000;
  const mapY = 100 - (telemetry.lat - 26.8475) * 5000;

  return (
    <div className="mini-map">
      <div className="map-grid"></div>
      <div className="map-boundary"></div>
      
      <div className="marker gate" style={{ top: '150px', left: '120px' }}>
        <div className="dot"></div>
        <span className="mono">MAIN_GATE</span>
      </div>
      <div className="marker garage" style={{ top: '50px', left: '80px' }}>
        <div className="dot"></div>
        <span className="mono">GARAGE</span>
      </div>

      <div className="drone-dot" style={{ top: `${mapY}px`, left: `${mapX}px` }}>
        <div className="ping"></div>
      </div>

      <div className="map-scale mono">50m</div>

      <style dangerouslySetInnerHTML={{ __html: `
        .mini-map {
          width: 100%;
          height: 200px;
          background-color: var(--bg-void);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-md);
          position: relative;
          overflow: hidden;
        }
        .map-grid {
          position: absolute;
          inset: 0;
          background-image: linear-gradient(var(--border-subtle) 1px, transparent 1px),
                            linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
          background-size: 20px 20px;
          opacity: 0.3;
        }
        .map-boundary {
          position: absolute;
          top: 30px;
          left: 40px;
          width: 130px;
          height: 140px;
          border: 1px dashed rgba(0, 212, 255, 0.2);
        }
        .marker {
          position: absolute;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 2px;
          z-index: 2;
        }
        .marker .dot {
          width: 4px;
          height: 4px;
          background-color: var(--text-tertiary);
          border-radius: 50%;
        }
        .marker span {
          font-size: 7px;
          color: var(--text-tertiary);
        }
        .drone-dot {
          position: absolute;
          width: 6px;
          height: 6px;
          background-color: var(--cyan-bright);
          border-radius: 50%;
          z-index: 5;
          transform: translate(-50%, -50%);
          transition: all 1.5s linear;
        }
        .ping {
          position: absolute;
          inset: -4px;
          border: 1px solid var(--cyan-bright);
          border-radius: 50%;
          animation: pulse-ring 1.5s infinite;
        }
        .map-scale {
          position: absolute;
          bottom: 10px;
          right: 10px;
          font-size: 8px;
          color: var(--text-tertiary);
          border-bottom: 1px solid var(--text-tertiary);
          padding-bottom: 1px;
        }
      `}} />
    </div>
  );
};
