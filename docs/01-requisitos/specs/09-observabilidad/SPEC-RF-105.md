# SPEC-09-observabilidad-105 — Cada microservicio del sistema debe exponer un endpoint `GET /metrics` que re...

## Metadata
- **RF origen**: RF-105
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** que todos los microservicios expongan sus métricas en formato Prometheus **para** poder integrar con Grafana y visualizar dashboards de monitoreo unificados. ---

## Objetivo
Cada microservicio del sistema debe exponer un endpoint `GET /metrics` que retorne métricas en formato Prometheus (texto plano). Este endpoint debe ser scrapeado por un servidor Prometheus central que recolectará todas las métricas para visualización en Grafana. Las métricas incluyen: health del servicio (RF-100), uso de recursos (RF-103), latencia de APIs (RF-104), y métricas específicas del negocio. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

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
1. Cada microservicio expone `GET /metrics` en el puerto HTTP principal. 2. Las métricas incluyen las estándar de proceso (`process_*`) y las específicas del servicio. 3. El formato es 100% compatible con Prometheus (sin errores de parseo). 4. Prometheus puede hacer scrape cada 15s sin impacto medible en el servicio. 5. Las métricas de un servicio no afectan las de otro (aislamiento). 6. Si el servicio está en mantenimiento y `/health` retorna `DOWN`, `/metrics` también retorna código de error. 7. Las métricas están correctamente etiquetadas con `service_name` y `tenant_id` cuando aplica. 8. Se puede hacer scrape de `/metrics` desde cualquier red interna sin autenticación. ---

## Endpoints
- `GET /metrics` — Endpoint principal de métricas Prometheus - `GET /health` — Health check (ver RF-100) - `GET /api/v1/observability/metrics` — Redirección a `/metrics` (por convención) ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda usar la librería oficial Prometheus client para el lenguaje del servicio. - No exponer métricas con labels de alta cardinalidad (user_id, session_id, transaction_id). - Si el servicio tiene muchos endpoints, usar `path` normalizado (sin IDs) como label. - Para servicios batch o jobs, exponer `job_batch_last_success_timestamp` para monitoreo de jobs. - Las métricas `_total` de tipo counter deben usar el sufijo `_total` por convención de nombres. - Se debe documentar cada métrica con `# HELP` y `# TYPE` para claridad en Prometheus UI.
