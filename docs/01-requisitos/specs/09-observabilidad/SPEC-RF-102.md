# SPEC-09-observabilidad-102 — El sistema debe monitorear continuamente la disponibilidad y latencia de cada...

## Metadata
- **RF origen**: RF-102
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** que el sistema detecte automáticamente cuando un microservicio deja de responder o su latencia supera el umbral normal **para** recibir alertas oportunas y tomar acción antes de que los clientes notifiquen la falla. ---

## Objetivo
El sistema debe monitorear continuamente la disponibilidad y latencia de cada microservicio. Cuando un microservicio deja de responder por completo, se genera una alerta **CRITICAL** inmediatamente. Cuando la latencia supera el doble del baseline (p95 histórico), se genera una alerta **WARNING**. Las alertas se envían a través de los canales configurados (email, SMS, Slack, webhook) según lo definido en RF-107. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
|| Campo | Tipo | Descripción | |---|-------|------|-------------| | alert_id | uuid | Identificador único de la alerta | | type | enum | `SERVICE_DOWN`, `SERVICE_DEGRADED`, `SERVICE_RECOVERY`, `LATENCY_RECOVERED` | | severity | enum | `CRITICAL`, `WARNING`, `INFO` | | service_id | string | ID del servicio afectado | | timestamp | datetime | Momento de la detección | | payload | object | Datos específicos del tipo de alerta | ---

## Datos de Salida
|| Campo | Tipo | Descripción | |---|-------|------|-------------| | alert_id | uuid | Identificador único de la alerta | | type | enum | `SERVICE_DOWN`, `SERVICE_DEGRADED`, `SERVICE_RECOVERY`, `LATENCY_RECOVERED` | | severity | enum | `CRITICAL`, `WARNING`, `INFO` | | service_id | string | ID del servicio afectado | | timestamp | datetime | Momento de la detección | | payload | object | Datos específicos del tipo de alerta | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Una alerta CRITICAL se genera en menos de 60s desde que un servicio deja de responder. 2. Una alerta WARNING se genera en menos de 5 min desde que la latencia supera el umbral. 3. Cada alerta incluye: servicio, timestamp, tipo, severidad y datos de contexto. 4. Las alertas se envían por todos los canales configurados para el tenant. 5. Si un servicio recupera, se envía una notificación de `RECOVERY`. 6. El sistema no genera alertas por spikes momentáneos (requiere consistencia). 7. Las alertas pueden ser silenciadas temporalmente (maintenance windows, RF-108). 8. Existe una vista de historial de alertas para las últimas 24h. 9. El operador puede reconocer (acknowledge) una alerta para indicar que está trabajando en ella. ---

## Endpoints
- `GET /api/v1/observability/alerts` — Listar alertas activas y recientes - `POST /api/v1/observability/alerts/{alert_id}/acknowledge` — Reconocer alerta - `POST /api/v1/observability/alerts/{alert_id}/silence` — Silenciar alerta (con ventana de tiempo) - `GET /api/v1/observability/alerts/{alert_id}/history` — Historial de cambios de estado - `GET /api/v1/observability/services/{service_id}/latency-history` — Historial de latencia para dashboards ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Para evitar falsos positivos por spikes de red, se requiere que la latencia超标 ocurra en 2 de 3 lecturas consecutivas antes de generar WARNING. - El `baseline_p95` se recalcula cada 5 minutos usando un sliding window de 24h. - Las alertas de tipo CRITICAL tienen deduplicación de 1min; WARNING de 5min. - El campo `affected_endpoints` en el payload indica qué endpoints de negocio podrían verse afectados (estimado a partir de la arquitectura del servicio).
