"use client";

import { useAuth } from "@/hooks/useAuth";
import { LogOut, User, Shield } from "lucide-react";

export default function NavigationHeader() {
    const { logout, user } = useAuth();

    return (
        <header className="mb-10 border-b border-white/10 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
                <h1 className="text-4xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 to-purple-600 bg-clip-text text-transparent">
                    OSIRIS
                </h1>
                <p className="text-muted-foreground mt-2 flex items-center gap-2">
                    Omni-Channel Dev Orchestrator
                    <span className="bg-blue-500/10 text-blue-400 text-xs px-2 py-0.5 rounded-full border border-blue-500/20 flex items-center gap-1">
                        <Shield size={10} /> HITL Secure
                    </span>
                </p>
            </div>

            <div className="flex items-center gap-4">
                {user && (
                    <div className="hidden md:flex flex-col items-end">
                        <span className="text-sm font-medium text-white">{user.full_name || 'Admin User'}</span>
                        <span className="text-xs text-gray-400 flex items-center gap-1">
                            <User size={10} /> {user.email}
                        </span>
                    </div>
                )}
                <button
                    onClick={logout}
                    className="flex items-center gap-2 bg-white/5 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/50 text-gray-300 px-4 py-2 rounded-lg transition-all font-medium border border-white/10"
                    title="Cerrar Sesión de Osiris"
                >
                    <LogOut size={18} />
                    <span className="hidden md:inline">Salir</span>
                </button>
            </div>
        </header>
    );
}
