# SPEC-06-027 — Logueo de Acciones Sensibles en Auditoría Inmutable

## Metadata
- **RF origen**: RF-027
- **Módulo**: 06-seguridad
- **Prioridad**: Alta
- **Servicios**: audit-service, gateway-service, auth-service, todos los servicios

---

## User Story
**Como** superadmin **quiero** que todas las acciones sensibles del sistema queden registradas en un log inmutable **para** poder investigar incidentes, demostrar cumplimiento regulatorio y auditar el comportamiento de usuarios y operadores.

## Objetivo
El sistema debe registrar en un log de auditoría todas las acciones que impliquen modificación de datos sensibles, errores de seguridad, o cambios en la configuración. Este log debe ser inmutable y solo permitir consultas de lectura con permisos elevados.

## Comportamiento Específico

### Happy Path
1. Un servicio detecta que una acción sensible está por ejecutarse o ya se ejecutó
2. El servicio construye el objeto AuditEvent con todos los campos requeridos
3. El servicio incluye un correlation_id para trazabilidad distributed
4. El servicio envía el evento al audit-service vía gRPC o mensaje Kafka
5. El audit-service persiste el evento en la tabla audit_logs con fecha de ingestión
6. Para acciones CRITICAL: el evento se replica en storage separado inmutable (WORM) después de 24h

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Base de datos de auditoría no disponible | Se escribe a cola fallback (Kafka); si también falla, se escribe a filesystem local (emergency.log) |
| Query con rango > 90 días | Sistema rechaza: "El rango máximo es 90 días" |
| Admin de sede intenta ver logs de otra sede | Retorna 403 Forbidden |
| Payload > 64KB | Se trunca a 64KB y se marca payload_truncated: true |
| Intento de borrado de log por usuario | El sistema NO permite DELETE/UPDATE; cualquier intento genera evento AUDIT_TAMPERING_ATTEMPT |
| Overflow de cola de auditoría | Modo degraded: solo eventos CRITICAL se procesan síncronamente |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| timestamp | datetime | Momento del evento (UTC, ISO 8601) | Sí |
| actor_id | UUID | ID del usuario que realizó la acción | Sí |
| actor_email | string | Email del actor | Sí |
| actor_rol | enum | Rol del actor al momento del evento | Sí |
| accion | enum | Tipo de acción (catálogo) | Sí |
| recurso | string | Nombre del recurso afectado | Sí |
| recurso_id | UUID | ID del recurso afectado | Condicional |
| tenant_id | UUID | ID del tenant | Sí |
| sede_id | UUID | ID de la sede | Condicional |
| IP | string | Dirección IP del cliente | Sí |
| payload | JSON | Detalles específicos de la acción | No |
| correlation_id | UUID | ID para trazabilidad distributed | Sí |
| resultado | enum | SUCCESS, FAILURE, PARTIAL | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único del log |
| timestamp | datetime | Momento del evento |
| actor_id | UUID | ID del actor |
| actor_email | string | Email del actor |
| accion | enum | Tipo de acción |
| recurso | string | Recurso afectado |
| recurso_id | UUID | ID del recurso |
| tenant_id | UUID | ID del tenant |
| IP | string | IP del cliente |
| payload | JSON | Detalles |
| correlation_id | UUID | Correlation ID |
| resultado | enum | SUCCESS/FAILURE/PARTIAL |
| ingestion_timestamp | datetime | Momento en que se persistió |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Toda acción sensible listada en el catálogo genera un registro en audit_logs con todos los campos requeridos
2. Los logs de auditoría son inmutables: no existe endpoint DELETE ni UPDATE para la tabla audit_logs
3. Un superadmin puede consultar logs de cualquier sede del tenant con filtros
4. Un admin_sede solo puede consultar logs de las sedes asignadas a su usuario
5. Los eventos de autenticación (login, logout, MFA) se persisten síncronamente (FAIL-Closed)
6. Un intento de tampering (UPDATE/DELETE en audit_logs) genera alerta y se rechaza
7. Los logs se pueden exportar a CSV/JSON con filtros aplicados

## Endpoints
- `GET /api/v1/audit/logs` — Consulta paginada de logs (filtros: fecha_inicio, fecha_fin, actor_id, accion, recurso, recurso_id, sede_id)
- `GET /api/v1/audit/logs/{id}` — Detalle de un log específico
- `GET /api/v1/audit/logs/export` — Exportación a CSV/JSON (máx 90 días, async)
- `GET /api/v1/audit/stats` — Estadísticas agregadas

## Health Check
- `GET /health` → { "status": "ok" }