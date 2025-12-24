import { Task, Message, Artifact } from "@/types";
import { fetchWithAuth } from "./api";

// Fallback Mock for Development if Backend fails/is empty
const MOCK_MESSAGES: Message[] = [];
const MOCK_ARTIFACTS: Artifact[] = [];

export async function fetchTaskDetails(id: number): Promise<{ task: Task, messages: Message[], artifacts: Artifact[] } | null> {
    try {
        console.log(`Fetching details for task ${id}...`);
        // 1. Fetch Task Info
        const task = await fetchWithAuth(`/tasks/${id}`);

        // 2. Fetch Messages/Artifacts (If endpoints exist, otherwise mock empty)
        // For now, assuming backend doesn't serve messages/artifacts yet in this endpoint
        // You might need to add specific endpoints in backend tasks.py like /tasks/{id}/messages

        return {
            task,
            messages: MOCK_MESSAGES, // Placeholder until backend connects
            artifacts: MOCK_ARTIFACTS // Placeholder until backend connects
        };
    } catch (error) {
        console.error("Error fetching task details:", error);
        return null;
    }
}
