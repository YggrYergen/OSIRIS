# PASOS DE IMPLEMENTACIÓN: OMNI-CHANNEL DEV ORCHESTRATOR

Este documento define la ruta crítica para construir el sistema. Cada paso debe completarse y verificarse antes de pasar al siguiente.

## FASE 1: PLANIFICACIÓN (COMPLETADA)
- [x] Crear estructura de archivos de documentación (`PLAN.md`, `STEPS.md`, `.aiexclude`).
- [x] Definir arquitectura y esquema de base de datos.
- [x] Crear `.env` inicial.

## FASE 2: BACKEND CORE (DESPLEGADA Y VERIFICADA)
- [x] **API Core**: Endpoints, Modelos y Configuración.
- [x] **Verificación**: Tests unitarios manuales pasaron exitosamente (Mock DB).
- [x] **Logging**: Sistema de trazas configurado con Loguru.

## FASE 3: MCP SERVER ("The Bridge") (COMPLETADA Y VERIFICADA)
- [x] **Servidor**: Implementado en Python.
- [x] **Verificación**: Script de testeo con Mocks (`scripts/test_mcp_logic.py`) validó lógica `claim_ticket`.

## FASE 4: PORTAL DE REVISIÓN (Frontend) (COMPLETADA)
El objetivo es que el humano pueda ver y gestionar el trabajo.
- [x] **Scaffolding**: Next.js 14 + Tailwind + TypeScript.
- [x] **Estilos**: Configurado tema oscuro premium en `globals.css`.
- [x] **Tipos**: Definidas interfaces TypeScript compartidas con Backend.
- [x] **Componentes UI**: `TaskCard` y `KanbanBoard` básico implementados.
- [x] **Auth UI**: Páginas de Login y Registro con estética premium.
- [x] **API Real**: Conexión con Backend mediante `fetchWithAuth` y `api-details.ts` corregido.
- [x] **Detalle de Tarea**: Página `/tasks/[id]` conectada exitosamente al backend.

## FASE 5: REAL-TIME & INTEGRACIÓN FINAL (EN PROCESO)
- [x] **WebSockets**: Gestor de WS en Backend y Hook `useTaskWebSocket` básico.
- [ ] **Chat en Vivo**: Conectar ChatInterface con WS.
- [ ] **Tests E2E**: Validación de flujos completos.

## FASE 6: SEGURIDAD, MULTI-AUTH Y REGISTRO (DESPLEGADA)
Este paso es crítico para la validación del sistema al 100%.
- [x] **Backend Security**: Implementado hashing (PBKDF2), JWT (jose) e identidad asíncrona.
- [x] **DB Migration**: Tabla `users` actualizada con email, google_id y hashed_password.
- [x] **Auth Endpoints**: Registro local, Login OAuth2 y soporte Google SSO.
- [x] **Protección de Rutas**: Endpoints de `/tasks` protegidos con inyección de usuario.
- [x] **Frontend Auth**: AuthGuard global, persistencia de sesión con Zustand.
- [x] **Validación**: Login Admin verificado y corregido (Pbkdf2 fix).

## FASE 7: DEPLOYMENT & CI/CD FINAL (PRÓXIMO)
1.  Docker Compose optimizado para producción.
2.  Scripts de backup y restauración.
3.  Webhooks de salida (PR triggers).
