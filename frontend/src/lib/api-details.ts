import { Task, Message, Artifact } from "@/types";
import { MOCK_TASKS } from "./api";

// ... existing MOCK_TASKS ...

const MOCK_MESSAGES: Message[] = [
    { id: 1, task_id: 1, sender_type: 'user', content: 'Hola, necesito la landing page.', timestamp: new Date(Date.now() - 3600000).toISOString() },
    { id: 2, task_id: 1, sender_type: 'agent', content: 'Entendido. ¿Tienes referencias de diseño?', timestamp: new Date(Date.now() - 3500000).toISOString() },
    { id: 3, task_id: 1, sender_type: 'user', content: 'Algo estilo Apple, muy minimalista.', timestamp: new Date(Date.now() - 3400000).toISOString() }
];

const MOCK_ARTIFACTS: Artifact[] = [
    {
        id: 1,
        task_id: 1,
        type: 'code',
        content: '// Code for Hero Section\nexport function Hero() {\n  return <h1>Welcome to Osiris</h1>;\n}',
        status: 'pending',
        created_at: new Date().toISOString()
    }
];

export async function fetchTaskDetails(id: number): Promise<{ task: Task, messages: Message[], artifacts: Artifact[] } | null> {
    // Mock fetch
    const task = MOCK_TASKS.find(t => t.id === id);
    if (!task) return null;

    return new Promise((resolve) => {
        setTimeout(() => resolve({
            task,
            messages: MOCK_MESSAGES.filter(m => m.task_id === 1), // Return mocks for demo
            artifacts: MOCK_ARTIFACTS.filter(a => a.task_id === 1)
        }), 500);
    });
}
