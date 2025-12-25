# PHASE 3: Deep Context (RAG) & Safe Execution Sandbox

## 1. Visión General
En la Fase 2 dotamos a OSIRIS de un cerebro y un sistema nervioso. En la Fase 3, le daremos **Memoria de Largo Plazo** y **Manos Seguras**.
Actualmente, el agente "olvida" al reiniciar y sus herramientas de ejecución corren directamente en el host (peligroso).

Objetivos:
1.  **Memoria Contextual (RAG)**: Que el agente pueda indexar y consultar bases de conocimiento (documentación, logs históricos, codebase).
2.  **Sandbox de Ejecución**: Aislar las herramientas de terminal (`run_shell`) en contenedores Docker efímeros para seguridad.
3.  **Gestión de Código (GitOps)**: Permitir que el agente realice commits y PRs de forma autónoma.

---

## 2. Arquitectura Técnica

### A. Sistema de Memoria (Vector Store)
Implementaremos una base de datos vectorial para RAG (Retrieval-Augmented Generation).
*   **Tecnología**: `pgvector` (si usamos Postgres) o `ChromaDB` (local/ligero).
*   **Flujo**:
    *   `Ingest`: Documentos/Código -> Chunking -> Embeddings -> DB.
    *   `Retrieve`: Query -> Similarity Switch -> Context Window.

### B. Execution Sandbox (Docker)
En lugar de `subprocess.run` en el host:
*   El `AgentService` instanciará un contenedor Docker (ej: `python:3.11-slim`) por Tarea o Sesión.
*   Las herramientas `read_file`, `write_file`, `run_shell` operarán *dentro* del contenedor vía Docker API.
*   Volúmenes montados para persistencia selectiva.

### C. Git Integration
Nuevas herramientas MCP:
*   `git_clone`: Clonar repositorios externos.
*   `git_status`/`diff`: Ver cambios.
*   `git_commit`: Crear puntos de guardado.
*   `git_push`: Subir cambios (requiere manejo seguro de credenciales).

---

## 3. Módulos Funcionales

### Módulo 3.A: Vector Memory Service
*   Servicio para calcular embeddings (OpenAI `text-embedding-3-small` o local).
*   Herramienta MCP `search_knowledge_base(query)`.

### Módulo 3.B: Docker Tool Provider
*   Reemplazar `app/services/tools/registry.py` actual con una versión que detecte si debe correr en Host vs Container.
*   Clase `DockerSession`.

### Módulo 3.C: Git Tools
*   Implementar wrappers sobre `gitpython`.
*   Integrar con el `ArtifactViewer` para mostrar diffs de Git.

---

## 4. Plan de Ejecución

1.  **Setup RAG**: Instalar dependencias (`langchain`, `chromadb`, etc.) y configurar embeddings.
2.  **Tool `ask_docs`**: Permitir al agente leer PDFs o MDs de la carpeta `docs/`.
3.  **Docker Setup**: Crear imagen base para los "Workers".
4.  **Migration**: Mover `ToolRegistry` a arquitectura de Sandbox.
