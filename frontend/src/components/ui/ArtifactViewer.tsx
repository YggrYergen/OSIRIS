import { Artifact } from "@/types";
import { FileCode, Image as ImageIcon, Check, X, Loader2 } from "lucide-react";

interface ArtifactViewerProps {
    artifacts: Artifact[];
    currentArtifact?: { filename: string; content: string } | null;
}

export function ArtifactViewer({ artifacts, currentArtifact }: ArtifactViewerProps) {
    const showEmpty = artifacts.length === 0 && !currentArtifact;

    if (showEmpty) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground p-10 border border-dashed border-white/10 rounded-lg">
                <FileCode className="w-10 h-10 mb-2 opacity-50" />
                <p>No hay artefactos pendientes de revisión</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Live Artifact being generated */}
            {currentArtifact && (
                <div className="border border-blue-500/30 rounded-lg overflow-hidden bg-blue-500/5 transition-all animate-in fade-in slide-in-from-bottom-5">
                    <header className="flex items-center justify-between px-4 py-3 border-b border-blue-500/20 bg-blue-500/10">
                        <div className="flex items-center gap-2">
                            <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />
                            <span className="font-mono text-xs text-blue-200">Writing: {currentArtifact.filename}</span>
                        </div>
                    </header>
                    <div className="p-0 overflow-x-auto">
                        <pre className="p-4 text-sm font-mono text-blue-100 bg-black/50">
                            <code>{currentArtifact.content}</code>
                        </pre>
                    </div>
                </div>
            )}

            {/* Historical Artifacts */}
            {artifacts.map(art => (
                <div key={art.id} className="border border-white/10 rounded-lg overflow-hidden bg-white/5">
                    <header className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/5">
                        <div className="flex items-center gap-2">
                            {art.type === 'code' ? <FileCode className="w-4 h-4 text-blue-400" /> : <ImageIcon className="w-4 h-4 text-purple-400" />}
                            <span className="font-mono text-xs text-gray-400">ID: {art.id} • {art.type.toUpperCase()}</span>
                        </div>
                        <div className="flex gap-2">
                            <button className="flex items-center gap-1 px-3 py-1 rounded bg-green-500/10 text-green-500 hover:bg-green-500/20 text-xs transition-colors">
                                <Check className="w-3 h-3" /> Aprobar
                            </button>
                            <button className="flex items-center gap-1 px-3 py-1 rounded bg-red-500/10 text-red-500 hover:bg-red-500/20 text-xs transition-colors">
                                <X className="w-3 h-3" /> Rechazar
                            </button>
                        </div>
                    </header>

                    <div className="p-0 overflow-x-auto">
                        {art.type === 'code' ? (
                            <pre className="p-4 text-sm font-mono text-gray-300 bg-black/50">
                                <code>{art.content}</code>
                            </pre>
                        ) : (
                            <div className="p-4">
                                <p className="text-sm text-gray-400 italic">Previsualización de imagen no disponible.</p>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
}
