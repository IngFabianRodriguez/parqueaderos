# SPEC-07-073 — Bloqueo de Usuarios tras 5 Intentos Fallidos de Login

## Metadata
- **RF origen**: RF-073
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: auth-service, user-service

---

## User Story
**Como** administrador de un tenant **quiero** que después de 5 intentos fallidos de login la cuenta del usuario se bloquee temporalmente **para** proteger contra ataques de fuerza bruta y credential stuffing.

## Objetivo
El sistema debe bloquear una cuenta después de 5 intentos fallidos consecutivos de login. El bloqueo dura 15 minutos, después de los cuales la cuenta se desbloquea automáticamente. Cada login exitoso reinicia el contador. El `tenant_admin` puede desbloquear manualmente.

## Comportamiento Específico

### Intento de Login
1. El usuario ingresa email y password.
2. Si el usuario tiene `status = blocked`: verificar si `locked_until` expiró. Si no expiró, retornar error 423.
3. El sistema verifica el password:
   - Si es incorrecto: `failed_login_attempts += 1`.
   - Si `failed_login_attempts >= 5`: establecer `locked_until = now() + 15 min`.
4. Si el password es correcto: `failed_login_attempts = 0`; continuar con MFA si está habilitado.

### Desbloqueo manual por Admin
1. El `tenant_admin` accede a `Settings → Users → [Usuario] → Unlock Account`.
2. Confirma la acción.
3. El sistema establece `locked_until = null` y `failed_login_attempts = 0`.
4. Se registra en `audit_log`.

## Criterios de Aceptación
1. Después de 5 intentos fallidos de password, la cuenta se bloquea por 15 minutos.
2. Los intentos fallidos se cuentan por usuario, no por IP.
3. Un login exitoso reinicia el contador de intentos fallidos a 0.
4. El usuario recibe mensaje indicando tiempo restante para desbloqueo.
5. El `tenant_admin` puede desbloquear manualmente cualquier usuario.
6. Los intentos fallidos se registran para auditoría (IP, timestamp, user agent).
7. Si el tenant tiene MFA obligatorio, el contador de intentos aplica al primer factor.

## Datos de Entrada
- **email** — Email del usuario que intenta hacer login (string, required)
- **password** — Password proporcionado por el usuario (string, required)
- **ip_address** — Dirección IP del cliente (string, auto-capturada)
- **user_agent** — User agent del navegador/cliente (string, auto-capturada)

## Datos de Salida
- **failed_login_attempts** — Contador de intentos fallidos actualizado (integer)
- **locked_until** — Timestamp hasta el cual la cuenta está bloqueada (timestamp, null si no está bloqueado)
- **status** — Estado de la cuenta: `active`, `blocked` (enum)
- **audit_log** — Entrada con `event_type = login_failed`, `ip_address`, `timestamp`, `failure_reason`
- **Respuesta** — 401 Unauthorized o 423 Locked según corresponda