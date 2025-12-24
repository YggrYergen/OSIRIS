import { Task } from "@/types";
import { useAuth } from "@/hooks/useAuth";

const API_URL = "http://localhost:8000/api/v1";

export async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
    const token = useAuth.getState().token;

    const headers = {
        "Content-Type": "application/json",
        ...options.headers,
    } as any;

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        useAuth.getState().logout();
        window.location.href = "/login";
        throw new Error("Sesión expirada");
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Error desconocido" }));
        throw new Error(error.detail || "Error en la petición");
    }

    return response.json();
}

export async function fetchTasks(): Promise<Task[]> {
    try {
        return await fetchWithAuth("/tasks");
    } catch (error) {
        console.error("Error fetching tasks, falling back to mocks", error);
        // Fallback for development if backend is not responding correctly
        return [];
    }
}
