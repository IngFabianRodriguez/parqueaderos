# SPEC-09-observabilidad-104 — El sistema debe trackear métricas de rendimiento a nivel de aplicación: laten...

## Metadata
- **RF origen**: RF-104
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** ver las métricas de latencia del API Gateway, tiempo de respuesta de cada endpoint y throughput (req/min) **para** identificar bottlenecks, optimizar rendimiento y verificar que los SLAs se cumplen. ---

## Objetivo
El sistema debe trackear métricas de rendimiento a nivel de aplicación: latencia del API Gateway (tiempo total de la request), tiempo de respuesta desagregado por endpoint (downstream), y throughput medido en requests por minuto. Estas métricas permiten crear dashboards de rendimiento, establecer baselines de latencia y detectar degradación de rendimiento. ---

## Comportamiento Específico

### Happy Path
1. El API Gateway middleware intercepta cada request entrante y registra: - `request_timestamp` (inicio) - `http_method`, `path`, `status_code` - `tenant_id`, `user_id` (si autenticado) 2. Al completar la request, se calcula: - `latency_ms`: tiempo total desde que entró al gateway hasta que se respondió - `upstream_latency_ms`: tiempo que tomó el microservicio destino 3. El middleware envía la métrica a Prometheus con labels. 4. Cada microservicio también instrumenta sus handlers internos y envía `http_request_duration_seconds` con labels adicionales: `service_name`, `endpoint`, `method`. 5. Se calculan agregaciones: p50, p95, p99, throughput por endpoint. ---

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
1. La latencia del API Gateway se mide desde el primer byte del request hasta el último byte del response. 2. Cada endpoint tiene métricas de: count, p50, p95, p99, min, max latencia. 3. El throughput por endpoint se muestra en req/min. 4. Los dashboards pueden filtrar por `tenant_id`, `service_name`, `method`, `status_code`. 5. Los histograms permiten calcular percentiles en Grafana con `histogram_quantile`. 6. Las métricas están disponibles en `/metrics` para scraping Prometheus. 7. Se pueden configurar alertas cuando la latencia p99 supera un umbral por endpoint. 8. El overhead del middleware de instrumentación es < 1ms. ---

## Endpoints
- `GET /metrics` — Métricas Prometheus (incluye todas las métricas de aplicación) - `GET /api/v1/observability/metrics/application` — API REST para métricas - Query params: `service_name`, `endpoint`, `from`, `to`, `percentile` (p50/p95/p99) - `GET /api/v1/observability/metrics/application/export` — Exportar a CSV/JSON - `GET /api/v1/observability/metrics/application/top-slow` — Top 10 endpoints más lentos ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Para evitar alta cardinalidad, el label `path` debe ser la plantilla de ruta (sin IDs). Se normaliza el path en el middleware. - La métrica `service_http_requests_in_flight` es útil para detectar饱和ación del servicio. - Se recomienda usar `histogram` en vez de `summary` para latency porque permite agregar percentiles post-scraping. - Para servicios con múltiples instancias, Prometheus agrega automáticamente las métricas. - Se deben exponer métricas de errores (`status_code 5xx`) separately para facilitar alertas de error rate.
