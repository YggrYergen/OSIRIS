"use client";
import { useEffect, useState } from "react";
import { fetchTaskDetails } from "@/lib/api-details";
import { Task, Message, Artifact } from "@/types";
import { ChatInterface } from "@/components/ui/ChatInterface";
import { ArtifactViewer } from "@/components/ui/ArtifactViewer";
import { ArrowLeft, Clock, User, Smartphone } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useTaskWebSocket } from "@/hooks/useTaskWebSocket";

export default function TaskDetailPage() {
    const params = useParams();
    const idStr = Array.isArray(params?.id) ? params.id[0] : params?.id;
    const taskId = idStr ? parseInt(idStr) : 1;

    // WebSocket Integration
    const { status: wsStatus, lastMessage } = useTaskWebSocket(taskId);

    // Initial Data Load
    const [data, setData] = useState<{ task: Task, messages: Message[], artifacts: Artifact[] } | null>(null);
    const [loading, setLoading] = useState(true);

    // Handle WS Messages log
    useEffect(() => {
        if (lastMessage) {
            console.log("WS Update:", lastMessage);
        }
    }, [lastMessage]);

    useEffect(() => {
        fetchTaskDetails(taskId).then(res => {
            setData(res);
            setLoading(false);
        });
    }, [taskId]);

    if (loading) return <div className="p-10 text-center">Cargando detalles...</div>;
    if (!data) return <div className="p-10 text-center text-red-400">Tarea no encontrada</div>;

    const { task, messages, artifacts } = data;

    return (
        <main className="min-h-screen bg-background text-foreground p-6">
            <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* LEFT COLUMN: Context & Chat */}
                <div className="lg:col-span-1 space-y-6">
                    <Link href="/" className="inline-flex items-center text-sm text-gray-500 hover:text-white mb-2 transition-colors">
                        <ArrowLeft className="w-4 h-4 mr-1" /> Volver al tablero
                    </Link>

                    <div className="p-6 rounded-lg bg-white/5 border border-white/10">
                        <header className="flex justify-between items-start mb-2">
                            <h1 className="text-xl font-bold text-white">{task.title}</h1>
                            <span className={`text-[10px] uppercase px-1.5 py-0.5 rounded border ${wsStatus === 'connected' ? 'text-green-400 border-green-400/30' : 'text-gray-500 border-gray-500/30'
                                }`}>
                                {wsStatus === 'connected' ? 'LIVE' : 'OFFLINE'}
                            </span>
                        </header>

                        <p className="text-sm text-gray-400 mb-4">{task.description}</p>

                        <div className="flex flex-wrap gap-2 text-xs text-gray-500 border-t border-white/5 pt-4">
                            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(task.created_at || "").toLocaleDateString()}</span>
                            <span className="flex items-center gap-1"><Smartphone className="w-3 h-3" /> {task.source}</span>
                            <span className="flex items-center gap-1"><User className="w-3 h-3" /> {task.created_by}</span>
                        </div>
                    </div>

                    <ChatInterface messages={messages} />
                </div>

                {/* RIGHT COLUMN: Workspace & Artifacts */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="flex items-center justify-between">
                        <h2 className="text-xl font-semibold">Espacio de Trabajo</h2>
                        <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                            STATUS: {task.status.toUpperCase()}
                        </span>
                    </div>

                    <ArtifactViewer artifacts={artifacts} />
                </div>

            </div>
        </main>
    );
}
