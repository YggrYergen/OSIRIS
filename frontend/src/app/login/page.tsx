"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { LogIn, Github, Mail, ShieldCheck, Bug } from "lucide-react";
import { motion } from "framer-motion";
import { useGoogleLogin } from "@react-oauth/google";

export default function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const { setAuth } = useAuth();
    const router = useRouter();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");

        try {
            console.log("Attempting login with:", email);
            const formData = new URLSearchParams();
            formData.append("username", email);
            formData.append("password", password);

            const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login/access-token", {
                method: "POST",
                headers: { "Content-Type": "application/x-www-form-urlencoded" },
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ detail: "Unknown Error" }));
                throw new Error(errData.detail || "Credenciales inválidas");
            }

            const data = await response.json();
            setAuth(data.access_token, { email, role: "admin" });
            router.push("/");
        } catch (err: any) {
            console.error("Login Fetch Error:", err);
            setError(err.message || "Error de conexión con el servidor");
        } finally {
            setLoading(false);
        }
    };

    // REAL GOOGLE LOGIN (Requires Valid Client ID)
    const googleLogin = useGoogleLogin({
        onSuccess: async (tokenResponse) => {
            setLoading(true);
            try {
                const response = await fetch(`http://127.0.0.1:8000/api/v1/auth/login/google?token_in=${tokenResponse.access_token}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" }
                });

                if (!response.ok) throw new Error("Backend rejection");

                const data = await response.json();
                setAuth(data.access_token, { email: "google-user@example.com", role: "agent" });
                router.push("/");

            } catch (err) {
                console.error(err);
                setError("Falló el inicio de sesión con Google");
            } finally {
                setLoading(false);
            }
        },
        onError: () => setError("Google Login Failed (Check Client ID)"),
    });

    // MOCK LOGIN FOR MANUAL TESTING (Bypass Client ID requirement)
    const handleMockGoogleLogin = async () => {
        setLoading(true);
        setError("");
        try {
            // Simulate network delay
            await new Promise(r => setTimeout(r, 800));

            const response = await fetch("http://127.0.0.1:8000/api/v1/auth/login/google?token_in=mock_dev_token", {
                method: "POST",
                headers: { "Content-Type": "application/json" }
            });

            if (!response.ok) throw new Error("Error al iniciar sesión con Google Mock");

            const data = await response.json();
            setAuth(data.access_token, { email: "tester@gmail.com", role: "agent", full_name: "Human Tester (Mock)" });
            router.push("/");
        } catch (err: any) {
            console.error("Mock Login Error:", err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0a0b] px-4 relative overflow-hidden">
            {/* Decorative Gradients */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-500/10 blur-[120px] rounded-full" />

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="w-full max-w-md"
            >
                <div className="bg-white/5 border border-white/10 p-8 rounded-2xl backdrop-blur-xl shadow-2xl">
                    <div className="flex flex-col items-center mb-8">
                        <div className="w-16 h-16 bg-blue-500/20 rounded-2xl flex items-center justify-center mb-4 border border-blue-500/20">
                            <ShieldCheck className="text-blue-400 w-10 h-10" />
                        </div>
                        <h1 className="text-3xl font-bold text-white mb-2">OSIRIS</h1>
                        <p className="text-gray-400 text-center">Inicie sesión para acceder al orquestador HITL</p>
                    </div>

                    <form onSubmit={handleLogin} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1.5">Email o Usuario</label>
                            <input
                                type="text"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-gray-600"
                                placeholder="admin@osiris.dev"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-300 mb-1.5">Contraseña</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all placeholder:text-gray-600"
                                placeholder="••••••••"
                                required
                            />
                        </div>

                        {error && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-red-500/10 border border-red-500/20 text-red-400 p-3 rounded-lg text-sm text-center"
                            >
                                {error}
                            </motion.div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
                        >
                            {loading ? "Verificando..." : (
                                <>
                                    <LogIn size={20} />
                                    Entrar al Sistema
                                </>
                            )}
                        </button>
                    </form>

                    <div className="relative my-8">
                        <div className="absolute inset-0 flex items-center">
                            <div className="w-full border-t border-white/5"></div>
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-[#121214] px-2 text-gray-500 font-medium">O continuar con</span>
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <button
                            onClick={() => googleLogin()}
                            disabled={loading}
                            className="bg-white/5 hover:bg-white/10 border border-white/10 text-white py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 font-medium disabled:opacity-50"
                        >
                            <Mail size={18} className="text-red-400" />
                            Google
                        </button>
                        <button className="bg-white/5 hover:bg-white/10 border border-white/10 text-white py-2.5 rounded-lg transition-all flex items-center justify-center gap-2 font-medium">
                            <Github size={18} className="text-white" />
                            GitHub
                        </button>
                    </div>

                    {/* Developer Mock Button */}
                    <div className="mt-6 flex justify-center">
                        <button
                            onClick={handleMockGoogleLogin}
                            className="text-xs text-gray-600 hover:text-blue-400 transition-colors flex items-center gap-1"
                        >
                            <Bug size={12} />
                            Dev Mode: Simular Google Login
                        </button>
                    </div>

                    <p className="mt-8 text-center text-sm text-gray-500">
                        ¿No tiene acceso?{" "}
                        <a href="/register" className="text-blue-400 hover:underline">Solicite registro</a>
                    </p>
                </div>

                <p className="mt-8 text-center text-xs text-gray-600">
                    &copy; 2025 Osiris Orchestration Division. Secure HITL Environment.
                </p>
            </motion.div>
        </div>
    );
}
