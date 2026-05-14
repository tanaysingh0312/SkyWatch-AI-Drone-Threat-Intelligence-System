import React, { useState, useEffect } from 'react';
import { Camera, Brain, Zap } from 'lucide-react';

export const LiveFeed = ({ frame, processing }) => {
  const [displayText, setDisplayText] = useState('');
  const [textIndex, setTextIndex] = useState(0);

  useEffect(() => {
    if (frame && frame.vlm_description) {
      setDisplayText('');
      setTextIndex(0);
    }
  }, [frame]);

  useEffect(() => {
    if (frame && textIndex < frame.vlm_description.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + frame.vlm_description[textIndex]);
        setTextIndex(prev => prev + 1);
      }, 15);
      return () => clearTimeout(timeout);
    }
  }, [frame, textIndex]);

  if (!frame) return (
    <div className="live-feed-empty">
      <Camera size={48} className="icon-muted" />
      <span className="font-display">SYSTEM STANDBY</span>
    </div>
  );

  return (
    <div className="live-feed">
      <div className="frame-container">
        <div className="corner-bracket tr"></div>
        <div className="corner-bracket tl"></div>
        <div className="corner-bracket br"></div>
        <div className="corner-bracket bl"></div>
        
        <div className="scanline-overlay"></div>
        <div className="frame-scan-line"></div>

        <div className="frame-content">
           {frame.frame_b64 ? (
             <img 
               src={`data:image/png;base64,${frame.frame_b64}`} 
               alt="Drone Feed" 
               style={{ width: '100%', height: '100%', objectFit: 'cover' }}
             />
           ) : (
             <>
               <div className="ground-plane" style={{ background: frame.sky_color }}></div>
               {frame.objects_visual && frame.objects_visual.map((obj, i) => (
                 <div 
                   key={i} 
                   className="detection-box"
                   style={{ 
                     left: `${obj.x}px`, 
                     top: `${obj.y}px`, 
                     width: `${obj.width}px`, 
                     height: `${obj.height}px`,
                     borderColor: obj.color
                   }}
                 >
                   <div className="detection-label" style={{ backgroundColor: obj.color }}>
                     {obj.label}
                   </div>
                 </div>
               ))}
             </>
           )}

           <div className="overlay-top-left mono">
             {frame.timestamp.split('T')[1].split('Z')[0]}
           </div>
           <div className="overlay-top-right font-display">
             {frame.location_label.replace('_', ' ')}
           </div>
           <div className="rec-indicator">
             <div className="rec-dot"></div>
             <span className="mono">REC</span>
           </div>
           <div className="frame-id mono">
             {frame.frame_id}
           </div>
        </div>
      </div>

      <div className="vlm-description-box">
        <div className="vlm-header">
          <div className="header-left">
            <Brain size={14} className="icon-cyan" />
            <span className="font-display">AI ANALYST DESCRIPTION</span>
          </div>
          <div className="vlm-badge">LLAVA-7B</div>
        </div>
        <div className="vlm-content">
          <p className="vlm-text">{displayText}</p>
          {processing && (
            <div className="processing-overlay">
               <Zap className="spin-slow icon-cyan" size={16} />
               <span className="mono">ANALYZING_FRAME...</span>
            </div>
          )}
        </div>
        <div className="confidence-track">
           <div className="confidence-bar" style={{ width: '94%' }}></div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .live-feed {
          display: flex;
          flex-direction: column;
          gap: 20px;
        }
        .frame-container {
          width: 640px;
          height: 360px;
          background: #000;
          border-radius: var(--radius-lg);
          position: relative;
          overflow: hidden;
          box-shadow: var(--shadow-lg);
          border: 4px solid var(--bg-surface);
        }
        .corner-bracket {
          position: absolute;
          width: 24px;
          height: 24px;
          border: 2px solid var(--cyan-bright);
          z-index: 10;
        }
        .corner-bracket.tl { top: 12px; left: 12px; border-right: none; border-bottom: none; }
        .corner-bracket.tr { top: 12px; right: 12px; border-left: none; border-bottom: none; }
        .corner-bracket.bl { bottom: 12px; left: 12px; border-right: none; border-top: none; }
        .corner-bracket.br { bottom: 12px; right: 12px; border-left: none; border-top: none; }
        
        .scanline-overlay {
          position: absolute;
          inset: 0;
          background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.03) 2px, rgba(0,0,0,0.03) 4px);
          pointer-events: none;
          z-index: 5;
        }
        .frame-scan-line {
          position: absolute;
          left: 0;
          width: 100%;
          height: 2px;
          background-color: var(--cyan-bright);
          box-shadow: 0 0 12px var(--cyan-bright);
          animation: scan-sweep 4s linear infinite;
          z-index: 6;
          opacity: 0.3;
        }
        .frame-content {
          width: 100%;
          height: 100%;
          position: relative;
          transition: background 0.5s ease;
        }
        .ground-plane {
          position: absolute;
          bottom: 0;
          width: 100%;
          height: 60%;
          background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        }
        .detection-box {
          position: absolute;
          border: 2px solid;
          animation: box-draw 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
          z-index: 2;
        }
        .detection-label {
          position: absolute;
          top: -22px;
          left: -2px;
          font-family: var(--font-mono);
          font-size: 10px;
          font-weight: 700;
          color: #fff;
          padding: 2px 8px;
          white-space: nowrap;
          border-radius: 2px 2px 0 0;
        }
        .overlay-top-left {
          position: absolute;
          top: 24px;
          left: 24px;
          font-size: 13px;
          font-weight: 700;
          background: rgba(0,0,0,0.6);
          backdrop-filter: blur(4px);
          color: #fff;
          padding: 4px 10px;
          border-radius: var(--radius-sm);
        }
        .overlay-top-right {
          position: absolute;
          top: 24px;
          right: 24px;
          font-size: 14px;
          font-weight: 700;
          color: var(--cyan-bright);
          background: rgba(0,0,0,0.6);
          backdrop-filter: blur(4px);
          padding: 4px 12px;
          border-radius: var(--radius-sm);
        }
        .rec-indicator {
          position: absolute;
          top: 60px;
          right: 24px;
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 11px;
          font-weight: 800;
          background: rgba(0,0,0,0.6);
          color: #fff;
          padding: 4px 10px;
          border-radius: var(--radius-sm);
        }
        .rec-dot {
          width: 8px;
          height: 8px;
          background: #ef4444;
          border-radius: 50%;
          animation: pulse-ring 1s infinite;
        }
        .frame-id {
          position: absolute;
          bottom: 20px;
          left: 24px;
          font-size: 10px;
          font-weight: 500;
          color: rgba(255,255,255,0.6);
          background: rgba(0,0,0,0.4);
          padding: 2px 8px;
          border-radius: 10px;
        }
        
        .vlm-description-box {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          padding: 24px;
          border-radius: var(--radius-lg);
          min-height: 140px;
          position: relative;
          display: flex;
          flex-direction: column;
          box-shadow: var(--shadow-md);
        }
        .vlm-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 16px;
          align-items: center;
        }
        .header-left {
          display: flex;
          align-items: center;
          gap: 10px;
          color: var(--text-tertiary);
          font-size: 13px;
          font-weight: 700;
          letter-spacing: 0.05em;
        }
        .vlm-badge {
          background-color: var(--cyan-glow);
          font-size: 10px;
          font-weight: 800;
          padding: 4px 12px;
          border-radius: 20px;
          color: var(--cyan-mid);
          border: 1px solid var(--cyan-border);
        }
        .vlm-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          justify-content: center;
        }
        .vlm-text {
          font-size: 16px;
          line-height: 1.6;
          color: var(--text-primary);
          font-weight: 500;
        }
        .processing-overlay {
          display: flex;
          align-items: center;
          gap: 12px;
          font-size: 12px;
          font-weight: 700;
          color: var(--cyan-mid);
          margin-top: 12px;
        }
        .confidence-track {
          margin-top: 20px;
          height: 4px;
          background-color: var(--bg-raised);
          width: 100%;
          border-radius: 2px;
        }
        .confidence-bar {
          height: 100%;
          background-color: var(--cyan-bright);
          border-radius: 2px;
          transition: width 0.5s ease;
        }
        .spin-slow {
          animation: spin 3s linear infinite;
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}} />
    </div>
  );
};
