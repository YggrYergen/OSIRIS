# OSIRIS: Omni-Channel Dev Orchestrator

> **Plataforma Enterprise de Orquestación de Desarrollo Asistido por IA con Supervisión Humana (HITL)**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![Status](https://img.shields.io/badge/status-production_ready-green.svg) ![License](https://img.shields.io/badge/license-MIT-lightgrey.svg) ![Python](https://img.shields.io/badge/python-3.11-blue.svg) ![Next.js](https://img.shields.io/badge/next.js-14-black.svg)

---

## 📖 Tabla de Contenidos

1.  [Introducción y Filosofía](#-introducción-y-filosofía)
2.  [Arquitectura del Sistema](#-arquitectura-del-sistema)
3.  [Estructura del Proyecto](#-estructura-del-proyecto) **(New)**
4.  [Capacidades y Casos de Uso](#-capacidades-y-casos-de-uso)
5.  [Modelo de Datos y Estados](#-modelo-de-datos-y-estados) **(Update)**
6.  [Model Context Protocol (MCP)](#-model-context-protocol-mcp) **(Corrected)**
7.  [Instalación y Despliegue](#-instalación-y-despliegue)
8.  [Guía de Desarrollo (Contributing)](#-guía-de-desarrollo-contributing) **(New)**
9.  [Troubleshooting](#-troubleshooting)

---

## 🔭 Introducción y Filosofía

**OSIRIS** no es simplemente un gestor de tareas; es un **sistema inmunológico para el código generado por IA**.

En la era actual, generar código es trivial. El verdadero desafío es la **integridad, la seguridad y la alineación**. Osiris introduce una capa de gobernanza estricta (HITL) entre la solicitud del usuario y el commit en producción.

### La Solución Osiris
Un pipeline donde ningún código generado por un agente es considerado "válido" hasta pasar por el **Portal de Supervisión**.
1.  **Ingesta**: Normalización de inputs (WhatsApp, Web, API).
2.  **Agencia IA**: Workers autónomos (Claude, GPT-4) consumen tareas vía MCP.
3.  **Supervisión**: Interfaz humana para revisión de difs y aprobación.

---

## 🏗 Arquitectura del Sistema

### Diagrama de Componentes
El sistema sigue una arquitectura de **monorepositorio modular** optimizada para despliegue en contenedores.

```mermaid
graph TD
    A[Clients: WhatsApp/Web] -->|Webhook| B(Backend API / FastAPI)
    B <-->|read/write| C[(PostgreSQL DB)]
    D[Frontend / Next.js] <-->|WebSocket| B
    E[AI Agent / Cursor/Windsurf] <-->|MCP Protocol| F[MCP Server]
    F -.->|Direct DB Access| C
```

1.  **Backend Core (`/backend`)**: API REST FastAPI + WebSockets Manager para estado en tiempo real.
2.  **Frontend Portal (`/frontend`)**: Next.js 14 App Router con TailwindCSS y Shadcn/UI.
3.  **MCP Server (`/mcp-server`)**: Puente que expone la base de datos como "Herramientas" para Agentes de IA locales.

---

## 📂 Estructura del Proyecto

Una visión jerárquica de los módulos clave para facilitar la navegación del desarrollador.

```text
OSIRIS/
├── backend/                # API Server (Python/FastAPI)
│   ├── app/
│   │   ├── api/            # REST Endpoints (v1/webhooks, tasks)
│   │   ├── core/           # Config, Logging, WebSocket Manager
│   │   ├── models/         # SQLAlchemy Models (Task, Artifact, Message)
│   │   └── schemas/        # Pydantic Schemas (Validation)
│   └── alembic/            # DB Migrations
├── frontend/               # User Interface (Next.js/TS)
│   ├── src/
│   │   ├── app/            # App Router Pages
│   │   ├── components/     # UI Components (TaskCard, ChatInterface)
│   │   └── lib/            # Utilities & WebSocket Hooks
├── mcp-server/             # AI Integration Layer
│   └── src/server.py       # MCP Implementation (Tools & Resources)
├── scripts/                # Utility scripts (e.g., inject_task.py)
└── docker-compose.yml      # Orchestration
```

---

## ⚡ Capacidades y Casos de Uso

### 1. Generación de Features "On-the-Go"
Desde un mensaje de audio en WhatsApp ("Crea una landing page") hasta una PR lista para mergear. Osiris orquesta la creación de la tarea, la asignación a un agente y la notificación de revisión.

### 2. Mantenimiento y Bugfixing
Reportes de errores ingresan como tickets de alta prioridad. El Agente analiza el contexto, propone un fix y el supervisor valida que no existan regresiones.

### 3. Documentación de Código
Tareas de baja prioridad para documentar módulos legacy. El agente consume el código fuente y genera docstrings estandarizados.

---

## 📊 Modelo de Datos y Estados

El ciclo de vida de una `Task` es una máquina de estados estricta. Es vital entenderla para extender el sistema.

### Estados de Tarea (`TaskStatus`)
*   `PENDING`: Tarea creada, esperando en cola.
*   `CLAIMED`: Un agente ha reservado la tarea (bloqueo optimista).
*   `IN_PROGRESS`: El agente está trabajando activamente.
*   `REVIEW_PENDING`: Se ha enviado un *Artifact* (código) para revisión humanada.
*   `APPROVED`: El humano aceptó el trabajo.
*   `REJECTED`: El humano rechazó el trabajo (con feedback).
*   `DONE`: Tarea finalizada y archivada.

### Entidades Core
*   **Artifact**: El entregable (Snippet de código, URL, Doc). Versionado 1..N por tarea.
*   **Message**: Chat contextual persistente entre IA y Humano asociado a la tarea.

---

## 🤖 Model Context Protocol (MCP)

Osiris implementa la especificación MCP para permitir que cualquier IDE o Agente compatible (Cursor, Windsurf, Claude Desktop) interactúe con el sistema.

### Resources (Lectura)
*   `orchestrator://queue`: Retorna la lista JSON de tareas en estado `PENDING`.

### Tools (Acción)
1.  **`claim_ticket(task_id: int)`**
    *   Marca una tarea como `CLAIMED` para evitar colisiones entre agentes.
2.  **`submit_artifact(task_id: int, content: str, type: str)`**
    *   Envía código o texto al humano. Cambia estado a `REVIEW_PENDING`.
3.  **`send_message(task_id: int, text: str)`**
    *   Envía un mensaje al chat de la tarea para consultar dudas al supervisor.

---

## 🚀 Instalación y Despliegue

### Requisitos
*   Docker Desktop & Git.
*   Python 3.11+ (Entorno Dev).

### Despliegue Rápido (Docker)
Este es el método recomendado para tener DB, Backend y Frontend conectados automáticamente.

```bash
# 1. Configuración de Entorno
cp .env.example .env
# Edita .env: Asegura contraseñas fuertes para POSTGRES_PASSWORD

# 2. Iniciar Servicios
docker-compose up --build -d

# 3. Verificar
# Frontend: http://localhost:3000
# Backend Docs: http://localhost:8000/docs
```

### Conexión del Agente (Local)
Para conectar tu Agente IA (ej. Windsurf/Claude) al sistema corriendo localmente:

Configura tu `claude_desktop_config.json` o equivalente:
```json
{
  "mcpServers": {
    "osiris": {
      "command": "python",
      "args": ["<ABSOLUTE_PATH>/OSIRIS/mcp-server/src/server.py"],
      "env": {
        "DATABASE_URL": "postgresql+asyncpg://postgres:postgres@localhost:5432/osiris_db"
      }
    }
  }
}
```
*Nota: El Agente corre en el host, por lo que debe poder acceder al puerto 5432 de localhost expuesto por Docker.*

---

## 🛠 Guía de Desarrollo (Contributing)

### Backend
*   **Framework**: FastAPI.
*   **ORM**: SQLAlchemy 2.0 (Async).
*   **Migraciones**: `alembic upgrade head` para aplicar cambios de schema.
*   **Tests**: Ejecutar `pytest` en `/backend`.

### Frontend
*   **Framework**: Next.js 14 App Router.
*   **Styling**: TailwindCSS.
*   **State**: React Query + WebSockets custom hook (`useTaskWebSocket`).

---

## 🔧 Troubleshooting

### "Backend modules not found" en MCP
El servidor MCP añade dinámicamente el path del backend. Asegúrate de ejecutarlo desde la raíz del proyecto o que la estructura de carpetas sea la estándar.

### WebSockets desconectados
Si usas Nginx o Cloudflare, configura `proxy_read_timeout` a 60s+ y habilita headers de upgrade (WS).

### Database Connection Refused
Asegúrate de que el contenedor `osiris_db` esté "Healthy". En el primer arranque, Postgres tarda unos segundos en inicializar antes de aceptar conexiones.

---
**© 2025 Osiris Project** | *Standardizing the AI Workforce*
