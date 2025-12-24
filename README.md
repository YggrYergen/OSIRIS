# OSIRIS: Omni-Channel Dev Orchestrator

> **Plataforma Enterprise de Orquestación de Desarrollo Asistido por IA con Supervisión Humana (HITL)**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![Status](https://img.shields.io/badge/status-production_ready-green.svg) ![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 📖 Tabla de Contenidos

1.  [Introducción y Filosofía](#-introducción-y-filosofía)
2.  [Visión General del Sistema](#-visión-general-del-sistema)
3.  [Arquitectura Técnica en Profundidad](#-arquitectura-técnica-en-profundidad)
    *   [Backend Core (FastAPI)](#1-backend-core-fastapi)
    *   [Base de Datos y Modelos](#2-base-de-datos-y-modelos)
    *   [Frontend Portal (Next.js)](#3-frontend-portal-nextjs)
    *   [Model Context Protocol (MCP) Server](#4-model-context-protocol-mcp-server)
4.  [Flujos de Datos y Ciclo de Vida](#-flujos-de-datos-y-ciclo-de-vida)
5.  [Instalación y Despliegue](#-instalación-y-despliegue)
6.  [Guía Operativa](#-guía-operativa)
7.  [Extensibilidad y Futuro](#-extensibilidad-y-futuro)

---

## 🔭 Introducción y Filosofía

**OSIRIS** no es simplemente un gestor de tareas; es un **sistema inmunológico para el código generado por IA**.

En la era actual, generar código es trivial. El verdadero desafío es la **integridad, la seguridad y la alineación** de ese código con los objetivos del negocio. Osiris introduce una capa de gobernanza estricta entre la "Intención" (solicitud del usuario) y la "Ejecución" (commit en producción).

### El Problema
Los agentes de IA autónomos ("Agentic Coding") tienden a divergir, alucinar o introducir regresiones sutiles si se les permite operar sin supervisión constante.

### La Solución Osiris
Un pipeline **Human-in-the-Loop (HITL)** forzado por arquitectura. Ningún código generado por un agente es considerado "válido" hasta que pasa por el **Portal de Supervisión**, donde un humano revisa, comenta o aprueba los artefactos generados.

---

## 🌍 Visión General del Sistema

El ecosistema Osiris se compone de tres pilares fundamentales que operan de forma asíncrona pero coordinada:

1.  **Ingesta (The Ear)**: Capaz de escuchar múltiples canales (WhatsApp, Slack, Email) y normalizar las solicitudes en "Tickets" estandarizados.
2.  **Ejecución (The Hand)**: Una interfaz estandarizada vía **MCP (Model Context Protocol)** que permite a cualquier IA (Claude, GPT-4, Llama) "fichar" tareas, trabajar en su entorno local y enviar resultados.
3.  **Control (The Eye)**: Un dashboard en tiempo real donde los humanos supervisan el progreso, chatean con los agentes y aprueban los entregables.

---

## 🏗 Arquitectura Técnica en Profundidad

### 1. Backend Core (FastAPI)
*Ubicación: `/backend`*

El núcleo del sistema es una API REST asíncrona construida sobre **FastAPI**. Diseñada para alta concurrencia y baja latencia.

*   **Gateway de Ingesta**: Endpoints dedicados en `/api/v1/webhooks` normalizan payloads externos (ej. Twilio WhatsApp) a estructuras internas.
*   **Gestor de WebSockets (`core/websockets.py`)**: Mantiene conexiones vivas con el Frontend. Implementa un patrón Pub/Sub donde cada `task_id` es un canal de difusión. Cualquier cambio de estado en una tarea se propaga en <50ms a todos los clientes conectados.
*   **Seguridad**: Middleware de CORS configurado y preparación para autenticación JWT (Oauth2 flows).

### 2. Base de Datos y Modelos
*Tecnología: PostgreSQL + SQLAlchemy + Alembic*

El modelo de datos es relacional y estricto para garantizar la integridad transaccional.

*   **Tasks (`models/task.py`)**: La entidad atómica. Contiene estado (`PENDING`, `IN_PROGRESS`, `REVIEW`, `DONE`, `REJECTED`), descripción y prioridad.
*   **Artifacts (`models/artifact.py`)**: Representa el trabajo entregable (snippets de código, PRs, documentos). Versioando automáticamente.
*   **Messages (`models/message.py`)**: Hilo de comunicación persistente entre el Humano y la IA. Contexto compartido.
*   **Users (`models/user.py`)**: Gestión de roles (Admin, Reviewer, Agent).

*Nota: Las migraciones de base de datos se manejan exclusivamente vía Alembic. No realice cambios DDL manuales.*

### 3. Frontend Portal (Next.js)
*Ubicación: `/frontend`*

Una Single Page Application (SPA) moderna renderizada en servidor y cliente.

*   **Tech Stack**: Next.js 14 (App Router), TypeScript, TailwindCSS v4, Framer Motion.
*   **Arquitectura de Componentes**: Diseño atómico. Componentes visuales puros en `components/ui` y componentes lógicos (containers) en `app/`.
*   **Real-Time Hooks**: `useTaskWebSocket` abstrae la complejidad de reconexión y manejo de eventos del socket, exponiendo un estado reactivo simple a la UI.
*   **Renderizado de Código**: Utiliza bloques de código con resaltado de sintaxis para facilitar la "Diff View" durante la revisión.

### 4. Model Context Protocol (MCP) Server
*Ubicación: `/mcp-server`*

El **puente universal**. Osiris no "contiene" a la IA; Osiris "expone" trabajo a la IA. Este servidor implementa el estándar abierto de Anthropic/Google para herramientas de contexto.

Lanza un servidor local que expone las siguientes **Tools** a cualquier agente conectado:
*   `read_pending_tasks()`: Lista tareas esperando atención.
*   `claim_task(task_id)`: Asigna la tarea al agente y cambia estado a `IN_PROGRESS`.
*   `submit_artifact(task_id, content)`: Envía el trabajo para revisión humana (`REVIEW`).
*   `read_feedback(task_id)`: Obtiene los comentarios del humano tras un rechazo.

---

## 🔄 Flujos de Datos y Ciclo de Vida

El ciclo de vida de una tarea es una máquina de estados finitos (FSM) estricta:

1.  **Creation**:
    *   Trigger: Webhook (ej. WhatsApp).
    *   Action: `POST /webhooks/...` -> DB Insert -> WS Broadcast "New Task".
    *   Status: `PENDING`.

2.  **Assignment**:
    *   Trigger: Agente llama `claim_task`.
    *   Action: Validación de disponibilidad -> DB Update (Assignee) -> WS Broadcast "Agent Working".
    *   Status: `IN_PROGRESS`.

3.  **Submission**:
    *   Trigger: Agente llama `submit_artifact`.
    *   Action: Guardado de contenido -> Notificación al Humano.
    *   Status: `REVIEW`.

4.  **Adjudication (Human Loop)**:
    *   Trigger: Humano hace clic en "Aprobar" o "Rechazar" en Frontend.
    *   **Opción A (Aprobar)**: Status `DONE`. El código se considera firme.
    *   **Opción B (Rechazar)**: Status `IN_PROGRESS`. Se añade un mensaje de feedback. El agente debe reintentar.

---

## 🚀 Instalación y Despliegue

### Requisitos Previos
*   Docker & Docker Compose (Recomendado para producción/local completo).
*   Python 3.11+ (Para desarrollo backend/mcp).
*   Node.js 20+ (Para desarrollo frontend).

### Inicio Rápido con Docker
Levanta todo el stack (DB, Backend, Frontend) en contenedores aislados.

```bash
# 1. Configurar entorno
cp .env.example .env
# TWEAK: Ajusta POSTGRES_PASSWORD en .env para seguridad

# 2. Levantar servicios
docker-compose up --build -d

# 3. Acceder
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Script de Prueba (Inyección)
Para verificar el sistema sin conectar WhatsApp real:
```bash
python scripts/inject_task.py
# Sigue las instrucciones para crear una tarea dummy
```

---

## 🎮 Guía Operativa

### Conectando un Agente (IA)
Para que una IA (ej. un asistente en tu IDE o terminal) pueda trabajar en Osiris:

1.  Asegúrate que el `mcp-server` esté corriendo o accesible.
2.  Configura el cliente MCP de tu herramienta (ej. `claude_desktop_config.json`):
    ```json
    "mcpServers": {
      "osiris-local": {
        "command": "python",
        "args": ["d:/OSIRIS/mcp-server/src/server.py"]
      }
    }
    ```
3.  Reinicia el agente. Ahora tendrá acceso a las *Tools* de Osiris.

### Rol del Supervisor
1.  Mantener el Frontend abierto.
2.  Cuando llegue una notificación sonora o visual, revisar el artefacto.
3.  **Ser implacable**: Si el código no cumple estándares, rechazar con feedback claro. La IA no se ofende.

---

## 🔌 Extensibilidad y Futuro

Osiris está diseñado para ser agnóstico y extensible. Aquí se detallan los vectores de expansión para desarrolladores:

### 1. Nuevos Canales de Entrada (Inputs)
Para añadir soporte a Slack, Telegram o Email:
*   Crear un nuevo endpoint en `backend/app/api/endpoints/webhooks.py`.
*   Mapear el payload entrante al esquema `TaskCreate`.
*   No se requiere cambiar nada más; el sistema es polimórfico respecto al origen.

### 2. Personalización de Reglas de Negocio
*   **Validaciones Automáticas**: Se pueden inyectar scripts de CI/CD en el paso de `submit_artifact` (backend) para correr linters o tests unitarios antes de siquiera molestar al humano.
*   **Asignación Inteligente**: Modificar la lógica de `claim_task` para asignar tareas basadas en la especialidad del agente (Router Pattern).

### 3. Integración CI/CD
*   **Fase Futura**: Cuando una tarea pasa a `DONE`, disparar un webhook saliente (Webhook Action) que haga commit del `artifact.content` a un repo Git real. Esto cerraría el ciclo de desarrollo completo automáticamente.

### 4. Soporte Multi-Tenant
*   Actualmente el sistema es Single-Tenant. Para uso SaaS, extender el modelo `User` para pertenecer a `Organizations` y filtrar todas las queries de SQLAlchemy por `org_id`.

---
**© 2025 Osiris Project** | *Building the Rails for the AI Age*
