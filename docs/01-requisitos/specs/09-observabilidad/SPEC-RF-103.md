# SPEC-09-observabilidad-103 — El sistema debe trackear el uso de recursos de infraestructura (CPU, memoria ...

## Metadata
- **RF origen**: RF-103
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador del sistema **quiero** ver las métricas de uso de CPU, RAM, disco y red de cada microservicio **para** identificar cuellos de botella, planificar capacidad y recibir alertas cuando un recurso esté siendo sobreexplotado. ---

## Objetivo
El sistema debe trackear el uso de recursos de infraestructura (CPU, memoria RAM, uso de disco, tráfico de red) de cada microservicio. Estos datos se almacenan con retención de 30 días y se exponen como métricas en formato Prometheus (`/metrics`) para visualización en Grafana. Los datos permiten crear dashboards de uso de recursos y configurar alertas de capacidad. ---

## Comportamiento Específico

### Happy Path
1. El agente de métricas (o el SDK del servicio) recolecta: - **CPU**: `cpu_percent` (por proceso y total), `cpu_cores_available`. - **RAM**: `memory_rss_mb`, `memory_heap_mb`, `memory_available_mb`. - **Disco**: `disk_used_gb`, `disk_free_gb`, `disk_inodes_used`. - **Red**: `network_bytes_in`, `network_bytes_out`, `network_connections_active`. 2. Los datos se envían al servidor de métricas (Prometheus/InfluxDB) con labels: `tenant_id`, `service_name`, `host`, `region`. 3. Se calculan agregados: `rate(cpu_percent[5m])` para uso promedio. 4. Se generan métricas exportables en `/metrics`. ---

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
1. Las métricas se recolectan cada 15 segundos sin impacto medible en el servicio (< 1ms overhead). 2. Las métricas están disponibles en formato Prometheus en `/metrics` de cada servicio. 3. Los labels `service_name` y `tenant_id` están presentes en todas las métricas. 4. Los datos de hasta 30 días están disponibles para consulta. 5. Los dashboards en Grafana pueden filtrar por `service_name`, `tenant_id`, `host`, `region`. 6. Las alertas thresholds son configurables por el `tenant_admin` (RF-106). 7. Se puede exportar el histórico de métricas a CSV/JSON. 8. La caída del agente de métricas no afecta la operación del servicio. ---

## Endpoints
- `GET /metrics` — Métricas Prometheus del servicio - `GET /api/v1/observability/metrics/infrastructure` — API para consultar métricas - Query params: `service_name`, `tenant_id`, `from`, `to`, `resolution` - `GET /api/v1/observability/metrics/infrastructure/export` — Exportar a CSV/JSON ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- En contenedores Kubernetes, las métricas de `node_*` se recolectan a nivel del nodo, no del container. - Se recomienda usar `process_cpu_seconds_total` (métrica estándar de Prometheus) como base para计算的 CPU. - Para evitar overload de métricas, se excluyen métricas de red por dirección IP individual (solo totales por interfaz). - El campo `gc_count` (contador de garbage collections) es útil para detectar memory pressure en aplicaciones gestionadas (JVM, Go). - Se debe garantizar que las métricas no contengan información sensible (IPs de usuarios, datos personales).
