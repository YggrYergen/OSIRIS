import { Task, Message, Artifact } from "@/types";
import { fetchWithAuth } from "./api";

export async function fetchTaskDetails(id: number): Promise<{ task: Task, messages: Message[] | null, artifacts: Artifact[] } | null> {
    try {
        console.log(`Fetching details for task ${id}...`);

        // 1. Fetch Task Info
        const task = await fetchWithAuth(`/tasks/${id}`);

        // 2. Fetch Messages
        // We catch errors here to avoid blocking the whole page if messages fail
        let messages: Message[] | null = null;
        try {
            messages = await fetchWithAuth(`/messages/${id}`);
        } catch (msgError) {
            console.warn("Could not fetch messages:", msgError);
            messages = null; // Mark as failed
        }

        // 3. Artifacts (Placeholder for now)
        const artifacts: Artifact[] = [];

        return {
            task,
            messages: Array.isArray(messages) ? messages : null,
            artifacts
        };
    } catch (error) {
        console.error("Error fetching task details:", error);
        return null;
    }
}
