"use client";

import { useEffect, useRef, useState } from 'react';
import { Message } from '@/types';

type WebSocketStatus = 'connecting' | 'connected' | 'disconnected' | 'error';

export function useTaskWebSocket(taskId: number) {
    const [status, setStatus] = useState<WebSocketStatus>('disconnected');
    const [errorMessage, setErrorMessage] = useState<string>("");
    const [lastMessage, setLastMessage] = useState<Message | null>(null);
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        const wsUrl = `ws://localhost:8000/api/v1/ws/tasks/${taskId}`;
        console.log("Connecting WS to:", wsUrl);

        if (wsRef.current) {
            wsRef.current.close();
        }

        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;
        setStatus('connecting');
        setErrorMessage("");

        ws.onopen = () => {
            setStatus('connected');
            console.log(`WS Connected to task ${taskId}`);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'ping') return;
                setLastMessage(data);
            } catch (e) {
                console.error("Failed to parse WS message", e);
            }
        };

        ws.onclose = (event) => {
            console.log("WS Closed", event.code, event.reason);
            if (event.code !== 1000) {
                setStatus('error');
                setErrorMessage(`Closed: ${event.code}`);
            } else {
                setStatus('disconnected');
            }
        };

        ws.onerror = (e) => {
            setStatus('error');
            console.error("WS Error", e);
            setErrorMessage("Connection Error");
        };

        return () => {
            // Close connection when unmounting
            if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
                ws.close();
            }
        };
    }, [taskId]);

    const sendMessage = (content: string, senderType: 'user' | 'agent' | 'supervisor' = 'user') => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            const payload = JSON.stringify({ content, sender_type: senderType });
            wsRef.current.send(payload);
        } else {
            console.warn("WebSocket not connected");
        }
    };

    return { status, lastMessage, sendMessage, errorMessage };
}
