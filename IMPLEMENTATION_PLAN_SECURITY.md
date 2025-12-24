# PLAN DE IMPLEMENTACIÓN: SEGURIDAD, MULTI-AUTH Y REGISTRO (OSIRIS)
**Status: COMPLETED (v1.1.0)**

Este documento detalla las modificaciones necesarias para habilitar un sistema de autenticación híbrido (Interno + Google OAuth2) y registro de usuarios, garantizando la validación del sistema al 100%.

## 1. OBJETIVO
Expandir el sistema Osiris con un ecosistema de identidad dual que permita a los supervisores y administradores registrarse e iniciar sesión de forma segura, ya sea mediante credenciales locales o a través de sus cuentas de Google.

## 2. MODIFICACIONES EN EL BACKEND

### A. Modelos y Base de Datos (`models/user.py`)
*   **Campos**: 
    *   `email`: string (único, indexado).
    *   `full_name`: string.
    *   `hashed_password`: string (Opcional, null si el usuario es exclusivo de Google).
    *   `google_id`: string (Opcional, para vinculación de cuenta).
    *   `is_active`: boolean (por defecto True).
*   **Migración**: Alembic revision para habilitar persistencia de identidad social.

### B. Módulo de Seguridad y OAuth2 (`core/security.py` & `core/auth.py`)
*   **Internal Auth**: Hashing con `bcrypt` y validación de credenciales locales.
*   **Google Auth**: Integración con Google OAuth2 Client. 
    *   Flujo: Redirección -> Callback -> Validación de ID Token -> Emisión de JWT propio de OSIRIS.
*   **JWT Engine**: Emisión de tokens de sesión unificados independientemente del método de entrada.

### C. Endpoints de Identidad (`api/endpoints/auth.py` & `api/endpoints/users.py`)
*   `POST /auth/register`: Registro de nuevas cuentas locales.
*   `POST /auth/login`: Login local (usuario/password).
*   `GET /auth/google`: Trigger para el flujo de Google.
*   `GET /auth/google/callback`: Recepción y validación del login social.

## 3. MODIFICACIONES EN EL FRONTEND

### A. UI de Acceso (`app/login/` & `app/register/`)
*   **Página de Login**: Diseño premium con botones de "Entrar con Google" y formulario tradicional.
*   **Página de Registro**: Formulario de alta para nuevos miembros del equipo de supervisión.
*   **Auth Guard**: Componente global `AuthGuard` para protección de rutas.

### B. Lógica de Sesión (`hooks/useAuth.ts`)
*   Manejo de estado reactivo con **Zustand**.
*   Inyección automática de JWT en `lib/api.ts`.
*   Protección de rutas vía Middleware/AuthGuard.

## 4. REQUISITOS DE INFRAESTRUCTURA
*   **Google Cloud Console**: Configuración de `GOOGLE_CLIENT_ID`.
*   **Protocolos**: URLs de callback coordinadas entre Frontend y Backend.

## 5. SOLICITUD DE CIERRE
Este plan se considera implementado exitosamente tras la verificación de los ciclos de testing.
