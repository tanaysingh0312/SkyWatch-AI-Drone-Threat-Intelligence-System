import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell, Legend } from 'recharts';
import { Target, AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

export const AnalyticsPage = ({ allFrames, alerts }) => {
  const threatData = allFrames.map(f => {
    try {
      const timePart = f.timestamp?.split('T')[1] || '00:00:00Z';
      const parts = timePart.split(':');
      const timeLabel = parts.length >= 3 ? `${parts[1]}:${parts[2].replace('Z', '')}` : '00:00';
      
      return {
        time: timeLabel,
        level: f.threat_level === 'CRITICAL' ? 4 : f.threat_level === 'HIGH' ? 3 : f.threat_level === 'MEDIUM' ? 2 : f.threat_level === 'LOW' ? 1 : 0,
        label: f.threat_level
      };
    } catch (e) {
      return { time: '00:00', level: 0, label: 'NONE' };
    }
  });

  const objects = allFrames.reduce((acc, f) => {
    const objList = typeof f.objects_detected === 'string' 
      ? f.objects_detected.split(',').filter(x => x.trim())
      : Array.isArray(f.objects_detected) ? f.objects_detected : [];
      
    objList.forEach(obj => {
      acc[obj] = (acc[obj] || 0) + 1;
    });
    return acc;
  }, {});

  const objectData = Object.entries(objects).map(([name, count]) => ({ name, count }));

  const alertStats = [
    { name: 'Critical', value: alerts.filter(a => a.severity === 'CRITICAL').length, color: '#ff2d55' },
    { name: 'High', value: alerts.filter(a => a.severity === 'HIGH').length, color: '#ff6b35' },
    { name: 'Medium', value: alerts.filter(a => a.severity === 'MEDIUM').length, color: '#f5a623' },
    { name: 'Low', value: alerts.filter(a => a.severity === 'LOW').length, color: '#3b82f6' }
  ].filter(a => a.value > 0);

  const stats = [
    { label: 'TOTAL FRAMES', value: allFrames.length, icon: Activity, color: 'var(--cyan-bright)' },
    { label: 'ALERTS FIRED', value: alerts.length, icon: AlertTriangle, color: 'var(--medium)' },
    { label: 'CRITICAL EVENTS', value: alertStats.find(a => a.name === 'Critical')?.value || 0, icon: Target, color: 'var(--critical)' },
    { label: 'SESSION SECURITY', value: 'OPTIMAL', icon: ShieldCheck, color: 'var(--safe)' }
  ];

  if (!allFrames || allFrames.length === 0) {
    return (
      <div className="analytics-page empty">
         <div className="empty-state-card">
            <Activity size={48} className="icon-muted" />
            <h2 className="font-display">NO ANALYTICS DATA</h2>
            <p>Start a mission to begin collecting security intelligence.</p>
         </div>
         <style>{`
           .analytics-page.empty { display: flex; align-items: center; justify-content: center; height: 100%; }
           .empty-state-card { text-align: center; color: var(--text-tertiary); display: flex; flex-direction: column; align-items: center; gap: 16px; }
           .empty-state-card h2 { color: var(--text-secondary); margin-top: 16px; }
         `}</style>
      </div>
    );
  }

  return (
    <div className="analytics-page page-enter">
      <div className="analytics-grid">
        {stats.map(s => (
          <div key={s.label} className="metric-card">
            <div className="metric-header">
               {s.icon && <s.icon size={16} style={{ color: s.color }} />}
               <span className="font-display">{s.label}</span>
            </div>
            <div className="metric-value mono" style={{ color: s.color }}>{s.value ?? 0}</div>
          </div>
        ))}

        <div className="chart-card large">
           <h3 className="font-display">THREAT TIMELINE // T-MINUS 60M</h3>
           <div className="chart-container">
             <ResponsiveContainer width="100%" height={300}>
               <LineChart data={threatData}>
                 <CartesianGrid strokeDasharray="3 3" stroke="var(--border-subtle)" vertical={false} />
                 <XAxis dataKey="time" stroke="var(--text-tertiary)" fontSize={10} />
                 <YAxis domain={[0, 4]} ticks={[0, 1, 2, 3, 4]} tickFormatter={val => ['N', 'L', 'M', 'H', 'C'][val]} stroke="var(--text-tertiary)" fontSize={10} />
                 <Tooltip 
                   contentStyle={{ backgroundColor: 'var(--bg-overlay)', border: '1px solid var(--border-normal)', borderRadius: '4px' }}
                   itemStyle={{ color: 'var(--cyan-bright)' }}
                   cursor={{ stroke: 'var(--cyan-dim)', strokeWidth: 2 }}
                 />
                 <Line 
                   type="monotone" 
                   dataKey="level" 
                   stroke="var(--cyan-bright)" 
                   strokeWidth={2} 
                   dot={{ fill: 'var(--bg-void)', stroke: 'var(--cyan-bright)', strokeWidth: 2, r: 4 }}
                   activeDot={{ r: 6, fill: 'var(--cyan-bright)' }}
                 />
               </LineChart>
             </ResponsiveContainer>
           </div>
        </div>

        <div className="chart-card">
           <h3 className="font-display">OBJECT FREQUENCY</h3>
           <div className="chart-container">
             <ResponsiveContainer width="100%" height={300}>
               <BarChart data={objectData} layout="vertical">
                 <XAxis type="number" hide />
                 <YAxis type="category" dataKey="name" stroke="var(--text-secondary)" fontSize={10} width={100} />
                 <Tooltip cursor={{ fill: 'var(--bg-raised)' }} />
                 <Bar dataKey="count" fill="var(--cyan-bright)" radius={[0, 4, 4, 0]} />
               </BarChart>
             </ResponsiveContainer>
           </div>
        </div>

        <div className="chart-card">
           <h3 className="font-display">ALERT DISTRIBUTION</h3>
           <div className="chart-container donut-container">
             <ResponsiveContainer width="100%" height={260}>
               <PieChart>
                 <Pie
                   data={alertStats}
                   cx="50%"
                   cy="50%"
                   innerRadius={60}
                   outerRadius={80}
                   paddingAngle={5}
                   dataKey="value"
                 >
                   {alertStats.map((entry, index) => (
                     <Cell key={`cell-${index}`} fill={entry.color} />
                   ))}
                 </Pie>
                 <Tooltip />
                 <Legend verticalAlign="bottom" height={36}/>
               </PieChart>
             </ResponsiveContainer>
             <div className="donut-center mono">
               <div className="label">TOTAL</div>
               <div className="value">{alerts.length}</div>
             </div>
           </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .analytics-page { padding: 32px; height: 100%; overflow-y: auto; }
        .analytics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; }
        
        .metric-card {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-md);
          padding: 20px;
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        .metric-header { display: flex; align-items: center; gap: 10px; font-size: 11px; color: var(--text-tertiary); }
        .metric-value { font-size: 28px; font-weight: 700; }
        
        .chart-card {
           grid-column: span 2;
           background-color: var(--bg-surface);
           border: 1px solid var(--border-normal);
           border-radius: var(--radius-md);
           padding: 24px;
        }
        .chart-card.large { grid-column: span 4; }
        .chart-card h3 { font-size: 14px; color: var(--text-tertiary); margin-bottom: 24px; border-left: 2px solid var(--cyan-dim); padding-left: 12px; }
        .chart-container { height: 300px; width: 100%; }
        
        .donut-container { position: relative; }
        .donut-center {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -60%);
          text-align: center;
          pointer-events: none;
        }
        .donut-center .label { font-size: 10px; color: var(--text-tertiary); }
        .donut-center .value { font-size: 24px; font-weight: 700; color: var(--text-primary); }
      `}} />
    </div>
  );
};
