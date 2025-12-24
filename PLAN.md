# PLAN DE ARQUITECTURA: OMNI-CHANNEL DEV ORCHESTRATOR

## 1. VISIÓN GENERAL
Sistema modular de orquestación de desarrollo de software automatizado con supervisión humana (HITL). Permite la gestión centralizada de tareas de desarrollo recibidas desde múltiples canales (Web, WhatsApp) ejecutadas por agentes de IA dentro de un entorno controlado (Antigravity).

## 2. ESTRUCTURA DEL MONOREPOSITORIO
El proyecto seguirá una estructura de monorepositorio estricta para mantener la separación de responsabilidades:

```text
/ (root)
├── backend/                # Ingestion Gateway (Python/FastAPI)
│   ├── app/
│   │   ├── api/            # Endpoints REST, Auth y WebSockets
│   │   ├── core/           # Configuración, Seguridad (JWT, Hashing)
│   │   ├── db/             # Base de Datos (SQLAlchemy Async)
│   │   ├── models/         # Modelos ORM (User, Task, Artifact, Message)
│   │   └── schemas/        # Schemas Pydantic (Validación)
│   ├── alembic/            # Migraciones de BD
│   └── ...
│
├── mcp-server/             # The Bridge (MCP Server Personalizado)
│   ├── src/
│   │   ├── server.py       # Entrada del servidor MCP (Tools: claim, submit)
│   │   └── ...
│
├── frontend/               # Portal de Revisión (Next.js)
│   ├── src/
│   │   ├── app/            # App Router (Login, Register, Tasks)
│   │   ├── components/     # UI Atómica y AuthGuard
│   │   ├── hooks/          # useAuth (Zustand), useTaskWebSocket
│   │   └── lib/            # api.ts (fetchWithAuth)
│   └── ...
│
├── scripts/                # Scripts de utilidad (Seed, Tests, Inject)
├── PLAN.md                 # Arquitectura y Diseño (Este archivo)
└── STEPS.md                # Pasos de implementación
```

## 3. ARQUITECTURA DE DATOS (PostgreSQL)

### Diagrama ER Simplificado

#### `users`
Tabla central de identidad y control de acceso.
*   `id` (Integer, PK): Identificador único.
*   `email` (String, UQ): Correo electrónico (identificador principal).
*   `username` (String, UQ): Nombre de usuario/display name.
*   `full_name` (String): Nombre completo del operador.
*   `hashed_password` (String, Nullable): Hash para login interno.
*   `google_id` (String, Nullable): ID único de Google para SSO.
*   `role` (Enum): 'admin', 'supervisor', 'agent'.
*   `is_active` (Boolean): Estado de la cuenta.
*   `created_at` (DateTime): Timestamp de creación.

#### `tasks`
La unidad central de trabajo.
*   `id` (Integer, PK).
*   `title` (String): Título corto de la tarea.
*   `description` (Text): Descripción completa / Prompt inicial.
*   `status` (Enum): 'pending', 'claimed', 'in_progress', 'review_pending', 'approved', 'rejected', 'done'.
*   `source` (Enum): 'whatsapp', 'web_chat', 'form'.
*   `created_by` (String): Identificador del solicitante externo.
*   `assigned_to` (Integer, FK -> users.id): Agente o humano asignado.
*   `created_at` (DateTime).

#### `messages`
*   `id` (Integer, PK).
*   `task_id` (Integer, FK -> tasks.id).
*   `sender_type` (Enum): 'user', 'system', 'agent', 'supervisor'.
*   `content` (Text).
*   `timestamp` (DateTime).

#### `artifacts`
Resultados generados por el agente para revisión.
*   `id` (Integer, PK).
*   `task_id` (Integer, FK -> tasks.id).
*   `type` (Enum): 'code', 'text', 'screenshot', 'diff'.
*   `content` (Text): Snippet de código o referencia.
*   `status` (Enum): 'pending', 'approved', 'rejected'.

## 4. COMPONENTES Y RESPONSABILIDADES

### A. Backend (Ingestion & Intelligence Gateway)
*   **Tech Stack**: Python 3.11, FastAPI, SQLAlchemy (Async), Alembic.
*   **Seguridad**: Hashing con Passlib (bcrypt), Tokens con Jose (JWT).
*   **Funciones**:
    *   Ingesta de Webhooks (WhatsApp/Twilio).
    *   **Módulo Auth**: Registro local, Login local (OAuth2 password flow), Login Google.
    *   **Control de Acceso**: Dependencia `get_current_user` protegiendo Endpoints.
    *   WebSockets para propagación de estado REACTIVE.

### B. MCP Server (The Bridge)
*   **Tech Stack**: Python, MCP SDK.
*   **Interfaz MCP**:
    *   **Resource**: `orchestrator://queue` (Lectura de cola).
    *   **Tool**: `claim_ticket(task_id)` / `submit_artifact(task_id, content, type)`.
    *   **Tool**: `send_message(task_id, text)`.

### C. Frontend (Supervisor Portal)
*   **Tech Stack**: Next.js 14, TailwindCSS v4, Zustand, Framer Motion.
*   **Funciones**:
    *   Auth Guard global: Redirección automática a `/login`.
    *   Pantalllas de registro y login social.
    *   Dashboard interactivo con actualización automática via WebSockets.

## 5. FLUJO DE SEGURIDAD (HITL-Safe)
1.  **Entrada**: Se crea una tarea vía Webhook. No requiere auth (Origen confiable/API Key).
2.  **Claim**: Un agente intenta tomar la tarea vía MCP. Requiere conexión DB confiable o Auth Token (futuro).
3.  **Review**: El supervisor entra al portal. Debe loguearse (Interno o Google).
4.  **Action**: Solo solicitudes autenticadas (JWT en Header) pueden aprobar/rechazar artefactos.
