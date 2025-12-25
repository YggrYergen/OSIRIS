# PHASE 2: Core Intelligence, Real-Time Event Loop & Omni-Channel Visualization

## 1. Visión General
El objetivo de la Fase 2 es transformar OSIRIS en un sistema **vivo**. Dejaremos de lado el modelo "Petición-Respuesta" tradicional para pasar a una **Arquitectura Guiada por Eventos (Event-Driven)**.

El sistema debe ser capaz de:
1.  **Ingestar** tareas desde múltiples fuentes (WhatsApp, Email, API) y reflejarlas instantáneamente.
2.  **Procesar** dichas tareas con un Agente IA autónomo que utilice herramientas reales (MCP).
3.  **Transmitir** cada pensamiento, cambio de archivo y log de terminal en tiempo real al humano vía **SSE**.

---

## 2. Arquitectura Técnica

### A. El Motor de Eventos (SSE - Server-Sent Events)
A diferencia de los WebSockets (que usaremos solo para input de alta frecuencia si es necesario), SSE será la columna vertebral de la **observabilidad**.
*   **Canal Único de Verdad**: El frontend mantendrá una conexión SSE (`/api/v1/stream`) suscritaa:
    *   `task_update`: Cambios de estado (Pending -> Running).
    *   `new_message`: Chats humanos o del agente.
    *   `artifact_stream`: Diffs de código generándose en tiempo real.
    *   `terminal_log`: Salida de comandos ejecutados por el agente.
    *   `system_notification`: Alertas globales (ej: "Nuevo lead recibido por WhatsApp").

### B. El Cerebro del Agente (Orquestador Multi-Modelo)
Implementaremos una capa de abstracción para el "Cerebro" que soporte múltiples proveedores.
*   **Motores Soportados**:
    1.  **OpenAI (GPT-4o)**: Ideal para razonamiento complejo y codificación precisa.
    2.  **Google Gemini (1.5 Pro)**: Ideal para ventanas de contexto masivas y velocidad.
*   **Switching Dinámico**: El usuario podrá alternar entre modelos desde la UI o configuración global.
*   **Capacidades**:
    *   Planificación (Chain of Thought).
    *   **Tool Calling Estandarizado**: Sistema agnóstico para que las herramientas (MCP) funcionen igual independientemente del modelo subyacente.
    *   Reflexión (Analizar errores de terminal y corregir).

### C. MCP (Model Context Protocol) Real
Implementación de herramientas seguras que el agente puede invocar:
1.  **File System**: `read_file`, `write_file`, `list_dir`.
2.  **Terminal Sandbox**: `run_command` (controlado, no `rm -rf /`).
3.  **Knowledge Base**: Consultar documentación técnica.

### D. Visualización de "Artefactos"
El chat no es suficiente para codificar. Necesitamos "Artifact Cards" en el frontend que reaccionen a eventos SSE.
*   Si el agente edita `main.py`, el usuario ve un diff visual o el archivo actualizándose en vivo en un panel lateral, no en el chat.
*   Si el agente corre tests, el usuario ve una "Terminal Card" con el output en vivo.

---

## 3. Módulos Funcionales a Implementar

### Módulo 2.A: Event Streaming Bus (Backend)
Configurar FastAPI con `StreamingResponse` y un patrón Pub/Sub (usando `asycio.Queue` o Redis) para despachar eventos a los clientes conectados.

### Módulo 2.B: Omni-Channel Ingestion (Webhooks)
Endopoints reales para recibir payloads externos.
*   Ejemplo: `POST /webhooks/whatsapp` -> Se convierte en `Task` -> Se emite evento `task_created` vía SSE -> Dashboard se actualiza solo.

### Módulo 2.C: Agentic Workflow Executor (Multi-Brain)
El servicio de fondo (`BackgroundTasks` o `Celery`) que toma una tarea y empieza a trabajar:
*   **BrainFactory**: Selecciona `OpenAIBrain` o `GeminiBrain` basado en preferencias.
*   Loop de Ejecución: 
    1.  Lee descripción.
    2.  Decide herramienta.
    3.  Ejecuta herramienta.
    4.  Guarda resultado.
    5.  Emite evento de progreso.

### Módulo 2.D: Frontend Live State
Actualizar `ChatInterface` y `Dashboard` para consumir SSE en lugar de hacer polling o depender puramente de WS (híbrido si mantemos WS para chat input rápido). Migrar el estado global a un store robusto (Zustand) que reacciona a los eventos entrantes.

---

## 4. Criterios de Éxito de la Fase 2
*   [ ] Dashboard se actualiza sin recargar página al recibir webhook simulado.
*   [ ] Agente recibe instrucción compleja y el usuario puede elegir si usar GPT-4o o Gemini.
*   [ ] Switching de modelo funciona correctamente (se verifica en logs).
*   [ ] Latencia de notificación < 200ms.
