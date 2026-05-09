# SPEC-15-soporte-177 — Implementar un sistema de monitoreo y tracking del SLA (Service Level Agreeme...

## Metadata
- **RF origen**: RF-177
- **Módulo**: 15-soporte
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de sede **quiero** ver el estado del SLA de cada ticket **para** asegurar que todos los tickets se atiendan dentro de los tiempos comprometidos y evitar penalizaciones por incumplimiento. ---

## Objetivo
Implementar un sistema de monitoreo y tracking del SLA (Service Level Agreement) para cada ticket de soporte, midiendo tiempo de primera respuesta y tiempo total de resolución. El sistema debe mostrar visualmente el estado del SLA, alertar cuando se aproxime al límite y generar reportes de cumplimiento. ---

## Comportamiento Específico

### Happy Path
1. Al crearse un ticket (RF-175), el sistema registra `fecha_creacion` y calcula `fecha_limite_primera_respuesta` según prioridad: - Alta: 4 horas desde creación - Media: 24 horas desde creación - Baja: 72 horas desde creación 2. Sistema también calcula `fecha_limite_resolucion`: - Alta: 24 horas desde creación - Media: 72 horas desde creación - Baja: 168 horas (7 días) desde creación 3. Operador ve en su panel de tickets una columna/barra visual de estado del SLA: - Verde: > 50% del tiempo disponible restante - Amarillo: 25-50% del tiempo disponible restante - Rojo: < 25% del tiempo disponible restante - Rojo pulsante: SLA ya incumplido 4. Sistema genera alertas automáticas: - A los 2/3 del tiempo límite: notificación push al operador - A 1 hora del límite: alerta urgente en panel con sonido - Al vencer el SLA: generación de ticket de escalamiento automático a admin_sede 5. Cuando operador responde por primera vez, sistema registra `primera_respuesta_at` y calcula `sla_primera_respuesta_cumplido` (boolean) 6. Cuando ticket cambia a estado "resuelto" o "cerrado", sistema registra `resuelto_at` y calcula `sla_resolucion_cumplido` (boolean) 7. Admin puede acceder a dashboard de métricas SLA con resumen de cumplimiento por sede, por operador, por período ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | Identificador del ticket | | sla_estado | enum | dentro_sla, warning, critico, incumplido | | tiempo_restante_primera_respuesta | interval | Tiempo restante para primera respuesta | | tiempo_restante_resolucion | interval | Tiempo restante para resolución | | sla_primera_respuesta_cumplido | boolean | true si se cumplió, null si aún no hay respuesta | | sla_resolucion_cumplido | boolean | true si se cumplió, null si aún no está resuelto | | primera_respuesta_at | datetime | Timestamp de la primera respuesta (null si no hay) | | resuelto_at | datetime | Timestamp de resolución (null si no resuelto) | | porcentaje_tiempo_utilizado | integer | Porcentaje del SLA ya consumido | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | uuid | Identificador del ticket | | sla_estado | enum | dentro_sla, warning, critico, incumplido | | tiempo_restante_primera_respuesta | interval | Tiempo restante para primera respuesta | | tiempo_restante_resolucion | interval | Tiempo restante para resolución | | sla_primera_respuesta_cumplido | boolean | true si se cumplió, null si aún no hay respuesta | | sla_resolucion_cumplido | boolean | true si se cumplió, null si aún no está resuelto | | primera_respuesta_at | datetime | Timestamp de la primera respuesta (null si no hay) | | resuelto_at | datetime | Timestamp de resolución (null si no resuelto) | | porcentaje_tiempo_utilizado | integer | Porcentaje del SLA ya consumido | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Cada ticket muestra visualmente su estado de SLA en el panel del operador (colores verde/amarillo/rojo) 2. Alertas automáticas se generan y envían al operador según los umbrales definidos 3. Métricas de SLA (cumplimiento/no cumplimiento) quedan registradas para cada ticket 4. Admin puede ver dashboard con % de cumplimiento de SLA por sede en tiempo real 5. Reporte de SLA es exportable a CSV/Excel con filtros por período, sede, prioridad 6. Cálculo de SLA considera timezone de la sede para correcto manejo de horas límite ---

## Endpoints
- `GET /api/v1/soporte/tickets/{ticket_id}/sla` — Obtener estado SLA actual de un ticket - `GET /api/v1/soporte/sla/dashboard?sede_id={id}&from={date}&to={date}` — Dashboard de métricas SLA - `GET /api/v1/soporte/sla/reportes/export?formato=csv` — Exportar reporte de SLA ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las métricas de SLA se recalculan cada vez que hay un cambio de estado en el ticket - El dashboard de SLA debe ser accesible también desde el admin panel para operadores multi-sede - Los colores de estado en el panel deben ser consistentes: verde (#22c55e), amarillo (#eab308), rojo (#ef4444) - Las alertas de SLA vencido deben crear un registro de incidencia separado para auditoría de cumplimiento - El tenant admin puede personalizar los umbrales de SLA por plan (Enterprise puede tener SLAs más estrictos)
