"use client";

import { useEffect, useState } from 'react';

type EventType = "task_update" | "new_message" | "artifact_update" | "terminal_log" | "system_alert" | "ping";

interface SSEEvent {
    type: EventType;
    data: any;
    timestamp: string;
}

export function useEventStream(token?: string) {
    const [lastEvent, setLastEvent] = useState<SSEEvent | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        // In real app, we might need token in URL: /api/v1/stream?token=${token}
        const url = `http://localhost:8000/api/v1/stream`;

        console.log("Connecting to SSE:", url);
        const eventSource = new EventSource(url);

        eventSource.onopen = () => {
            console.log("SSE Connected");
            setIsConnected(true);
        };

        const handleMessage = (event: MessageEvent) => {
            try {
                // We expect "data" field to contain JSON
                const parsedData = JSON.parse(event.data);

                // For named events, "event.type" is set by the server "event: name" line
                // But our backend yields "event: type" line, which browser puts in event.type
                // And "data: {}" line which goes to event.data.

                const sseEvent: SSEEvent = {
                    type: event.type as EventType || "ping",
                    data: parsedData,
                    timestamp: new Date().toISOString()
                };

                if (sseEvent.type !== 'ping') {
                    console.log("SSE Event:", sseEvent);
                    setLastEvent(sseEvent);
                }
            } catch (error) {
                console.error("Error parsing SSE data:", error);
            }
        };

        // We listen to generic "message" (if server doesn't set type) or specific types if server sets them.
        // Our backend implementation sets specific types.
        eventSource.addEventListener("task_update", handleMessage);
        eventSource.addEventListener("new_message", handleMessage);
        eventSource.addEventListener("artifact_update", handleMessage);
        eventSource.addEventListener("terminal_log", handleMessage);
        eventSource.addEventListener("system_alert", handleMessage);
        eventSource.addEventListener("ping", handleMessage);

        // Also listen to default just in case
        eventSource.onmessage = handleMessage;

        eventSource.onerror = (error) => {
            console.error("SSE Error:", error);
            // EventSource auto retries, but we update status
            setIsConnected(false);
        };

        return () => {
            eventSource.close();
        };
    }, [token]);

    return { lastEvent, isConnected };
}
