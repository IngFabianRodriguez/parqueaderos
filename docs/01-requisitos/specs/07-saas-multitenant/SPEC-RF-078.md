# SPEC-07-078 — Registro de Accesos al Sistema (Quién, Cuándo, Desde Dónde)

## Metadata
- **RF origen**: RF-078
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: auth-service, audit-service

---

## User Story
**Como** administrador de un tenant **quiero** ver un registro de quién accedió al sistema, a qué hora y desde qué dirección IP **para** monitorizar el uso del sistema y detectar accesos no autorizados.

## Objetivo
El sistema debe registrar cada evento de autenticación (login exitoso, logout, login fallido) con datos del usuario, timestamp, dirección IP, user agent, y resultado. Este registro es consultable desde el admin panel.

## Comportamiento Específico

### Eventos registrados
Cada evento de autenticación genera un registro en `login_history`:
- `event_id` (UUID)
- `user_id` (FK)
- `tenant_id` (FK)
- `event_type`: `login_success`, `login_failed`, `logout`, `mfa_challenge`, `session_expired`
- `ip_address`
- `user_agent`
- `device_fingerprint` (si disponible)
- `login_method`: `password`, `sso`, `api_key`
- `failure_reason` (si falló): `invalid_password`, `user_not_found`, `account_locked`, `mfa_failed`
- `timestamp`

### Consulta del registro
1. El `tenant_admin` accede a `Settings → Security → Login History`.
2. Ve la lista de eventos ordenados por timestamp descendente.
3. Filtros: usuario, tipo de evento, rango de fechas.
4. Exportación a CSV/Excel disponible.

## Criterios de Aceptación
1. Todo login exitoso se registra con usuario, IP, user agent y timestamp.
2. Todo login fallido se registra con razón de falla.
3. Los logout y expiraciones de sesión también se registran.
4. El admin puede filtrar por usuario, tipo de evento y rango de fechas.
5. Los datos se retienen por 1 año.
6. Un admin solo ve el historial de usuarios de su tenant.
7. El `superadmin` puede ver el historial de cualquier tenant.