
# 🧪 GUÍA DE TESTEO MANUAL EXHAUSTIVO - OSIRIS

Sigue estos pasos para validar que el sistema funciona de punta a punta ("Definition of Done").

## Prequisitos
Tener el sistema corriendo (Backend :8000, Frontend :3000).

---

## 🟢 PASO 1: VERIFICACIÓN VISUAL
1.  Abre tu navegador en `http://localhost:3000`.
2.  Deberías ver el **Osiris Task Queue** (Kanban).
3.  Probablemente esté vacío o muestre datos de ejemplo.
4.  Observa el diseño "Dark Mode Premium".

## 🟢 PASO 2: INGESTA DE TAREA (El Cliente)
Vamos a simular que llega un mensaje de WhatsApp pidiendo un desarrollo.

1.  Abre una terminal nueva en `D:\OSIRIS`.
2.  Ejecuta el inyector:
    ```powershell
    python scripts/inject_task.py
    ```
3.  Escribe: `"Crear una Landing Page para venta de Cafeteras IA"` (o lo que gustes).
4.  **Verifica en Frontend**: Vuelve al navegador y refresca (o espera si WebSocket funcionó). Deberías ver una nueva tarjeta en la columna **PENDING**.

## 🟢 PASO 3: DETALLE Y CONEXIÓN (El Humano)
1.  Haz clic en la tarjeta de la tarea creada.
2.  Navegarás a `/tasks/[ID]`.
3.  Verifica que el título y descripción coinciden.
4.  Observa el indicador de estado en la cabecera: Debería decir **OFFLINE** inicialmente (ya que no hay agente conectado al socket aun, o si el socket conectó frontend-backend dirá LIVE).

## 🟢 PASO 4: INTERVENCIÓN DEL AGENTE (La IA)
Ahora simularemos que un Agente Autónoma (como Windsurf) toma el trabajo.

1.  Abre otra terminal.
2.  Ejecuta el script de validación lógica MCP (que actúa como agente):
    ```powershell
    python scripts/test_mcp_logic.py
    ```
    *Nota: Este script ejecutará `claim_ticket`. Si quieres ver cambios reflejados, asegúrate que el ID en el script coincida con el de la tarea (por defecto ID=1).*

3.  **Verifica en Frontend**:
    *   Si actualizas la página, el estado de la tarea debería cambiar a **CLAIMED** o el agente debería haber enviado un mensaje.

## 🟢 PASO 5: DEFINITION OF DONE
El sistema se considera "Done" si:
- [ ] Pudiste crear una tarea desde la terminal.
- [ ] La viste en la Web.
- [ ] Pudiste entrar al detalle.
- [ ] La interfaz se siente fluida y libre de errores de consola graves.

---
**Happy Testing! 🚀**
