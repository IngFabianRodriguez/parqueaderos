# SPEC-06-026 — Autenticación de Usuarios con JWT y Roles Diferenciados

## Metadata
- **RF origen**: RF-026
- **Módulo**: 06-seguridad
- **Prioridad**: Alta
- **Servicios**: auth-service, user-service, gateway-service

---

## User Story
**Como** administrador del sistema **quiero** que cada usuario sea autenticado con credenciales seguras y tenga un rol definido **para** garantizar que solo personas autorizadas accedan a funciones apropiadas según su responsabilidad.

## Objetivo
El sistema debe implementar un mecanismo de autenticación basado en JSON Web Tokens (JWT) que permita identificar y autorizar a los usuarios según cuatro roles diferenciados: superadmin, admin_sede, operador y cliente. El sistema debe soportar flujo de login/logout, refresh de tokens, y MFA opcional para roles sensibles.

## Comportamiento Específico

### Happy Path
1. Usuario navega a la página de login y complete formulario con email y contraseña
2. Sistema valida que el email exista y la contraseña coincida (bcrypt cost factor 12)
3. Si rol es superadmin/admin_sede y MFA habilitado: sistema envía código TOTP
4. Usuario ingresa código MFA de 6 dígitos
5. Sistema genera JWT con claims del usuario y TTL de 15 minutos
6. Sistema genera refresh token con TTL de 7 días y lo almacena
7. Sistema retorna access_token y refresh_token
8. Cliente almacena ambos tokens y envía access_token en header Authorization en todas las requests

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Refresh token expirado | Retorna 401 y obliga re-autenticarse |
| Refresh token usado > 5 veces | Invalida toda la familia de tokens, requiere re-login |
| Refresh token revoked | Retorna 401, cliente debe redirigir a login |
| Usuario desactivado/suspendido | Retorna 403: "Cuenta suspendida. Contacte al administrador." |
| Tenant inactivo | Retorna 403: "Tenant inactivo. Contacte soporte." |
| 5 intentos fallidos en 10 min | Bloquea cuenta por 15 min y envía email de alerta |
| MFA configurado pero no enviado | Retorna 428 cuando el factor es requerido |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| email | string | Correo electrónico del usuario | Sí |
| password | string | Contraseña (mín 8 caracteres) | Sí |
| mfa_code | string | Código TOTP de 6 dígitos | Condicional (si MFA habilitado) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| access_token | string | JWT con claims del usuario |
| refresh_token | string | Token opaco para refresh |
| expires_in | integer | TTL del access token en segundos (900 = 15 min) |
| token_type | string | Siempre "Bearer" |
| user | object | Datos públicos del usuario (id, nombre, email, rol) |

### Estructura del JWT Claims
```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "rol": "admin_sede",
  "sede_ids": ["sede_uuid_1", "sede_uuid_2"],
  "permisos": ["reports:read", "gate:operate"],
  "iat": 1715250000,
  "exp": 1715250900
}
```

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un usuario con credenciales válidas recibe un JWT válido y puede hacer requests autenticadas durante 15 minutos
2. El JWT contiene todos los claims necesarios (user_id, tenant_id, rol, sede_ids, permisos)
3. Un superadmin tiene acceso a todas las sedes; admin_sede solo a las asignadas; operador solo a las asignadas; cliente solo a sus propios datos
4. Cuando el access token expira, el cliente puede usar el refresh token para obtener uno nuevo
5. Un intento de acceso con credenciales inválidas no revela si el email existe (mensaje genérico)
6. Después de 5 intentos fallidos, la cuenta se bloquea 15 minutos y se notifica al usuario
7. El login con MFA para superadmin requiere código TOTP válido además de credenciales
8. El logout revoca el refresh token y el sistema rechaza intentos de usar tokens revocados

## Endpoints
- `POST /api/v1/auth/login` — Inicio de sesión (retorna access + refresh token)
- `POST /api/v1/auth/refresh` — Refresca el access token
- `POST /api/v1/auth/logout` — Revoca el refresh token
- `POST /api/v1/auth/mfa/setup` — Inicia configuración de MFA
- `POST /api/v1/auth/mfa/verify` — Verifica código MFA durante login
- `GET /api/v1/auth/me` — Retorna información del usuario autenticado

## Health Check
- `GET /health` → { "status": "ok" }