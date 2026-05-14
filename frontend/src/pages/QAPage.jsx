import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot, Tag, Search } from 'lucide-react';

export const QAPage = ({ allFrames }) => {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'DSAA ANALYST ONLINE. I have analyzed current session history. How can I assist you with the surveillance data?', timestamp: new Date().toISOString() }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const quickQuestions = [
    "How many vehicles today?",
    "Any midnight incidents?",
    "Show critical alerts",
    "What objects at main gate?",
    "Session summary"
  ];

  const handleSend = async (text) => {
    if (!text.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', text, timestamp: new Date().toISOString() }]);
    setInput('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text })
      });
      
      if (response.ok) {
        const data = await response.json();
        setMessages(prev => [...prev, { 
          role: 'ai', 
          text: data.answer, 
          sources: data.sources, 
          timestamp: new Date().toISOString() 
        }]);
      } else {
        throw new Error('QA backend failed');
      }
    } catch (err) {
      console.error('QA Error:', err);
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: "I'm having trouble connecting to the intelligence engine. Please ensure the backend is running.", 
        timestamp: new Date().toISOString() 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="qa-page page-enter">
      <div className="qa-container">
        <div className="qa-header">
           <div className="header-info">
             <h1 className="font-display">AI ANALYST Q&A</h1>
             <p className="subtitle mono">Powered by qwen3:8b + ChromaDB</p>
           </div>
        </div>

        <div className="chat-area" ref={scrollRef}>
          {messages.map((msg, i) => (
            <div key={i} className={`message-row ${msg.role}`}>
              <div className="message-icon">
                {msg.role === 'ai' ? <Bot size={16} /> : <User size={16} />}
              </div>
              <div className="message-bubble">
                {msg.role === 'ai' && <div className="ai-name font-display">DSAA ANALYST</div>}
                <div className="message-text">{msg.text}</div>
                {msg.sources && msg.sources.length > 0 && (
                   <div className="sources-row">
                     <span className="mono">Sources:</span>
                     {msg.sources.map(s => <span key={s} className="source-chip mono">{s}</span>)}
                   </div>
                )}
                <div className="message-time mono">{new Date(msg.timestamp).toLocaleTimeString()}</div>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message-row ai">
              <div className="message-icon"><Bot size={16} /></div>
              <div className="message-bubble typing">
                <div className="dot"></div>
                <div className="dot"></div>
                <div className="dot"></div>
              </div>
            </div>
          )}
        </div>

        <div className="qa-footer">
          <div className="quick-questions">
            {quickQuestions.map(q => (
              <button key={q} onClick={() => handleSend(q)}>{q}</button>
            ))}
          </div>
          <div className="input-area">
            <input 
              type="text" 
              placeholder="Query the surveillance history..." 
              value={input}
              onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
              onChange={(e) => setInput(e.target.value)}
              disabled={isTyping}
            />
            <button className="send-btn" onClick={() => handleSend(input)} disabled={isTyping || !input.trim()}>
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>

      <style dangerouslySetInnerHTML={{ __html: `
        .qa-page {
          height: 100%;
          padding: 40px;
          display: flex;
          justify-content: center;
          align-items: center;
          background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
        }
        .qa-container {
          width: 100%;
          max-width: 1000px;
          height: 100%;
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-lg);
          display: flex;
          flex-direction: column;
          overflow: hidden;
          box-shadow: var(--shadow-lg);
        }
        .qa-header {
           padding: 24px 32px;
           border-bottom: 1px solid var(--border-normal);
           background-color: var(--bg-surface);
        }
        .qa-header h1 { font-size: 20px; font-weight: 800; color: var(--text-primary); margin-bottom: 4px; }
        .qa-header .subtitle { font-size: 11px; color: var(--cyan-mid); font-weight: 700; letter-spacing: 0.05em; }

        .chat-area {
          flex: 1;
          padding: 32px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 24px;
          background-color: var(--bg-base);
        }
        .message-row { display: flex; gap: 16px; max-width: 85%; }
        .message-row.user { align-self: flex-end; flex-direction: row-reverse; }
        .message-icon {
          width: 36px;
          height: 36px;
          background-color: var(--bg-surface);
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: var(--cyan-bright);
          flex-shrink: 0;
          border: 1px solid var(--border-normal);
          box-shadow: var(--shadow-sm);
        }
        .message-bubble {
          padding: 20px;
          border-radius: 16px;
          position: relative;
          font-size: 15px;
          line-height: 1.6;
          box-shadow: var(--shadow-sm);
        }
        .ai .message-bubble {
          background-color: var(--bg-surface);
          border: 1px solid var(--border-normal);
          color: var(--text-primary);
          border-bottom-left-radius: 4px;
        }
        .user .message-bubble {
          background-color: var(--cyan-bright);
          color: white;
          border-bottom-right-radius: 4px;
        }
        .ai-name { font-size: 10px; font-weight: 800; color: var(--cyan-mid); margin-bottom: 8px; letter-spacing: 0.1em; }
        .message-time { font-size: 9px; color: var(--text-tertiary); margin-top: 12px; font-weight: 600; }
        
        .sources-row {
          margin-top: 16px;
          padding-top: 16px;
          border-top: 1px solid var(--border-subtle);
          display: flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 10px;
        }
        .sources-row span { font-size: 11px; color: var(--text-tertiary); font-weight: 700; }
        .source-chip {
           background-color: var(--bg-raised);
           padding: 4px 10px;
           border-radius: 20px;
           color: var(--cyan-mid) !important;
           border: 1px solid var(--border-normal);
        }
        
        .typing { display: flex; gap: 6px; padding: 16px 20px; background-color: var(--bg-surface); border-radius: 16px; width: fit-content; }
        .dot {
          width: 8px;
          height: 8px;
          background-color: var(--cyan-dim);
          border-radius: 50%;
          animation: dot-bounce 1.4s infinite;
        }
        .dot:nth-child(2) { animation-delay: 0.2s; }
        .dot:nth-child(3) { animation-delay: 0.4s; }
        
        .qa-footer { padding: 24px 32px; background-color: var(--bg-surface); border-top: 1px solid var(--border-normal); }
        .quick-questions { display: flex; gap: 12px; overflow-x: auto; margin-bottom: 20px; padding-bottom: 4px; scrollbar-width: none; }
        .quick-questions::-webkit-scrollbar { display: none; }
        .quick-questions button {
          background-color: var(--bg-raised);
          border: 1px solid var(--border-normal);
          color: var(--text-secondary);
          padding: 8px 18px;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 600;
          white-space: nowrap;
          cursor: pointer;
          transition: all 0.2s;
        }
        .quick-questions button:hover { border-color: var(--cyan-bright); color: var(--cyan-bright); background-color: var(--cyan-glow); }
        
        .input-area { display: flex; gap: 16px; }
        .input-area input {
          flex: 1;
          background-color: var(--bg-base);
          border: 1px solid var(--border-normal);
          border-radius: var(--radius-md);
          padding: 0 24px;
          color: var(--text-primary);
          height: 56px;
          font-size: 15px;
          font-weight: 500;
          box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
        }
        .input-area input:focus { outline: none; border-color: var(--cyan-bright); box-shadow: 0 0 0 4px var(--cyan-glow); }
        .send-btn {
          width: 56px;
          height: 56px;
          background-color: var(--cyan-bright);
          border: none;
          border-radius: var(--radius-md);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 12px var(--cyan-glow);
          transition: all 0.2s;
        }
        .send-btn:hover:not(:disabled) { transform: translateY(-2px); box-shadow: 0 6px 16px var(--cyan-glow); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
      `}} />
    </div>
  );
};
