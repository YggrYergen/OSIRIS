# PLAN DE ARQUITECTURA: OMNI-CHANNEL DEV ORCHESTRATOR

## 1. VISIÓN GENERAL
Sistema modular de orquestación de desarrollo de software automatizado con supervisión humana (HITL). Permite la gestión centralizada de tareas de desarrollo recibidas desde múltiples canales (Web, WhatsApp) ejecutadas por agentes de IA dentro de un entorno controlado (Antigravity).

## 2. ESTRUCTURA DEL MONOREPOSITORIO
El proyecto seguirá una estructura de monorepositorio estricta para mantener la separación de responsabilidades:

```text
/ (root)
├── backend/                # Ingestion Gateway (Python/FastAPI)
│   ├── app/
│   │   ├── api/            # Endpoints REST y WebSockets
│   │   ├── core/           # Configuración, Seguridad
│   │   ├── db/             # Base de Datos (SQLAlchemy)
│   │   ├── models/         # Modelos ORM
│   │   └── schemas/        # Schemas Pydantic
│   ├── alembic/            # Migraciones de BD
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── mcp-server/             # The Bridge (MCP Server Personalizado)
│   ├── src/
│   │   ├── server.py       # Entrada del servidor MCP
│   │   ├── tools.py        # Definición de Herramientas
│   │   └── resources.py    # Definición de Recursos
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/               # Portal de Revisión (Next.js)
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   └── ...
│
├── .aiexclude              # Reglas de exclusión para IA
├── PLAN.md                 # Arquitectura y Diseño (Este archivo)
└── STEPS.md                # Pasos de implementación
```

## 3. ARQUITECTURA DE DATOS (PostgreSQL)

### Diagrama ER Simplificado

#### `users`
Tabla para autenticación y roles de supervisores humanos y agentes.
*   `id` (Integer, PK): Identificador único over.
*   `username` (String, UQ): Nombre de usuario.
*   `role` (Enum): 'admin', 'supervisor', 'agent'.
*   `created_at` (DateTime): Timestamp de creación.

#### `tasks`
La unidad central de trabajo.
*   `id` (Integer, PK): Identificador único de la tarea.
*   `title` (String): Título corto de la tarea.
*   `description` (Text): Descripción completa / Prompt inicial.
*   `status` (Enum): 'pending', 'claimed', 'in_progress', 'review_pending', 'approved', 'rejected', 'done'.
*   `source` (Enum): 'whatsapp', 'web_chat', 'form'.
*   `created_by` (String): Identificador del solicitante externo.
*   `assigned_to` (Integer, FK -> users.id): Agente o humano asignado.
*   `created_at` (DateTime): Fecha de ingreso.
*   `updated_at` (DateTime): Última actualización.

#### `messages`
Registro de conversación para contexto y comunicación.
*   `id` (Integer, PK).
*   `task_id` (Integer, FK -> tasks.id).
*   `sender_type` (Enum): 'user', 'system', 'agent', 'supervisor'.
*   `content` (Text): Contenido del mensaje.
*   `timestamp` (DateTime).

#### `artifacts`
Resultados generados por el agente para revisión.
*   `id` (Integer, PK).
*   `task_id` (Integer, FK -> tasks.id).
*   `type` (Enum): 'code', 'text', 'screenshot', 'diff'.
*   `content` (Text): Contenido del artefacto o path relativo.
*   `status` (Enum): 'pending', 'approved', 'rejected'.
*   `created_at` (DateTime).

## 4. COMPONENTES Y RESPONSABILIDADES

### A. Backend (Ingestion Gateway)
*   **Tech Stack**: Python 3.10+, FastAPI, SQLAlchemy (Async), Alembic, Uvicorn.
*   **Funciones**:
    *   Recibir Webhooks de fuentes externas.
    *   Mantener el estado real de la base de datos.
    *   Exponer API REST para el Frontend.
    *   Manejar WebSockets para actualizaciones en tiempo real al Frontend.

### B. MCP Server (The Bridge)
*   **Tech Stack**: Python, `mcp` SDK (o `fastmcp`).
*   **Funciones**: Conectar al Agente de IA con la Base de Datos del Backend.
*   **Interfaz MCP**:
    *   **Resource**: `orchestrator://queue`
        *   Devuelve un JSON con la lista de tareas con status='pending'.
    *   **Tool**: `claim_ticket(task_id: int)`
        *   Cambia status a 'claimed' y asigna al agente.
    *   **Tool**: `submit_artifact(task_id: int, content: str, type: str)`
        *   Crea un registro en `artifacts` y cambia tarea a 'review_pending'.
    *   **Tool**: `send_message(task_id: int, text: str)`
        *   Inserta un mensaje en `messages` para que lo vea el humano o se reenvíe al origen.

### C. Frontend (Review Portal)
*   **Tech Stack**: Next.js 14, TailwindCSS, Shadcn/UI (opcional), Lucide Icons.
*   **Funciones**:
    *   Dashboard tipo Kanban o Lista para ver tickets.
    *   Vista detallada de ticket con chat en vivo.
    *   Interfaz de Diff/Visualización de Artefactos para Aprobar/Rechazar.

## 5. FLUJO DE TRABAJO (Happy Path)
1.  **Ingesta**: Llega un request via WhatsApp -> Backend crea `Task` (status='pending').
2.  **Notificación**: Backend emite evento WS al Frontend (opcional) y actualiza DB.
3.  **Observación**: Agente consulta recurso `orchestrator://queue` via MCP.
4.  **Asignación**: Agente usa tool `claim_ticket(id)`.
5.  **Ejecución**: Agente trabaja, genera código.
6.  **Entrega**: Agente usa `submit_artifact(...)`.
7.  **Revisión**: Humano ve el artefacto en Frontend. Aprueba.
8.  **Finalización**: Tarea marcada como 'done'. Notificación al origen.
