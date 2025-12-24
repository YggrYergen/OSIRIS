import { Task, TaskStatus } from "@/types";

// Mock data for development when backend is offline
export const MOCK_TASKS: Task[] = [
    {
        id: 1,
        title: "Crear Landing Page Osiris",
        description: "Necesito una landing page moderna para el proyecto Osiris. Debe tener Hero, Features y Contacto.",
        status: "pending",
        source: "whatsapp",
        created_at: new Date().toISOString(),
        created_by: "+5491155556666"
    },
    {
        id: 2,
        title: "Fix Login Bug",
        description: "El login falla cuando el usuario tiene caracteres especiales en el password.",
        status: "in_progress",
        source: "web_chat",
        created_at: new Date(Date.now() - 3600000).toISOString(),
        created_by: "dev_lead"
    },
    {
        id: 3,
        title: "Review Artifact #42",
        description: "Revisar la implementación del servidor MCP.",
        status: "review_pending",
        source: "web_chat",
        created_at: new Date(Date.now() - 7200000).toISOString(),
        created_by: "system"
    }
];

export async function fetchTasks(): Promise<Task[]> {
    // In a real scenario, fetch from /api/v1/tasks
    // return fetch('/api/v1/tasks').then(res => res.json());

    // Return mocks for now
    return new Promise((resolve) => {
        setTimeout(() => resolve(MOCK_TASKS), 500);
    });
}
