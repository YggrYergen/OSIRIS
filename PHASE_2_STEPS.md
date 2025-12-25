# PHASE 2 IMPLEMENTATION STEPS

Este documento detalla los pasos técnicos para implementar la arquitectura de la Fase 2, incluyendo soporte Multi-Modelo.

---

## Módulo A: Infraestructura SSE y Eventos (Foundation)

### Step 1: Backend Event Bus
- [x] Crear `app/schemas/events.py` (Tipos de Eventos).
- [x] Crear `app/core/event_bus.py` (Pub/Sub Queue).
- [x] Implementar endpoint SSE en `app/api/endpoints/stream.py`. (Verificar funcionamiento).

### Step 2: Frontend SSE Hook & Store
- [x] Crear `useEventStream` hook en React.
- [ ] Integrar hook en `Providers` o Layout global.
- [ ] Actualizar Zustand Store para reaccionar a eventos.

## Módulo B: Omni-Channel & Ingestión

### Step 3: Webhook Receiver
- [ ] Crear `app/api/endpoints/webhooks.py` (expandir el existente).
- [ ] Endpoint `POST /ingest/{source}`.
- [ ] Lógica: Crear Tarea -> Push Evento `task_created`.

## Módulo C: El Agente (Multi-Brain Architecture)

### Step 4: Brain Abstraction Layer
- [ ] Crear interfaz abstracta `app/services/brain/base.py`:
    -   Método `think(history, tools) -> Plan/Action`.
- [ ] Implementar `app/services/brain/openai_brain.py`.
- [ ] Implementar `app/services/brain/gemini_brain.py`.
- [ ] Crear `app/services/brain/factory.py` para instanciar según configuración.

### Step 5: Service Layer (Agent Loop)
- [ ] Crear `app/services/agent_service.py`.
- [ ] Integrar Factory para obtener el cerebro configurado (por defecto OpenAI, switchable a Gemini).
- [ ] Implementar el Loop: Pensar -> Actuar -> Verificar -> Notificar (SSE).

### Step 6: Tool Definitions (MCP Tools)
- [ ] Implementar wrappers seguros de FileSystem y Shell.

## Módulo D: Visualización en Frontend

### Step 7: UI de Selección de Modelo
- [ ] Agregar selector (Dropdown/Toggle) en la UI para elegir "Brain: OpenAI" o "Brain: Gemini".
- [ ] Persistir preferencia en LocalStorage o UserSettings.

### Step 8: Componentes Artifact & Terminal
- [ ] Crear `ArtifactRenderer` (Code block with syntax highlighting).
- [ ] Crear `TerminalFeed` (Logs streaming).

---

## Verificación Final Fase 2 (E2E)

1.  Iniciar tarea con OpenAI. Ver logs.
2.  Cambiar a Gemini a mitad de vuelo o en nueva tarea. Ver logs.
3.  Confirmar que ambos pueden editar archivos y responder chats.
