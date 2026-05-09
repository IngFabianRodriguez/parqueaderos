# SPEC-09-observabilidad-115 — El sistema debe mostrar visualmente (con color rojo) aquellos microservicios ...

## Metadata
- **RF origen**: RF-115
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin **quiero** ver一眼就知道哪些 servicios están por debajo del SLA contratado **para** actuar rápidamente y evitar incumplimientos contractuales con mis clientes. ---

## Objetivo
El sistema debe mostrar visualmente (con color rojo) aquellos microservicios cuyo uptime del mes actual esté por debajo del SLA contratado. El SLA default para planes Enterprise es 99.9%. Si el uptime real está por debajo del umbral, el servicio se marca en rojo en el dashboard. ---

## Comportamiento Específico

### Happy Path
1. El servicio `monitoring-service` obtiene el uptime mensual calculado (RF-114) para cada microservicio 2. Para cada microservicio, obtiene el SLA contratado de la configuración del tenant 3. Compara: `uptime_real vs sla_threshold` a. Si `uptime_real >= sla_threshold`: color verde (cumplimiento) b. Si `uptime_real < sla_threshold`: color rojo (incumplimiento) 4. El dashboard consulta `GET /api/v1/dashboard/sla-status` que retorna la lista de servicios con su estado 5. El frontend renderiza cada servicio con el color correspondiente 6. Si un servicio pasa de verde a rojo, se genera una alerta `sla_breach` por el canal configurado 7. El dashboard también muestra el porcentaje de uptime al lado del color para contexto ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | microservice_id | string | Identificador del microservicio | | microservice_name | string | Nombre legible del microservicio | | uptime_percentage | decimal | Uptime real del mes actual | | sla_threshold | decimal | Umbral contratado | | sla_status | enum | `compliant` (verde), `breached` (rojo), `unknown` (gris) | | downtime_minutes | integer | Minutos de downtime en el mes | | breach_alert_sent | boolean | Si ya se envió alerta de SLA breach | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | microservice_id | string | Identificador del microservicio | | microservice_name | string | Nombre legible del microservicio | | uptime_percentage | decimal | Uptime real del mes actual | | sla_threshold | decimal | Umbral contratado | | sla_status | enum | `compliant` (verde), `breached` (rojo), `unknown` (gris) | | downtime_minutes | integer | Minutos de downtime en el mes | | breach_alert_sent | boolean | Si ya se envió alerta de SLA breach | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todo microservicio con uptime < SLA se muestra en color rojo en el dashboard 2. Todo microservicio con uptime >= SLA se muestra en color verde 3. El color rojo aparece dentro de las 24 horas posteriores al momento en que el uptime cae por debajo del SLA 4. El dashboard muestra el porcentaje de uptime junto al indicador de color 5. Se genera una alerta `sla_breach` cuando un servicio cae por debajo del SLA 6. El indicador es visible en la vista principal del dashboard sin necesidad de drill-down ---

## Endpoints
- `GET /api/v1/dashboard/sla-status` — Estado SLA de todos los servicios - `GET /api/v1/monitoring/uptime/{microservice_id}?month={month}` — Detalle de uptime de un servicio - `GET /api/v1/tenants/{tenant_id}/sla` — Configuración de SLA del tenant ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El umbral de SLA es configurable por tenant_admin desde el módulo de administración - Para contratos con SLA diferenciado por servicio (ej: API Gateway 99.99%, otros 99.9%), se permite configurar por microservicio - El color rojo se mantiene hasta que el servicio recupere el uptime o el admin marque la alerta como `acknowledged`
