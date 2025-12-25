import { Message, SenderType } from "@/types";
import { cn } from "@/lib/utils";
import { User, Bot, ShieldAlert } from "lucide-react";
import { useState, useRef, useEffect } from "react";

interface ChatProps {
    messages: Message[];
    onSendMessage?: (content: string) => void; // Callback to send message
}

const senderIcon: Record<SenderType, React.ReactNode> = {
    user: <User className="w-4 h-4" />,
    agent: <Bot className="w-4 h-4" />,
    system: <ShieldAlert className="w-4 h-4" />,
    supervisor: <User className="w-4 h-4 text-yellow-500" />,
};

export function ChatInterface({ messages, onSendMessage }: ChatProps) {
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom on new messages
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
        }
    }, [messages]);

    const handleSend = () => {
        if (!input.trim() || !onSendMessage) return;
        onSendMessage(input);
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-[600px] border border-white/10 rounded-lg bg-black/20 overflow-hidden">
            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 text-sm mt-10">
                        No hay mensajes aún. Escribe el primero.
                    </div>
                )}
                {messages.map((msg) => {
                    const isAgent = msg.sender_type === 'agent' || msg.sender_type === 'system';
                    return (
                        <div
                            key={msg.id || Math.random()} // Fallback key if id missing
                            className={cn(
                                "flex gap-3 max-w-[80%]",
                                isAgent ? "self-start" : "self-end flex-row-reverse"
                            )}
                        >
                            <div className={cn(
                                "w-8 h-8 rounded-full flex items-center justify-center shrink-0",
                                isAgent ? "bg-blue-500/20 text-blue-400" : "bg-purple-500/20 text-purple-400"
                            )}>
                                {senderIcon[msg.sender_type] || <User className="w-4 h-4" />}
                            </div>

                            <div className={cn(
                                "p-3 rounded-lg text-sm",
                                isAgent ? "bg-white/5" : "bg-purple-500/10 border border-purple-500/20"
                            )}>
                                <p className="text-gray-200">{msg.content}</p>
                                <span className="text-[10px] text-gray-500 block mt-1 opacity-70">
                                    {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString() : "Just now"}
                                </span>
                            </div>
                        </div>
                    );
                })}
            </div>

            <div className="p-4 border-t border-white/10 bg-white/5">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Escribe un mensaje..."
                        className="flex-1 bg-transparent border border-white/20 rounded px-4 py-2 text-sm focus:outline-none focus:border-blue-500 transition-colors"
                    />
                    <button
                        onClick={handleSend}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm transition-colors"
                    >
                        Enviar
                    </button>
                </div>
            </div>
        </div>
    );
}
