# PHASE 3 IMPLEMENTATION STEPS

## Módulo A: Memoria y Contexto (RAG)

### Step 1: Infraestructura Vectorial
- [ ] Instalar `chromadb` y `langchain-openai`.
- [ ] Crear `app/services/memory/vector_store.py`.
- [ ] Implementar función `ingest_document(path)`.

### Step 2: Tool de Conocimiento
- [ ] Crear herramienta MCP `query_knowledge_base(query: str) -> str`.
- [ ] Registrar herramienta en `ToolRegistry`.
- [ ] Test: Preguntar al agente sobre un documento indexado.

## Módulo B: Ejecución Segura (Docker Sandbox)

### Step 3: Docker Manager
- [ ] Instalar `docker` SDK para Python.
- [ ] Crear `app/core/sandbox.py`.
    -   `start_container()`
    -   `exec_command(container_id, cmd)`
    -   `stop_container()`

### Step 4: Migración de Tools
- [ ] Actualizar `run_shell` en `registry.py` para usar `sandbox.exec_command` si la configuración lo dicta.
- [ ] Actualizar `write_file` / `read_file` para trabajar con el sistema de archivos del contenedor (o volumen montado).

## Módulo C: Git Operations

### Step 5: Git Tools
- [ ] Crear herramientas:
    -   `git_init`
    -   `git_add`
    -   `git_commit`
    -   `git_push`
- [ ] Asegurar inyección segura de tokens (GitHub PAT).

## Verificación Fase 3
- [ ] Agente capaz de leer un README.md y responder preguntas (RAG).
- [ ] Agente ejecuta `ls -la` y retorna resultado desde dentro de un contenedor Docker aislado.
- [ ] Agente hace un commit de sus cambios.
