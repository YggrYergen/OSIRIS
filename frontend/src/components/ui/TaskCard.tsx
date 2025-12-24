import { Trash2, CheckCircle, Clock, AlertCircle } from "lucide-react";
import { cn } from "@/lib/utils";
import { Task, TaskStatus } from "@/types";

interface TaskCardProps {
    task: Task;
    onClick?: (task: Task) => void;
}

const statusColor: Record<TaskStatus, string> = {
    pending: "bg-yellow-500/10 text-yellow-500 border-yellow-500/20",
    claimed: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    in_progress: "bg-blue-600/10 text-blue-600 border-blue-600/20",
    review_pending: "bg-purple-500/10 text-purple-500 border-purple-500/20",
    approved: "bg-green-500/10 text-green-500 border-green-500/20",
    rejected: "bg-red-500/10 text-red-500 border-red-500/20",
    done: "bg-gray-500/10 text-gray-500 border-gray-500/20",
};

export function TaskCard({ task, onClick }: TaskCardProps) {
    return (
        <div
            onClick={() => onClick?.(task)}
            className="group relative flex flex-col gap-3 rounded-lg border border-white/10 bg-white/5 p-4 hover:bg-white/10 hover:border-white/20 transition-all cursor-pointer"
        >
            <div className="flex justify-between items-start">
                <span className={cn("px-2 py-0.5 rounded text-xs font-medium border", statusColor[task.status])}>
                    {task.status.replace('_', ' ').toUpperCase()}
                </span>
                <span className="text-xs text-muted-foreground">
                    {new Date(task.created_at || "").toLocaleTimeString()}
                </span>
            </div>

            <div>
                <h3 className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                    {task.title || "Untitled Task"}
                </h3>
                <p className="text-sm text-gray-400 line-clamp-2 mt-1">
                    {task.description}
                </p>
            </div>

            <div className="flex items-center gap-2 text-xs text-gray-500 mt-2">
                <span className="bg-gray-800 px-1.5 py-0.5 rounded text-gray-300">
                    {task.source}
                </span>
                {task.created_by && <span>by {task.created_by}</span>}
            </div>
        </div>
    );
}
