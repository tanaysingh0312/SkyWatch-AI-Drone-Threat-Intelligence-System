import { useState, useEffect } from 'react';

export function useTelemetry(currentFrame) {
  const [telemetry, setTelemetry] = useState({
    location: 'INITIALIZING...',
    lat: 0,
    lon: 0,
    altitude: 0,
    heading: 0,
    battery: 100,
    timestamp: new Date().toISOString(),
    sessionTime: '00:00'
  });

  const [startTime] = useState(Date.now());

  useEffect(() => {
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      const mins = Math.floor(elapsed / 60).toString().padStart(2, '0');
      const secs = (elapsed % 60).toString().padStart(2, '0');
      setTelemetry(prev => ({ ...prev, sessionTime: `${mins}:${secs}`, timestamp: new Date().toISOString() }));
    }, 1000);

    return () => clearInterval(timer);
  }, [startTime]);

  useEffect(() => {
    if (currentFrame) {
      setTelemetry(prev => ({
        ...prev,
        location: currentFrame.location_label,
        lat: currentFrame.drone_lat,
        lon: currentFrame.drone_lon,
        altitude: currentFrame.altitude_m,
        heading: currentFrame.heading_deg,
        battery: currentFrame.battery_pct
      }));
    }
  }, [currentFrame]);

  return telemetry;
}
