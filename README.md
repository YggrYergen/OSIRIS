# OSIRIS: Omni-Channel Dev Orchestrator

> **Plataforma Enterprise de Orquestación de Desarrollo Asistido por IA con Supervisión Humana (HITL)**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg) ![Status](https://img.shields.io/badge/status-production_ready-green.svg) ![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

---

## 📖 Tabla de Contenidos

1.  [Introducción y Filosofía](#-introducción-y-filosofía)
2.  [Visión General del Sistema](#-visión-general-del-sistema)
3.  [Capacidades y Casos de Uso](#-capacidades-y-casos-de-uso) **(Nuevo)**
4.  [Arquitectura Técnica en Profundidad](#-arquitectura-técnica-en-profundidad)
    *   [Backend Core (FastAPI)](#1-backend-core-fastapi)
    *   [Base de Datos y Modelos](#2-base-de-datos-y-modelos)
    *   [Frontend Portal (Next.js)](#3-frontend-portal-nextjs)
    *   [Model Context Protocol (MCP) Server](#4-model-context-protocol-mcp-server)
5.  [Flujos de Datos y Ciclo de Vida](#-flujos-de-datos-y-ciclo-de-vida)
6.  [Instalación y Despliegue](#-instalación-y-despliegue)
7.  [Guía Operativa](#-guía-operativa)
8.  [Extensibilidad y Futuro](#-extensibilidad-y-futuro)

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

## ⚡ Capacidades y Casos de Uso

Osiris está diseñado para manejar el ciclo completo de desarrollo en escenarios complejos. A continuación, detallamos exhaustivamente qué puede hacer el sistema y cómo opera internamente en cada caso.

### Caso 1: Generación de Features "On-the-Go"
*Escenario: Un Product Manager tiene una idea en una reunión y la envía por WhatsApp.*

*   **Experiencia de Usuario:**
    1.  El usuario envía un audio o texto a WhatsApp: *"Necesito una Landing Page para la campaña de Black Friday, estilo cyberpunk, con un contador regresivo".*
    2.  En segundos, el Agente confirma recepción.
    3.  Minutos después, el usuario recibe una notificación: *"Propuesta lista para revisión"*.
    4.  El usuario (o el Tech Lead) entra al Portal Web, ve el código y la previsualización del componente.
    5.  Si aprueba, el código se integra al repositorio.

*   **Under The Hood (Flujo Técnico):**
    1.  **Webhook**: Twilio recibe el mensaje -> POST `/api/v1/webhooks/whatsapp` en Osiris Backend.
    2.  **Task Creation**: Se crea Tarea ID `TASK-123` con descripción y prioridad alta.
    3.  **MCP List**: El Agente (ej. Claude en Windsurf) consulta `read_pending_tasks()` y ve la nueva tarea.
    4.  **Claim & Work**: El Agente llama `claim_task('TASK-123')`. Genera los archivos React/Tailwind localmente.
    5.  **Submission**: El Agente llama `submit_artifact('TASK-123', content='...')`.
    6.  **Review**: El WebSocket alerta al Frontend. El humano revisa. Si da OK -> Estado `DONE`.

### Caso 2: Corrección de Bugs y Mantenimiento
*Escenario: Un usuario reporta un error crítico en producción a través de un formulario de soporte.*

*   **Experiencia de Usuario:**
    1.  Reporte: *"El botón de pago da error 500 en Firefox"*.
    2.  El sistema ingesta el reporte automáticamente.
    3.  El Agente asignado analiza el stack trace (adjunto en la tarea) y propone un fix.
    4.  El Tech Lead revisa el "Diff" en el portal de Osiris y ve que solo cambia una línea de validación. Aprueba inmediatamente.

*   **Under The Hood:**
    1.  **Context Injection**: Al crear la tarea, Osiris puede inyectar logs o contexto adicional en el campo `description`.
    2.  **Iterative Feedback**: Si el humano rechaza el primer fix *"Esto rompe Chrome"*, se añade un mensaje a la DB.
    3.  **Re-Try**: El Agente lee el feedback con `read_feedback()`, ajusta el código y reenvía el artefacto. El ciclo se repite hasta la perfección.

### Caso 3: Documentación de Código Legacy
*Escenario: Un desarrollador senior quiere documentar un módulo antiguo escrito en Python.*

*   **Experiencia de Usuario:**
    1.  El Dev envía: *"Documenta exhaustivamente la clase `PaymentGateway` en `src/payments.py` siguiendo formato Google Docstring"*.
    2.  El Agente lee el archivo (si tiene acceso al repo local) o recibe el contenido en la descripción.
    3.  El Agente devuelve el archivo python con los docstrings añadidos.
    4.  Revisión rápida y Merge.

*   **Under The Hood:**
    1.  **Large Payloads**: Osiris maneja grandes volúmenes de texto en `artifact.content` gracias a estar basado en almacenamiento de texto en DB (o S3 en implementaciones custom).
    2.  **Security**: Al pasar por revisión humana, se asegura que la IA no haya alucinado métodos inexistentes o expuesto secretos en los comentarios.

### Caso 4: Refactorización Arquitectónica
*Escenario: Migración de CSS plano a TailwindCSS.*

*   **Experiencia:**
    1.  Tara masiva: *"Refactorizar componentes del Dashboard para usar utilidades de Tailwind"*.
    2.  El Agente toma componentes uno por uno (subtareas) y envía las versiones actualizadas.
    3.  El humano las aprueba en lote.

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
Para añadir soporte a Slack, Telegram o Emails:
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
