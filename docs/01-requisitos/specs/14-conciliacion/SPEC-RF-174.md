# SPEC-14-conciliacion-174 — El sistema debe enviar una notificación inmediata al administrador de sede cu...

## Metadata
- **RF origen**: RF-174
- **Módulo**: 14-conciliacion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede **quiero** recibir una notificación cuando un operador hace cierre de turno **para** estar informado de la actividad en mi sede y poder supervisar los cierres en tiempo real. ---

## Objetivo
El sistema debe enviar una notificación inmediata al administrador de sede cuando un operador completa el cierre de turno. La notificación debe incluir los datos clave del cierre (operador, turno, resumen) y un enlace directo al reporte PDF generado. ---

## Comportamiento Específico

### Happy Path
1. Sistema detecta cierre de turno completado exitosamente 2. Sistema identifica al administrador(es) de sede asociados a la sede del operador 3. Sistema recolecta datos para la notificación: - Nombre del operador - Hora de inicio y cierre del turno - Total de ingresos del turno - Resultado de conciliación (conciliado / discrepancy) - Enlace al PDF del reporte 4. Sistema determina canales de notificación según preferencias del admin: - Email (si configurado) - Push notification (si tiene app móvil) - Slack (si configurado, ver RF-166) - SMS (si configurado, ver RF-166) 5. Sistema envía notificación por cada canal habilitado 6. Sistema registra en audit log: - Operador que cerró - Admin que recibió notificación - Canal utilizado - Timestamp - Contenido de la notificación ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | notificacion_id | UUID | Identificador de la notificación | | canales_utilizados | Array[Enum] | Canales por los que se envió (email, push, slack, sms) | | estado_envio | Enum | "enviado" / "fallido" / "pendiente_reintento" | | timestamp_envio | Timestamp | Fecha y hora del envío | | admin_receptor | UUID | ID del admin que recibió | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | notificacion_id | UUID | Identificador de la notificación | | canales_utilizados | Array[Enum] | Canales por los que se envió (email, push, slack, sms) | | estado_envio | Enum | "enviado" / "fallido" / "pendiente_reintento" | | timestamp_envio | Timestamp | Fecha y hora del envío | | admin_receptor | UUID | ID del admin que recibió | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La notificación se envía dentro de los 60 segundos posteriores al cierre del turno 2. Todos los canales configurados para el admin reciben la notificación 3. La notificación incluye siempre los datos clave del turno 4. El enlace al PDF es accesible y válido por al menos 30 días 5. El admin puede silenciar notificaciones de cierre de turno (configuración personal) 6. Se mantiene historial de todas las notificaciones enviadas ---

## Endpoints
- `GET /api/v1/notificaciones/historial?sede_id={sede_id}&tipo=CIERRE_TURNO` — Consultar historial de notificaciones de cierre - `PUT /api/v1/admin/preferencias/canales` — Actualizar canales de notificación preferidos - `POST /api/v1/notificaciones/reenviar/{notificacion_id}` — Reenviar una notificación (admin) ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El admin de sede puede delegar la recepción de notificaciones a otro usuario - Las notificaciones de cierre con discrepancia tienen prioridad más alta (se envían primero) - Se puede configurar un "horario silencioso" donde las notificaciones se acumulan y envían al día siguiente - La notificación por SMS es solo para casos de discrepancia (no para cierres normales) para reducir costos
