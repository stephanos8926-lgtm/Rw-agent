import { useState, useEffect, useRef, useCallback } from 'react';

export type MessageRole = 'user' | 'agent' | 'system' | 'tool_result' | 'tool_intent';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: Date;
  tool?: string;
}

export function useAgent(wsUrl: string = 'ws://localhost:8000/ws/agent') {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setIsConnected(true);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'system',
          content: 'Connected to Agentic OS (Debian Headless)',
          timestamp: new Date()
        }]);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setIsTyping(false);

        const newMessage: ChatMessage = {
          id: Date.now().toString() + Math.random(),
          role: data.role || data.type,
          content: data.content,
          timestamp: new Date(),
          tool: data.tool
        };

        if (data.type === 'tool_intent' || data.type === 'tool_result') {
           newMessage.role = data.type;
        } else {
           newMessage.role = data.role === 'user' ? 'user' : 'agent';
        }

        // Avoid duplicating the user's echo message if we already show it optimistically
        if (data.type === 'message' && data.role === 'user') return; 

        setMessages(prev => [...prev, newMessage]);
      };

      ws.onclose = () => {
        setIsConnected(false);
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'system',
          content: 'Disconnected from Agentic OS. Reconnecting in 5s...',
          timestamp: new Date()
        }]);
        setTimeout(connect, 5000);
      };

      ws.onerror = (err) => {
        console.error('WebSocket error:', err);
      };

      wsRef.current = ws;
    } catch (e) {
      console.error(e);
    }
  }, [wsUrl]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [connect]);

  const sendMessage = useCallback((content: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      // Optimistic UI update
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        role: 'user',
        content,
        timestamp: new Date()
      }]);
      
      setIsTyping(true);
      wsRef.current.send(JSON.stringify({ message: content }));
    }
  }, []);

  const clearHistory = () => setMessages([]);

  return { messages, isConnected, isTyping, sendMessage, clearHistory };
}
