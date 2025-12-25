import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';

interface TerminalLog {
    timestamp: string;
    command: string;
    output: string;
}

interface TerminalFeedProps {
    logs: TerminalLog[];
}

export function TerminalFeed({ logs }: TerminalFeedProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    if (logs.length === 0) return null;

    return (
        <div className="mt-6 border border-white/10 rounded-lg overflow-hidden bg-black font-mono text-xs shadow-2xl">
            <header className="px-4 py-2 bg-white/5 border-b border-white/10 flex items-center gap-2 text-gray-400">
                <Terminal className="w-3 h-3" />
                <span>Agent Terminal</span>
            </header>
            <div className="p-4 max-h-60 overflow-y-auto space-y-2 text-gray-300">
                {logs.map((log, i) => (
                    <div key={i} className="flex flex-col gap-1">
                        <div className="flex gap-2 text-blue-400">
                            <span className="opacity-50">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                            <span className="font-bold">$ {log.command}</span>
                        </div>
                        <div className="pl-6 whitespace-pre-wrap opacity-80 border-l-2 border-white/10 ml-1">
                            {log.output}
                        </div>
                    </div>
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
}
