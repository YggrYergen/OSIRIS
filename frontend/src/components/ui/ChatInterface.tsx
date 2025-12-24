import { Message, SenderType } from "@/types";
import { cn } from "@/lib/utils";
import { User, Bot, ShieldAlert } from "lucide-react";

interface ChatProps {
    messages: Message[];
}

const senderIcon: Record<SenderType, React.ReactNode> = {
    user: <User className="w-4 h-4" />,
    agent: <Bot className="w-4 h-4" />,
    system: <ShieldAlert className="w-4 h-4" />,
    supervisor: <User className="w-4 h-4 text-yellow-500" />,
};

export function ChatInterface({ messages }: ChatProps) {
    return (
        <div className="flex flex-col h-[600px] border border-white/10 rounded-lg bg-black/20 overflow-hidden">
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg) => {
                    const isAgent = msg.sender_type === 'agent' || msg.sender_type === 'system';
                    return (
                        <div
                            key={msg.id}
                            className={cn(
                                "flex gap-3 max-w-[80%]",
                                isAgent ? "self-start" : "self-end flex-row-reverse"
                            )}
                        >
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                isAgent ? "bg-blue-500/20 text-blue-400" : "bg-purple-500/20 text-purple-400"
                            )}>
                                {senderIcon[msg.sender_type]}
                            </div>

                            <div className={cn(
                                "p-3 rounded-lg text-sm",
                                isAgent ? "bg-white/5" : "bg-purple-500/10 border border-purple-500/20"
                            )}>
                                <p className="text-gray-200">{msg.content}</p>
                                <span className="text-[10px] text-gray-500 block mt-1 opacity-70">
                                    {new Date(msg.timestamp).toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="p-4 border-t border-white/10 bg-white/5">
                <input
                    type="text"
                    placeholder="Escribe un mensaje..."
                    className="w-full bg-transparent border border-white/20 rounded px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                />
            </div>
        </div>
    );
}
