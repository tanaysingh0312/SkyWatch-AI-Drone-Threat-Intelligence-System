import React, { useState } from 'react';
import { Search, ChevronDown, ChevronUp, Download, Tag } from 'lucide-react';

export const EventsPage = ({ allFrames }) => {
  const [expandedId, setExpandedId] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredFrames = allFrames.filter(f => 
    f.vlm_description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    f.location_label.toLowerCase().includes(searchTerm.toLowerCase())
  ).reverse();

  const exportCSV = () => {
    const headers = ['TIME', 'LOCATION', 'THREAT', 'DESCRIPTION'];
    const rows = filteredFrames.map(f => [
      f.timestamp,
      f.location_label,
      f.threat_level,
      f.vlm_description.replace(/,/g, ';')
    ]);
    
    const csvContent = [headers, ...rows].map(e => e.join(",")).join("\n");
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'drone_events.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="events-page page-enter">
      <div className="events-header">
        <div>
          <h1 className="font-display">SECURITY EVENT LOG</h1>
          <p className="subtitle mono">TOTAL_EVENTS: {allFrames.length} // FILTER: ACTIVE</p>
        </div>
        <div className="header-actions">
           <div className="search-box">
             <Search size={14} className="icon-muted" />
             <input 
               type="text" 
               placeholder="Search by location or description..." 
               value={searchTerm}
               onChange={(e) => setSearchTerm(e.target.value)}
             />
           </div>
           <button className="export-btn" onClick={exportCSV}>
             <Download size={16} />
             <span className="font-display">CSV EXPORT</span>
           </button>
        </div>
      </div>

      <div className="events-table-container">
        <table className="events-table">
          <thead>
            <tr className="font-display">
              <th>TIME</th>
              <th>LOCATION</th>
              <th>OBJECTS</th>
              <th>THREAT</th>
              <th>AGENT SUMMARY</th>
              <th className="text-right">ACTIONS</th>
            </tr>
          </thead>
          <tbody>
            {filteredFrames.length === 0 ? (
              <tr>
                <td colSpan="6" className="empty-table mono">NO_EVENTS_RECORDED</td>
              </tr>
            ) : (
              filteredFrames.map(frame => (
                <React.Fragment key={frame.frame_id}>
                  <tr className={`event-row ${expandedId === frame.frame_id ? 'expanded' : ''}`} onClick={() => setExpandedId(expandedId === frame.frame_id ? null : frame.frame_id)}>
                    <td className="mono">{frame.timestamp?.split('T')[1]?.split('.')[0] || '00:00:00'}</td>
                    <td className="font-display">{String(frame.location_label || 'UNKNOWN').toUpperCase()}</td>
                    <td>
                      <div className="object-pills">
                        {(typeof frame.objects_detected === 'string' 
                          ? frame.objects_detected.split(',').filter(x => x.trim())
                          : Array.isArray(frame.objects_detected) ? frame.objects_detected : []
                        ).map((obj, i) => (
                          <span key={i} className="obj-pill">{obj}</span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <span className={`threat-badge ${String(frame.threat_level || 'NONE').toLowerCase()}`}>
                        {frame.threat_level || 'NONE'}
                      </span>
                    </td>
                    <td className="summary-cell">{frame.agent_summary}</td>
                    <td className="text-right">
                      {expandedId === frame.frame_id ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                    </td>
                  </tr>
                  {expandedId === frame.frame_id && (
                    <tr className="expanded-content">
                      <td colSpan="6">
                        <div className="detail-panel">
                          <div className="detail-grid">
                            <div className="detail-info">
                              <h4 className="font-display">FULL ANALYSIS</h4>
                              <p className="detail-desc">{frame.vlm_description}</p>
                              <div className="recommendation">
                                <span className="font-display label">RECOMMENDED ACTION:</span>
                                <span className="value">{frame.recommended_action}</span>
                              </div>
                            </div>
                            <div className="detail-telemetry">
                              <h4 className="font-display">TELEMETRY DATA</h4>
                              <div className="mono-grid">
                                <div>LAT: {frame.drone_lat}</div>
                                <div>LON: {frame.drone_lon}</div>
                                <div>ALT: {frame.altitude_m}m</div>
                                <div>BAT: {frame.battery_pct}%</div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))
            )}
          </tbody>
        </table>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .events-page {
          padding: 32px;
          height: 100%;
          display: flex;
          flex-direction: column;
          gap: 24px;
          overflow-y: auto;
        }
        .events-header {
           display: flex;
           justify-content: space-between;
           align-items: center;
        }
        .subtitle {
          font-size: 10px;
          color: var(--text-tertiary);
          margin-top: 4px;
        }
        .header-actions {
          display: flex;
          gap: 16px;
        }
        .search-box {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-sm);
          padding: 0 12px;
          display: flex;
          align-items: center;
          gap: 10px;
          width: 300px;
        }
        .search-box input {
          background: none;
          border: none;
          color: var(--text-primary);
          height: 36px;
          width: 100%;
          font-size: 12px;
        }
        .search-box input:focus { outline: none; }
        
        .export-btn {
          background-color: var(--cyan-bright);
          color: var(--bg-void);
          border: none;
          padding: 0 16px;
          height: 36px;
          border-radius: var(--radius-sm);
          display: flex;
          align-items: center;
          gap: 10px;
          font-weight: 700;
          cursor: pointer;
          transition: background 0.2s;
        }
        .export-btn:hover { background-color: var(--cyan-mid); }
        
        .events-table-container {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-md);
          overflow: hidden;
        }
        .events-table {
          width: 100%;
          border-collapse: collapse;
          text-align: left;
        }
        .events-table th {
          background-color: var(--bg-void);
          padding: 12px 20px;
          font-size: 11px;
          color: var(--text-tertiary);
          border-bottom: 1px solid var(--border-subtle);
        }
        .events-table td {
          padding: 14px 20px;
          font-size: 13px;
          border-bottom: 1px solid var(--border-subtle);
        }
        .event-row { cursor: pointer; transition: background 0.2s; }
        .event-row:hover { background-color: var(--bg-raised); }
        .event-row.expanded { background-color: var(--bg-raised); }
        
        .object-pills { display: flex; gap: 6px; }
        .obj-pill {
          font-size: 9px;
          padding: 2px 6px;
          background-color: var(--bg-raised);
          border: 1px solid var(--border-subtle);
          border-radius: 4px;
          color: var(--text-secondary);
        }
        
        .threat-badge {
          font-size: 10px;
          font-weight: 700;
          padding: 2px 8px;
          border-radius: 10px;
        }
        .threat-badge.critical { background-color: var(--critical-dim); color: var(--critical); }
        .threat-badge.high { background-color: var(--high-dim); color: var(--high); }
        .threat-badge.medium { background-color: var(--medium-dim); color: var(--medium); }
        .threat-badge.none { background-color: var(--safe-dim); color: var(--safe); }
        
        .summary-cell { color: var(--text-secondary); max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .text-right { text-align: right; }
        .empty-table { padding: 40px !important; text-align: center; color: var(--text-tertiary); }
        
        .detail-panel {
          padding: 24px;
          background-color: var(--bg-void);
          border-bottom: 1px solid var(--cyan-border);
        }
        .detail-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 40px; }
        .detail-panel h4 { font-size: 12px; color: var(--cyan-bright); margin-bottom: 12px; }
        .detail-desc { font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-bottom: 20px; }
        .recommendation {
          background-color: rgba(245, 166, 35, 0.1);
          padding: 12px;
          border-left: 2px solid var(--medium);
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .recommendation .label { font-size: 10px; color: var(--medium); }
        .recommendation .value { font-size: 14px; font-weight: 500; }
        
        .mono-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          font-family: var(--font-mono);
          font-size: 11px;
          color: var(--text-tertiary);
        }
      `}} />
    </div>
  );
};
