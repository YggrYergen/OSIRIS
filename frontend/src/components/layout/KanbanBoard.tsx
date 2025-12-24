"use client";
import { useEffect, useState } from "react";
import { fetchTasks } from "@/lib/api";
import { Task } from "@/types";
import { TaskCard } from "@/components/ui/TaskCard";
import { Layers, RefreshCw } from "lucide-react";
import Link from "next/link";

export default function KanbanBoard() {
    const [tasks, setTasks] = useState<Task[]>([]);
    const [loading, setLoading] = useState(true);

    const loadData = async () => {
        setLoading(true);
        const data = await fetchTasks();
        setTasks(data);
        setLoading(false);
    };

    useEffect(() => {
        loadData();
    }, []);

    return (
        <div className="flex flex-col h-full">
            <header className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                    <Layers className="text-blue-500" /> Task Queue
                </h2>
                <button
                    onClick={loadData}
                    className="p-2 hover:bg-white/10 rounded-full transition-colors"
                >
                    <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {tasks.map(task => (
                    <Link key={task.id} href={`/tasks/${task.id}`}>
                        <TaskCard task={task} />
                    </Link>
                ))}
            </div>

            {tasks.length === 0 && !loading && (
                <div className="text-center py-20 text-gray-500">
                    No tasks found.
                </div>
            )}
        </div>
    );
}
