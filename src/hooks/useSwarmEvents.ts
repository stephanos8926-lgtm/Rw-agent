import { useState, useEffect, useRef } from 'react';

export interface SwarmEvent {
  type: string;
  payload: any;
  timestamp: number;
}

export function useSwarmEvents(url: string) {
  const [events, setEvents] = useState<SwarmEvent[]>([]);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}${url}`;
    
    ws.current = new WebSocket(wsUrl);

    ws.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setEvents(prev => [...prev, { ...data, timestamp: Date.now() }]);
      } catch (err) {
        console.error("Failed to parse swarm event", err);
      }
    };

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [url]);

  return { events };
}
