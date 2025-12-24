export type TaskStatus = 'pending' | 'claimed' | 'in_progress' | 'review_pending' | 'approved' | 'rejected' | 'done';
export type TaskSource = 'whatsapp' | 'web_chat' | 'form';

export interface Task {
    id: number;
    title: string;
    description: string;
    status: TaskStatus;
    source: TaskSource;
    created_by?: string;
    assigned_to?: number;
    created_at?: string;
    updated_at?: string;
}

export type ArtifactType = 'code' | 'text' | 'screenshot' | 'diff';
export type ArtifactStatus = 'pending' | 'approved' | 'rejected';

export interface Artifact {
    id: number;
    task_id: number;
    type: ArtifactType;
    content: string;
    status: ArtifactStatus;
    created_at: string;
}

export type SenderType = 'user' | 'system' | 'agent' | 'supervisor';

export interface Message {
    id: number;
    task_id: number;
    sender_type: SenderType;
    content: string;
    timestamp: string;
}
