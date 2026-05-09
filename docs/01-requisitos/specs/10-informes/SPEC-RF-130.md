# SPEC-10-informes-130 — El sistema debe mantener un log detallado de cada ejecución de reporte progra...

## Metadata
- **RF origen**: RF-130
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede **quiero** consultar el historial de reportes programados que han sido entregados **para** auditar qué reportes se enviaron, cuándo, a quién y en qué estado. ---

## Objetivo
El sistema debe mantener un log detallado de cada ejecución de reporte programado, incluyendo: destinatario, fecha y hora de entrega, formato del archivo, tamaño, estado (entregado, fallido, reintentado) y mensaje de error si aplica. Este log debe ser consultable por el administrador y persistir durante al menos 90 días. ---

## Comportamiento Específico

### Happy Path
1. Cada vez que se ejecuta un reporte programado (RF-129), el sistema registra un entry en el log de entregas. 2. El log se escribe tanto en éxito como en falla de la entrega. 3. El usuario accede a la sección "Log de Entregas" dentro del módulo de informes. 4. El usuario puede filtrar por: - Programa de reporte específico. - Destinatario (email). - Estado: ENTREGADO, FALLIDO, REINTENTADO, PENDIENTE. - Rango de fechas. 5. El sistema retorna la lista de registros paginados ordenados por fecha descendente. 6. Por cada registro se puede ver el detalle expandido incluyendo mensaje de error si falló. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | registro_id | UUID | Identificador único del log | | programa_id | UUID | ID del programa que ejecutó | | nombre_programa | String | Nombre del programa | | nombre_reporte | String | Nombre del reporte base | | destinatario | String | Email del destinatario | | fecha_programada | DateTime | Hora que estaba programada la ejecución | | fecha_ejecucion | DateTime | Timestamp cuando realmente se ejecutó | | fecha_entrega | DateTime | Timestamp cuando se entregó (null si falló) | | formato | Enum | XLSX, CSV, PDF | | tamano_bytes | Integer | Tamaño del archivo en bytes | | estado | Enum | ENTREGADO, FALLIDO, REINTENTADO, PENDIENTE | | intentos | Integer | Número de intentos realizados | | mensaje_error | String | Descripción del error si falló | | error_codigo | String | Código de error si aplica (ej: EMAIL_REJECTED, TIMEOUT) | | ejecutor | UUID | ID del usuario que creó el programa | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | registro_id | UUID | Identificador único del log | | programa_id | UUID | ID del programa que ejecutó | | nombre_programa | String | Nombre del programa | | nombre_reporte | String | Nombre del reporte base | | destinatario | String | Email del destinatario | | fecha_programada | DateTime | Hora que estaba programada la ejecución | | fecha_ejecucion | DateTime | Timestamp cuando realmente se ejecutó | | fecha_entrega | DateTime | Timestamp cuando se entregó (null si falló) | | formato | Enum | XLSX, CSV, PDF | | tamano_bytes | Integer | Tamaño del archivo en bytes | | estado | Enum | ENTREGADO, FALLIDO, REINTENTADO, PENDIENTE | | intentos | Integer | Número de intentos realizados | | mensaje_error | String | Descripción del error si falló | | error_codigo | String | Código de error si aplica (ej: EMAIL_REJECTED, TIMEOUT) | | ejecutor | UUID | ID del usuario que creó el programa | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El log registra cada ejecución de reporte programado, tanto exitoso como fallido. 2. Cada registro contiene: destinatario, fecha/hora, formato, tamaño, estado y mensaje de error si falló. 3. El log es consultable con filtros por programa, destinatario, estado y rango de fechas. 4. El log persiste durante al menos 90 días; después de 90 días se archiva o elimina. 5. Un administrador puede ver los logs de todos los programas de su sede. 6. Los registros de log no son editables ni eliminables por usuarios (son audit trail). 7. Los logs pueden exportarse a CSV para auditoría externa. ---

## Endpoints
- `GET /api/v1/reports/delivery-log` — Lista los registros del log con filtros - `GET /api/v1/reports/delivery-log/{id}` — Detalle de un registro específico - `GET /api/v1/reports/delivery-log/export` — Exporta el log a CSV - `GET /api/v1/reports/schedules/{id}/delivery-history` — Historial de entregas de un programa específico ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El log es de solo adición; no se permiteupdate ni delete de registros existentes. - Los registros de log incluyen un campo `ejecutor` que muestra quién creó el programa, no quién recibió el reporte. - Para programas con múltiples destinatarios, se crea un registro por destinatario. - El campo `fecha_entrega` es null cuando el estado es FALLIDO o REINTENTADO; solo se populate cuando el estado es ENTREGADO. - Se recomienda implementar rotación de logs: архивировать registros mayores a 90 días a una tabla de histórico para compliance.
