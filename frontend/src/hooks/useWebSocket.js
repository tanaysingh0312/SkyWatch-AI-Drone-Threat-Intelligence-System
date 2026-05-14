import { useState, useEffect, useCallback, useRef } from 'react';
import { MOCK_SCENES } from '../data/mockScenes';

export function useWebSocket() {
  const [currentFrame, setCurrentFrame] = useState(null);
  const [allFrames, setAllFrames] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [sessionActive, setSessionActive] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [sessionId, setSessionId] = useState('OFFLINE');

  const ws = useRef(null);

  const connect = useCallback(() => {
    if (ws.current) return;

    const socket = new WebSocket('ws://localhost:8000/ws/live');

    socket.onopen = () => {
      console.log('WS Connected');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'frame_processed') {
        // Map backend fields to frontend expectations and flatten telemetry
        const mappedFrame = {
          ...data,
          ...data.telemetry,
          vlm_description: data.description,
          sky_color: data.telemetry?.time_of_day === 'night' ? '#050810' : '#87CEEB',
          objects_visual: [] 
        };
        setCurrentFrame(mappedFrame);
        setAllFrames(prev => [...prev, mappedFrame]);
        if (data.telemetry?.session_id) setSessionId(data.telemetry.session_id);
      } else if (data.event === 'session_stopped') {
        setSessionActive(false);
      }
    };

    socket.onclose = () => {
      console.log('WS Disconnected');
      setIsConnected(false);
      ws.current = null;
      // Reconnect after 3s
      setTimeout(connect, 3000);
    };

    ws.current = socket;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (ws.current) ws.current.close();
    };
  }, [connect]);

  const startSession = useCallback(async () => {
    try {
      setProcessing(true);
      const res = await fetch('http://localhost:8000/session/start', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setSessionId(data.session_id);
        setSessionActive(true);
        setAllFrames([]);
      }
    } catch (err) {
      console.error('Failed to start session:', err);
    } finally {
      setProcessing(false);
    }
  }, []);

  const stopSession = useCallback(async () => {
    try {
      await fetch('http://localhost:8000/session/stop', { method: 'POST' });
      setSessionActive(false);
    } catch (err) {
      console.error('Failed to stop session:', err);
    }
  }, []);

  return {
    currentFrame,
    allFrames,
    isConnected,
    startSession,
    stopSession, 
    sessionActive,
    processing,
    sessionId
  };
}
