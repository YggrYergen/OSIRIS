"use client";
import { useEffect, useState } from "react";
import { fetchTaskDetails } from "@/lib/api-details";
import { Task, Message, Artifact } from "@/types";
import { ChatInterface } from "@/components/ui/ChatInterface";
import { ArtifactViewer } from "@/components/ui/ArtifactViewer";
import { TerminalFeed } from "@/components/ui/TerminalFeed";
import { ArrowLeft, Clock, User, Smartphone, Cpu, Play } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTaskWebSocket } from "@/hooks/useTaskWebSocket";
import { useEventStream } from "@/hooks/useEventStream";

export default function TaskDetailPage() {
    const params = useParams();
    const idStr = Array.isArray(params?.id) ? params.id[0] : params?.id;
    const taskId = idStr ? parseInt(idStr) : 1;

    // --- STATE ---
    const [data, setData] = useState<{ task: Task, messages: Message[], artifacts: Artifact[] } | null>(null);
    const [loading, setLoading] = useState(true);
    const [terminalLogs, setTerminalLogs] = useState<any[]>([]);
    const [currentArtifact, setCurrentArtifact] = useState<{ filename: string; content: string } | null>(null);
    const [brainModel, setBrainModel] = useState<'openai' | 'gemini'>('openai');

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

        if (lastEvent.type === 'new_message' && lastEvent.data.task_id === taskId) {
            const newMsg = lastEvent.data.data; // Wraps generic data
            // Deduplicate if needed, but usually distinct from WS
            setData(prev => {
                if (!prev) return null;
                // convert simple dict to Message type structure if needed
                const msgObj: Message = {
                    id: Date.now(), // Temp ID until refresh
                    task_id: taskId,
                    content: newMsg.content,
                    sender_type: newMsg.sender_type || 'agent',
                    timestamp: new Date().toISOString()
                };
                return { ...prev, messages: [...prev.messages, msgObj] };
            });
        }

        if (lastEvent.type === 'terminal_log' && lastEvent.data.task_id === taskId) {
            setTerminalLogs(prev => [...prev, {
                timestamp: lastEvent.timestamp,
                command: lastEvent.data.data.command,
                output: lastEvent.data.data.output
            }]);
        }

        if (lastEvent.type === 'artifact_update' && lastEvent.data.task_id === taskId) {
            setCurrentArtifact({
                filename: lastEvent.data.data.filename,
                content: lastEvent.data.data.content
            });
        }

    }, [lastEvent]);

    // Initial Load
    useEffect(() => {
        fetchTaskDetails(taskId).then(res => {
            setData(res);
            setLoading(false);
        });
    }, [taskId]);

    // Helper: Trigger Agent manually
    const handleRunAgent = async () => {
        try {
            await fetch(`http://localhost:8000/api/v1/agent/run/${taskId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    instruction: "Analyze this task and write a plan file.",
                    provider: brainModel
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
                        <header className="flex justify-between items-start mb-2">
                            <h1 className="text-xl font-bold text-white">{task.title}</h1>
                            <div className="flex flex-col items-end gap-1">
                                <div className="flex gap-1">
                                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${wsStatus === 'connected' ? 'text-green-400 border-green-400/30' : 'text-gray-500 border-gray-500/30'
                                        }`}>WS</span>
                                    <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${sseConnected ? 'text-blue-400 border-blue-400/30' : 'text-gray-500 border-gray-500/30'
                                        }`}>SSE</span>
                                </div>
                            </div>
                        </header>

                        <p className="text-sm text-gray-400 mb-4">{task.description}</p>

                        {/* Brain Controls */}
                        <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/10">
                            <div className="flex items-center gap-2">
                                <Cpu className="w-4 h-4 text-purple-400" />
                                <select
                                    value={brainModel}
                                    onChange={(e) => setBrainModel(e.target.value as any)}
                                    className="bg-black/50 border border-white/20 rounded text-xs px-2 py-1 focus:outline-none"
                                >
                                    <option value="openai">OpenAI (GPT-4o)</option>
                                    <option value="gemini">Google Gemini 1.5</option>
                                </select>
                            </div>
                            <button
                                onClick={handleRunAgent}
                                className="flex items-center gap-1 bg-purple-600 hover:bg-purple-500 text-white px-3 py-1 rounded text-xs transition-colors"
                            >
                                <Play className="w-3 h-3" /> Auto-Run
                            </button>
                        </div>
                    </div>

                    <div className="flex-1 min-h-0 border border-white/10 rounded-lg overflow-hidden bg-white/5 flex flex-col">
                        <ChatInterface
                            messages={messages}
                            onSendMessage={(content) => sendMessage(content, 'user')}
                        />
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
