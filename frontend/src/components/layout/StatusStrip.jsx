import React from 'react';
import { Activity, Wifi, Terminal } from 'lucide-react';

export const StatusStrip = ({ isConnected, frameCount }) => {
  return (
    <div className="status-strip mono">
      <div className="strip-left">
        <div className="strip-item">
          <Activity size={12} />
          <span>FPS: 60.0</span>
        </div>
        <div className="strip-item">
          <Terminal size={12} />
          <span>BUF: 128MB</span>
        </div>
        <div className="strip-item">
          <span>{frameCount.toLocaleString()} PKTS</span>
        </div>
      </div>
      
      <div className="strip-right">
        <div className="strip-item">
          <Wifi size={12} className={isConnected ? 'icon-safe' : 'icon-danger'} />
          <span className={isConnected ? 'text-safe' : 'text-danger'}>
            {isConnected ? 'WEBSOCKET_CONNECTED' : 'DISCONNECTED'}
          </span>
        </div>
        <div className="strip-item active-tag">
          <div className="tag-dot"></div>
          <span>DATA_STREAM_ACTIVE</span>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .status-strip {
          height: 24px;
          background-color: var(--bg-void);
          border-top: 1px solid var(--border-subtle);
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 0 16px;
          font-size: 10px;
          color: var(--text-tertiary);
          position: fixed;
          bottom: 0;
          width: 100%;
          z-index: 200;
        }
        .strip-left, .strip-right {
          display: flex;
          align-items: center;
          gap: 20px;
        }
        .strip-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .icon-safe { color: var(--safe); }
        .icon-danger { color: var(--critical); }
        .text-safe { color: var(--safe); }
        .text-danger { color: var(--critical); }
        .active-tag {
          color: var(--safe);
          font-weight: 600;
        }
        .tag-dot {
          width: 6px;
          height: 6px;
          background-color: var(--safe);
          border-radius: 50%;
        }
      `}} />
    </div>
  );
};
