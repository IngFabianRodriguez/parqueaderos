# SPEC-09-observabilidad-111 — El sistema debe generar una alerta inmediata cuando una talanquera reporta es...

## Metadata
- **RF origen**: RF-111
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sistema de monitoreo **quiero** detectar cuando una talanquera reporta error o deja de responder por más de 2 minutos **para** alertar inmediatamente al tenant_admin y evitar que vehículos queden varados en la entrada o salida del parqueadero. ---

## Objetivo
El sistema debe generar una alerta inmediata cuando una talanquera reporta estado de `error` o cuando no responde durante más de 2 minutos. Esta alerta debe enviarse por el canal configurado (email, SMS, Slack o webhook) de forma prioritaria, sin respetar ventanas de silencio (maintenance windows) salvo que el dispositivo esté explícitamente en modo mantenimiento. ---

## Comportamiento Específico

### Happy Path
1. El sistema monitoriza continuamente el estado de todas las talanqueras 2. Caso A — Talanquera reporta `status=error`: a. El servicio `device-monitor` recibe el evento de error b. Se genera inmediatamente una alerta `device_failure` con nivel `critical` c. La alerta incluye: `device_id`, `talanquera_nombre`, `error_type`, `timestamp` d. Se envía por todos los canales activos del tenant_admin 3. Caso B — Talanquera no responde por más de 2 minutos: a. Un job de verificación ejecuta cada 30 segundos b. Si `now - last_command_response_at > 2 minutos` y no hay `status=maintenance` c. Se genera alerta `device_no_response` con nivel `critical` d. Se incluye información del último comando pendiente 4. La alerta queda abierta hasta que: a. La talanquera confirma respuesta (comando completado) b. Un operador marca la alerta como `acknowledged` desde el admin o app móvil c. Se detecta que la talanquera pasó a modo `maintenance` 5. Al resolverse, se genera un evento `alert_resolved` en el audit log ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | alert_id | UUID | Identificador único de la alerta | | device_id | UUID | Identificador de la talanquera | | alert_type | enum | `device_failure` (error reportado) / `device_no_response` (timeout) | | severity | enum | `critical` | | message | string | Descripción de la alerta | | created_at | timestamp | Momento de creación | | resolved_at | timestamp | Momento de resolución (null si está abierta) | | resolved_by | UUID | Usuario que resolvió (null si está abierta) | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | alert_id | UUID | Identificador único de la alerta | | device_id | UUID | Identificador de la talanquera | | alert_type | enum | `device_failure` (error reportado) / `device_no_response` (timeout) | | severity | enum | `critical` | | message | string | Descripción de la alerta | | created_at | timestamp | Momento de creación | | resolved_at | timestamp | Momento de resolución (null si está abierta) | | resolved_by | UUID | Usuario que resolvió (null si está abierta) | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Toda talanquera que reporte `status=error` genera alerta inmediata (< 5 segundos después del reporte) 2. Toda talanquera sin respuesta por 2 minutos genera alerta `device_no_response` 3. Las alertas `critical` se envían por todos los canales configurados sin respetar ventanas de silencio 4. El tenant_admin recibe la alerta con información suficiente para actuar: dispositivo, sede, error/tipo, última acción 5. El operador puede ver las alertas activas en el dashboard y en la app móvil 6. El sistema permite marcar la alerta como `acknowledged` para rastreo ---

## Endpoints
- `GET /api/v1/alerts?status=active&type=device_failure,device_no_response` — Lista alertas activas - `PATCH /api/v1/alerts/{alert_id}` — Actualiza estado de alerta (acknowledge/resolve) - `GET /api/v1/devices/{device_id}/history` — Historial de eventos de un dispositivo ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las alertas de falla de talanquera tienen nivel `critical` y no respean ventanas de silencio para garantizar respuesta inmediata - Se puede configurar un "escalation policy": si la alerta no es reconocida en 5 minutos, se escala a otro usuario - La integración con sistemas de terceros (central de monitoreo, CCTV) se puede hacer via webhook (RF-164)
