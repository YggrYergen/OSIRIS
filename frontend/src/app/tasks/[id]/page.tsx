"use client";
import { useEffect, useState } from "react";
import { fetchTaskDetails } from "@/lib/api-details";
import { Task, Message, Artifact } from "@/types";
import { ChatInterface } from "@/components/ui/ChatInterface";
import { ArtifactViewer } from "@/components/ui/ArtifactViewer";
import { TerminalFeed } from "@/components/ui/TerminalFeed";
import { ArrowLeft, Clock, User, Smartphone, Cpu, Play, RefreshCw } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTaskWebSocket } from "@/hooks/useTaskWebSocket";
import { useEventStream } from "@/hooks/useEventStream";

// Define consistent model options
const BRAIN_OPTIONS = {
    openai: [
        { id: "gpt-4o", name: "GPT-4o (Default)" },
        { id: "gpt-4-turbo", name: "GPT-4 Turbo" },
        { id: "o1-preview", name: "o1 Preview (Reasoning)" },
        { id: "o1-mini", name: "o1 Mini (Fast Reasoning)" }
    ],
    gemini: [
        { id: "gemini-1.5-pro", name: "Gemini 1.5 Pro" },
        { id: "gemini-1.5-flash", name: "Gemini 1.5 Flash" }
    ]
};

