# 🧪 GUÍA DE TESTEO MANUAL INTEGRAL (OSIRIS v1.1.0)

Esta guía permite validar holísticamente todas las piezas del sistema: Backend, Frontend, Seguridad (Multi-Auth) y Lógica de Orquestación.

## 🛠 PRE-REQUISITOS (Ambiente Windows 11)
El sistema debe estar en ejecución. Sigue la sección [Despliegue Local](#-despliegue-local) para activarlo.

---

## 🔐 MÓDULO A: SEGURIDAD Y ACCESO (NUEVO)
*Validación del sistema de identidad y protección de perímetros.*

### 1. Intento de Acceso No Autorizado
1. Abre `http://localhost:3000/`.
2. **Resultado Esperado**: El sistema debe detectar que no hay token y redirigirte automáticamente a `http://localhost:3000/login`. No deberías poder ver el Dashboard.

### 2. Registro de Nuevo Supervisor
1. En la pantalla de login, haz clic en **"Solicite registro"**.
2. Completa el formulario (Usa un email real o ficticio, ej: `test@osiris.dev`).
3. Haz clic en **"Completar Registro"**.
4. **Resultado Esperado**: Redirección exitosa al Login con un mensaje de éxito.

### 3. Login Exitoso (Credenciales Internas)
1. Usa las credenciales del Administrador Semilla:
   * **Email**: `admin@osiris.dev`
   * **Password**: `admin123`
2. **Resultado Esperado**: Acceso concedido, redirección al Dashboard. Verifica que en el header o perfil se reconozca tu rol de "Admin".

### 4. Simulación de Google SSO
1. Cierra sesión (Logout).
2. Haz clic en el botón **"Google"**.
3. **Resultado Esperado**: Redirección al Mock de Google (en dev) y retorno con una sesión activa.

---

## 🟢 MÓDULO B: GESTIÓN DE TAREAS (INGESTA HITL)
*Validación del pipeline de datos y supervisión.*

### 1. Ingesta de Tarea desde "Origen Externo"
1. Abre una terminal de PowerShell.
2. Ejecuta el script de inyección:
   ```powershell
   .\venv\Scripts\Activate
   $env:PYTHONPATH="backend"
   python scripts/inject_task.py
   ```
3. Ingresa un título descriptivo: `"Refactorizar módulo de Auth para producción"`.
4. **Verificación en Dashboard**: La tarea debe aparecer instantáneamente en la columna **PENDING**.

### 2. Supervisión y Detalle (Requires Auth)
1. Haz clic en la nueva tarea.
2. **Resultado Esperado**: Debes ver el detalle completo. Si intentas acceder a esta URL desde un navegador en incógnito (sin login), debe fallar o redirigir.

---

## 🤖 MÓDULO C: INTERACCIÓN CON EL AGENTE (MCP)
*Validación del puente entre IA y Humano.*

### 1. Reclamo de Tarea (Agent Claim)
1. Simula que un agente toma la tarea:
   ```powershell
   python scripts/test_mcp_logic.py
   ```
   *(Asegúrate de que el script apunte al ID correcto de la tarea recién creada).*
2. **Resultado Esperado**: En el Dashboard, la tarjeta debe cambiar de color/estado a **CLAIMED**.

---

## 🔍 PASOS DE CIERRE: INTEGRACIÓN TOTAL
1.  **Persistencia**: Recarga la página (`F5`). Debes seguir logueado (Zustand + LocalStorage).
2.  **Seguridad Zero-Trust**: Intenta usar una herramienta de API (Postman/Curl) para hacer un `GET` a `http://localhost:8000/api/v1/tasks` sin el header de Authorization. El backend debe responder `401 Unauthorized`.

---
**¿Pudiste completar todo?**
Si todos los checks son positivos, el sistema OSIRIS está operando bajo su arquitectura nominal v1.1.0. 🚀
