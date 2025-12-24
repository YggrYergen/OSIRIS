"use client";

import { useEffect, useRef, useState } from 'react';

type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export function useTaskWebSocket(taskId: number) {
    const [status, setStatus] = useState<WebSocketStatus>('disconnected');
    const [lastMessage, setLastMessage] = useState<any>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        // In a real env, this URL should come from env vars
        // e.g. process.env.NEXT_PUBLIC_WS_URL
        const wsUrl = `ws://localhost:8000/api/v1/ws/tasks/${taskId}`;

        // Avoid connecting if already connected or if server is known down (mock mode)
        // For demo purposes, we try to connect
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        setStatus('connecting');

        ws.onopen = () => {
            setStatus('connected');
            console.log(`WS Connected to task ${taskId}`);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                setLastMessage(data);
            } catch (e) {
                console.error("Failed to parse WS message", e);
            }
        };

        ws.onclose = () => {
            setStatus('disconnected');
        };

        ws.onerror = (e) => {
            setStatus('error');
            // console.error("WS Error", e); // Silence in demo to avoid console spam if server down
        };

        return () => {
            ws.close();
        };
    }, [taskId]);

    return { status, lastMessage };
}
