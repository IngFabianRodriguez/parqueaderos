# SPEC-09-observabilidad-114 — El sistema debe calcular y mostrar el uptime real de cada microservicio por m...

## Metadata
- **RF origen**: RF-114
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** tenant_admin **quiero** ver el uptime real de cada microservicio por mes **para** verificar que el servicio cumple con los niveles pactados en mi contrato y tomar acciones correctivas si hay caídas. ---

## Objetivo
El sistema debe calcular y mostrar el uptime real de cada microservicio por mes, definido como: `(minutos disponibles / total minutos del mes) * 100`. Se considera un microservicio "disponible" cuando responde correctamente a su endpoint `/health` con status 200. ---

## Comportamiento Específico

### Happy Path
1. El servicio `monitoring-service` ejecuta health checks de cada microservicio cada 30 segundos 2. Cada health check registra: `microservicio`, `timestamp`, `status` (ok/fail), `response_time_ms` 3. Al final de cada mes, el job `calculate-monthly-uptime` ejecuta: a. Para cada microservicio, cuenta los minutos totales del mes b. Cuenta los minutos donde al menos un health check fue exitoso c. Calcula: `uptime % = (minutos_ok / total_minutos) * 100` 4. El resultado se almacena en la tabla `monthly_uptime` con: `microservicio_id`, `año`, `mes`, `uptime_percentage`, `total_minutes`, `minutes_available`, `calculated_at` 5. El dashboard de SLA consulta estos datos y los muestra por microservicio y mes 6. Se permite comparar el uptime de diferentes meses ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | microservice_id | string | Identificador del microservicio | | year | integer | Año del cálculo | | month | integer | Mes del cálculo (1-12) | | uptime_percentage | decimal | Porcentaje de uptime (ej: 99.95) | | total_minutes | integer | Total de minutos en el mes | | minutes_available | integer | Minutos con al menos un health check exitoso | | minutes_down | integer | Minutos sin health checks exitosos | | incidents_count | integer | Número de incidentes únicos en el mes | | calculated_at | timestamp | Momento del cálculo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | microservice_id | string | Identificador del microservicio | | year | integer | Año del cálculo | | month | integer | Mes del cálculo (1-12) | | uptime_percentage | decimal | Porcentaje de uptime (ej: 99.95) | | total_minutes | integer | Total de minutos en el mes | | minutes_available | integer | Minutos con al menos un health check exitoso | | minutes_down | integer | Minutos sin health checks exitosos | | incidents_count | integer | Número de incidentes únicos en el mes | | calculated_at | timestamp | Momento del cálculo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El uptime se calcula como: minutos disponibles / total minutos del mes 2. Se considera "disponible" un minuto donde al menos un health check fue exitoso 3. El uptime se calcula mensualmente y se almacena con histórico 4. El dashboard permite ver uptime de los últimos 12 meses por microservicio 5. Se puede filtrar por sede si el microservicio es específico de una sede 6. El uptime se muestra con 2 decimales (ej: 99.95%) ---

## Endpoints
- `GET /api/v1/monitoring/uptime?microservice={id}&year={year}&month={month}` — Consulta uptime de un microservicio - `GET /api/v1/monitoring/uptime/history` — Historial de uptime de todos los microservicios - `GET /api/v1/health` — Health check del servicio de monitoreo ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El uptime se calcula considerando zonas horarias del tenant (UTC de la sede principal) - Para contratos Enterprise con SLA de 99.9%, el downtime máximo permitido por mes es ~43 minutos - Se recomienda guardar los health checks crudos por 30 días para auditoría y recalculo si es necesario
