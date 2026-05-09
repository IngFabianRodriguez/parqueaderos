# SPEC-09-observabilidad-108 — El sistema debe permitir al `tenant_admin` crear ventanas de silencio (mainte...

## Metadata
- **RF origen**: RF-108
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** `tenant_admin` **quiero** configurar ventanas de silencio (maintenance windows) durante las cuales las alertas no se envíen **para** realizar mantenimiento planificado sin que se disparen notificaciones falsas que molesten al equipo de operaciones. ---

## Objetivo
El sistema debe permitir al `tenant_admin` crear ventanas de silencio (maintenance windows) que especifiquen: período de inicio y fin, servicios afectados (o "todos"), y motivo del mantenimiento. Durante estas ventanas, si se generan alertas, el sistema las marca como silenciadas, las almacena en historial, pero **no** las envía a los canales de notificación. Cuando la ventana termina, las alertas silenciadas pueden consultarse en un reporte de "alertas silenciadas por mantenimiento". ---

## Comportamiento Específico

### Happy Path
1. El `tenant_admin` accede a `Observabilidad → Alertas → Ventanas de Silencio`. 2. El sistema muestra las ventanas existentes y un botón "Crear nueva ventana". 3. El admin define la ventana: - `window_name`: Nombre descriptivo (ej: "Mantenimiento database server"). - `start_time`: Fecha y hora de inicio (timezone del tenant). - `end_time`: Fecha y hora de fin. - `affected_services`: Lista de servicios (o "todos"). - `affected_metrics` (opcional): Métricas específicas (ej: solo latencia). - `severities_to_silence`: `[CRITICAL]`, `[WARNING]`, `[INFO]`, o todas. - `notify_on_end`: ¿Enviar resumen al terminar? (boolean). - `reason`: Motivo del mantenimiento (para auditoría). - `ticket_id` (opcional): ID del ticket de mantenimiento en otro sistema. 4. El sistema valida que no haya conflicto con ventanas existentes. 5. La ventana se guarda en `maintenance_windows`. 6. Un worker background verifica cada minuto si alguna ventana debe activarse o desactivarse. 7. Cuando una ventana se activa: - Las alertas de los servicios/métricas afectados se marcan como `SILENCED`. - Las alertas no se envían a ningún canal de notificación. 8. Cuando la ventana termina: - Si `notify_on_end` = true, se envía un resumen de alertas silenciadas. - La ventana se marca como `COMPLETED` en el historial. 9. El admin puede terminar una ventana anticipadamente (opcional). ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `tenant_admin` puede crear, editar, cancelar y consultar ventanas de silencio. 2. Cada ventana especifica: nombre, inicio, fin, servicios afectados, severidades, motivo. 3. Durante la ventana, las alertas de los servicios/severidades afectados se silencian. 4. Las alertas silenciadas se marcan con `silenced: true` y se guardan en historial. 5. Al terminar la ventana, se puede enviar un resumen de alertas silenciadas. 6. Las ventanas se pueden crear con anticipación (ej: programada para mañana a las 10pm). 7. Las ventanas pueden cancelarse anticipadamente. 8. No se permiten ventanas que se crucen en el tiempo para los mismos servicios. 9. Las alertas silenciadas son visibles en el dashboard de alertas con marca de "silenciada". 10. Existe un reporte de "Alertas por Mantenimiento" con historial de ventanas y alertas silenciadas. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/maintenance-windows` — Listar ventanas - `POST /api/v1/tenants/{tenant_id}/maintenance-windows` — Crear ventana - `PUT /api/v1/tenants/{tenant_id}/maintenance-windows/{window_id}` — Editar ventana - `DELETE /api/v1/tenants/{tenant_id}/maintenance-windows/{window_id}` — Cancelar ventana - `PATCH /api/v1/tenants/{tenant_id}/maintenance-windows/{window_id}/extend` — Extender ventana (durante activa) - `GET /api/v1/tenants/{tenant_id}/maintenance-windows/{window_id}/silenced-alerts` — Ver alertas silenciadas - `GET /api/v1/tenants/{tenant_id}/maintenance-windows/history` — Historial de ventanas pasadas ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda que la ventana incluya un buffer de 5-10 min antes del mantenimiento real (para que las alertas de preparación no se envíen). - El campo `ticket_id` permite vincular el mantenimiento con un sistema de tickets externo (ej: Jira). - Para servicios críticos, se puede configurar que las alertas CRITICAL nunca se silencien (override a nivel de servicio). - Las ventanas recurrentes (ej: "todos los domingos 2am-4am") no están en el alcance inicial; pueden agregarse en una versión futura. - El resumen al terminar la ventana (`notify_on_end`) se envía por los mismos canales configurados para alertas normales.