export default function TaskDetailPage() {
    const params = useParams();
    const idStr = Array.isArray(params?.id) ? params.id[0] : params?.id;
    const taskId = idStr ? parseInt(idStr) : 1;

    // --- STATE ---
    const [data, setData] = useState<{ task: Task, messages: Message[], artifacts: Artifact[] } | null>(null);
    const [loading, setLoading] = useState(true);
    const [terminalLogs, setTerminalLogs] = useState<any[]>([]);
    const [currentArtifact, setCurrentArtifact] = useState<{ filename: string; content: string } | null>(null);

    // Brain Selection State
    const [brainProvider, setBrainProvider] = useState<'openai' | 'gemini'>('openai');
    const [brainModel, setBrainModel] = useState<string>('gpt-4o');

    // Update model default when provider changes
    const handleProviderChange = (provider: 'openai' | 'gemini') => {
        setBrainProvider(provider);
        setBrainModel(BRAIN_OPTIONS[provider][0].id);
    };

    // --- WEBSOCKETS (Legacy/Chat Input) ---
    const { status: wsStatus, lastMessage, sendMessage, errorMessage } = useTaskWebSocket(taskId);

    // --- SSE (Real-time Intelligence) ---
    const { lastEvent, isConnected: sseConnected } = useEventStream();

    // Handle WS Messages (User Chat Only mostly)
    useEffect(() => {
        if (lastMessage && data) {
            setData(prev => {
                if (!prev) return null;
                if (prev.messages.some(m => m.id === lastMessage.id)) return prev;
                return { ...prev, messages: [...prev.messages, lastMessage] };
            });
        }
    }, [lastMessage]);

    // Handle SSE Events (Agent Brain)
    useEffect(() => {
        if (!lastEvent || !data) return;

        // DEBUG: Trace events
        console.log("DEBUG EVENT:", lastEvent);

        if (lastEvent.type === 'new_message' && lastEvent.data.task_id === taskId) {
            const newMsg = lastEvent.data;

            setData(prev => {
                if (!prev) return null;
                const msgObj: Message = {
                    id: Date.now(),
                    task_id: taskId,
                    content: newMsg.data?.content || newMsg.content || "Empty content?",
                    sender_type: newMsg.sender_type || 'agent',
                    timestamp: new Date().toISOString()
                };
                return { ...prev, messages: [...prev.messages, msgObj] };
            });
        }

        if (lastEvent.type === 'terminal_log' && lastEvent.data.task_id === taskId) {
            // Support both nested and flat structures
            const logData = lastEvent.data.data || lastEvent.data;

            setTerminalLogs(prev => [...prev, {
                timestamp: lastEvent.timestamp,
                command: logData.command,
                output: logData.output
            }]);
        }

        if (lastEvent.type === 'artifact_update' && lastEvent.data.task_id === taskId) {
            const artifactData = lastEvent.data.data || lastEvent.data;
            setCurrentArtifact({
                filename: artifactData.filename,
                content: artifactData.content
            });
        }

    }, [lastEvent]);

    const refreshData = () => {
        // Silent refresh is better for polling
        fetchTaskDetails(taskId).then(res => {
            if (res) {
                // CRITICAL DEBUG: Log incoming data to see why it might be skipped
                console.log("CRITICAL DEBUG: Poll Result", {
                    taskId,
                    msgCount: res.messages?.length,
                    firstMsg: res.messages?.[0],
                    allMessages: res.messages
                });

                setData(prev => {
                    if (!prev) return {
                        task: res.task,
                        messages: res.messages || [],
                        artifacts: res.artifacts
                    };

                    // SAFETY CHECK: If messages is null (fetch failed), KEEP old messages
                    if (res.messages === null) {
                        return { ...prev, task: res.task, artifacts: res.artifacts };
                    }

                    // Optimization: Only update if length changed
                    if (res.messages.length !== prev.messages.length || res.artifacts.length !== prev.artifacts.length) {
                        return {
                            task: res.task,
                            messages: res.messages,
                            artifacts: res.artifacts
                        };
                    }
                    return prev;
                });
            }
            setLoading(false);
        });
    };

    // Initial Load & Auto-Refresh (Polling as Failsafe)
    useEffect(() => {
        refreshData();
        const interval = setInterval(() => {
            refreshData();
        }, 2000); // 2 second polling

        return () => clearInterval(interval);
    }, [taskId]);

    // Helper: Trigger Agent manually
    const handleRunAgent = async () => {
        try {
            await fetch(`http://localhost:8000/api/v1/agent/run/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    instruction: "Analyze this task and write a plan file.",
                    provider: brainProvider,
                    model: brainModel
                })
            });
        } catch (e) {
            console.error("Failed to run agent", e);
        }
    };

    if (loading) return <div className="p-10 text-center">Cargando detalles...</div>;
    if (!data) return <div className="p-10 text-center text-red-400">Tarea no encontrada</div>;

    const { task, messages, artifacts } = data;

    return (
        <main className="min-h-screen bg-background text-foreground p-6">
            <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* LEFT COLUMN: Context & Chat */}
                <div className="lg:col-span-1 space-y-6 flex flex-col h-[calc(100vh-3rem)]">
                    <Link href="/" className="inline-flex items-center text-sm text-gray-500 hover:text-white mb-2 transition-colors">
                        <ArrowLeft className="w-4 h-4 mr-1" /> Volver al tablero
                    </Link>

                    <div className="p-6 rounded-lg bg-white/5 border border-white/10 shrink-0">
                        <header className="flex justify-between items-center mb-2">
                            <h1 className="text-xl font-bold text-white">{task.title}</h1>
                            <div className="flex flex-col items-end gap-1">
                                <div className="flex gap-2 items-center">
                                    <button
                                        onClick={refreshData}
                                        className="text-gray-400 hover:text-white transition-colors bg-white/10 p-1 rounded hover:bg-white/20"
                                        title="Refresh Data"
                                    >
                                        <RefreshCw className="w-3 h-3" />
                                    </button>
                                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${wsStatus === 'connected' ? 'text-green-400 border-green-400/30' : 'text-gray-500 border-gray-500/30'
                                        }`}>WS</span>
                                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${sseConnected ? 'text-blue-400 border-blue-400/30' : 'text-gray-500 border-gray-500/30'
                                        }`}>SSE</span>
                                </div>
                            </div>
                        </header>

                        <p className="text-sm text-gray-400 mb-4">{task.description}</p>

                        {/* Brain Controls */}
                        <div className="flex flex-col gap-2 mt-4 pt-4 border-t border-white/10">
                            <label className="text-xs text-gray-500 uppercase font-semibold">Brain Configuration</label>

                            <div className="flex items-center gap-2">
                                <Cpu className="w-4 h-4 text-purple-400" />
                                <select
                                    value={brainProvider}
                                    onChange={(e) => handleProviderChange(e.target.value as any)}
                                    className="bg-black/50 border border-white/20 rounded text-xs px-2 py-1 focus:outline-none flex-1"
                                >
                                    <option value="openai">OpenAI</option>
                                    <option value="gemini">Google Gemini</option>
                                </select>
                            </div>

                            <div className="flex items-center gap-2">
                                <div className="w-4 h-4" /> {/* Spacer */}
                                <select
                                    value={brainModel}
                                    onChange={(e) => setBrainModel(e.target.value)}
                                    className="bg-black/50 border border-white/20 rounded text-xs px-2 py-1 focus:outline-none flex-1 text-gray-300"
                                >
                                    {BRAIN_OPTIONS[brainProvider].map(opt => (
                                        <option key={opt.id} value={opt.id}>{opt.name}</option>
                                    ))}
                                </select>
                            </div>

                            <button
                                onClick={handleRunAgent}
                                className="mt-2 flex items-center justify-center gap-1 bg-purple-600 hover:bg-purple-500 text-white px-3 py-2 rounded text-xs transition-colors font-semibold"
                            >
                                <Play className="w-3 h-3" /> Auto-Run Agent
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 min-h-0 border border-white/10 rounded-lg overflow-hidden bg-white/5 flex flex-col">
                        <ChatInterface
                            messages={messages}
                            onSendMessage={(content) => sendMessage(content, 'user')}
                        />
                    </div>
                    {/* VISUAL DEBUG TOOL */}
                    <div className="p-2 border-t border-white/10 opacity-70 hover:opacity-100 transition-opacity">
                        <details>
                            <summary className="text-xs text-red-400 cursor-pointer font-bold">Show Raw Debug Data (Messages JSON)</summary>
                            <pre className="text-[10px] text-gray-400 overflow-auto max-h-40 mt-2 bg-black/80 p-2 rounded border border-red-900/50">
                                {JSON.stringify(messages, null, 2)}
                            </pre>
                        </details>
                    </div>
                </div>

                {/* RIGHT COLUMN: Workspace & Artifacts */}
                <div className="lg:col-span-2 space-y-6 flex flex-col h-[calc(100vh-3rem)] overflow-y-auto">
                    <div className="shrink-0 flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Espacio de Trabajo</h2>
                        <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                            STATUS: {task.status.toUpperCase()} (ID: {taskId})
                        </span>
                    </div>

                    <ArtifactViewer artifacts={artifacts} currentArtifact={currentArtifact} />

                    <TerminalFeed logs={terminalLogs} />
                </div>

            </div>
        </main>
    );
}
