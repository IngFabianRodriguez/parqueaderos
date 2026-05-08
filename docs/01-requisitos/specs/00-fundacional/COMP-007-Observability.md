# COMP-007 — Observability Stack

## Metadata

- **Nombre**: observability-stack
- **Tipo**: Infraestructura (Observabilidad)
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los microservicios
- **Componentes relacionados**: API Gateway, todos los servicios internos

---

## Objetivo

Centralizar la observabilidad del sistema (logs, metrics, traces) para lograr debugging rápido, monitoreo de salud y alertas proactivas. Todo debe fluir hacia un sistema unificado accesible por el equipo de operaciones.

---

## Arquitectura

```
[Todos los servicios]
        │
        ├── Logs (structured JSON) ──→ Loki ──→ Grafana
        ├── Metrics (Prometheus) ──────────→ Prometheus ──→ Grafana
        └── Traces (OpenTelemetry) ──→ Tempo ──→ Grafana

[Grafana]
  └── Dashboards: Overview, Servicios, Infraestructura, Alertas
```

### Componentes

| Componente | Tecnología | Puerto | Función |
|------------|------------|--------|---------|
| Metrics | Prometheus | 9090 | Recolectar y almacenar métricas |
| Logs | Loki | 3100 | Agregación de logs estructurados |
| Traces | Tempo | 3200 | Distributed tracing storage |
| Visualización | Grafana | 3000 | Dashboards unificados |
| Alerting | AlertManager | 9093 | Routing de alertas |
| Collection | OpenTelemetry Collector | 4317/4318 | Recibe OTLP, exporta a backends |
| Service Graph | - | - | Genera service graph desde traces |

---

## Logs Estructurados

### Formato JSON por defecto

```json
{
  "timestamp": "2026-01-15T10:30:00Z",
  "level": "INFO",
  "service": "tenant-service",
  "trace_id": "abc123-def456",
  "span_id": "span789",
  "message": "Tenant created successfully",
  "tenant_id": "uuid",
  "user_id": "uuid",
  "duration_ms": 45,
  "metadata": {}
}
```

### Niveles

- **ERROR**: Fallo en operación, requiere atención inmediata
- **WARN**: Degradación, comportamiento inesperado
- **INFO**: Eventos normales (startup, shutdown, configuración)
- **DEBUG**: Detalle de debugging (solo en entornos dev/staging)

### Logs de Auditoría

```json
{
  "timestamp": "...",
  "level": "INFO",
  "service": "audit-service",
  "event_type": "AUDIT",
  "action": "tenant.update_plan",
  "actor_id": "uuid",
  "actor_ip": "192.168.1.1",
  "resource_type": "tenant",
  "resource_id": "uuid",
  "changes": { "plan": ["starter", "professional"] },
  "trace_id": "..."
}
```

---

## Métricas (Prometheus)

### Métricas de Negocio

| Métrica | Tipo | Labels | Descripción |
|---------|------|--------|-------------|
| `parkcore_transacciones_total` | Counter | sede_id, tipo | Total transacciones |
| `parkcore_ingresos_mensuales` | Gauge | tenant_id, sede_id | Ingresos del mes actual |
| `parkcore_espacios_ocupados` | Gauge | sede_id, zona_id | Espacios ocupados ahora |
| `parkcore_tasa_ocupacion` | Gauge | sede_id | Porcentaje ocupación |
| `parkcore_tickets_soporte_total` | Counter | sede_id, estado | Tickets creados |

### Métricas Técnicas

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `http_requests_total` | Counter | Requests por servicio, método, status |
| `http_request_duration_seconds` | Histogram | Latencia P50/P90/P99 |
| `db_query_duration_seconds` | Histogram | Latencia de queries |
| `redis_operations_total` | Counter | Operaciones Redis |
| `kafka_messages_produced_total` | Counter | Mensajes producidos |
| `grpc_calls_total` | Counter | Llamadas gRPC |

### Métricas de Salud

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `service_up` | Gauge | 1=up, 0=down |
| `circuit_breaker_state` | Gauge | closed=0, open=1, half-open=2 |
| `rate_limit_hits_total` | Counter | Rate limit violations |

---

## OpenTelemetry - Distributed Tracing

### Context Propagation

Headers inyectados y propagados:
```
traceparent: 00-{trace-id}-{span-id}-{flags}
tracestate: tenant={tenant_id}
X-Trace-ID: {trace-id} (backup)
```

### Spans obligatorios

Cada operación debe crear spans para:
- HTTP handler (in/out)
- DB query
- External calls (Redis, Kafka, Vault)
- Business logic

### Sampling

- ** Producción**: 10% de traces, 100% de errores
- **Staging**: 50% de traces
- **Dev**: 100% de traces

---

## Dashboards (Grafana)

### Dashboard: Overview

- Consumo de recursos por servicio
- Errores en tiempo real
- Latencia P99 por servicio
- Disponibilidad (uptime)

### Dashboard: Negocio

- Transacciones por hora
- Ingresos del día/mes
- Ocupación por sede
- Tickets de soporte abiertos

### Dashboard: Infraestructura

- CPU/Memoria por pod
- Uso de disco
- Conexiones DB
- Network I/O

### Dashboard: Alertas

- Alertas activas
- Historial de alertas
- MTTR (Mean Time To Recovery)

---

## Alertamiento

### Reglas de Alertamiento

| Alerta | Condición | Severidad | Canal |
|--------|-----------|-----------|-------|
| `ServiceDown` | service_up == 0 por 2min | critical | PagerDuty + Slack |
| `HighErrorRate` | error_rate > 5% por 5min | warning | Slack |
| `HighLatency` | P99 > 1s por 10min | warning | Slack |
| `DiskSpaceLow` | disk > 85% | warning | Slack |
| `DiskSpaceCritical` | disk > 95% | critical | PagerDuty |
| `DatabaseSlow` | db_p99 > 2s por 5min | warning | Slack |
| `CircuitBreakerOpen` | cb_state == 1 por 1min | warning | Slack |

### Notification Routing

```yaml
critical:
  - pagerduty
  - slack_critical
warning:
  - slack_warning
info:
  - slack_info
```

---

## OpenTelemetry Collector Config

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
  memory_limiter:
    check_interval: 5s
    limit_mib: 512

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  loki:
    endpoint: http://loki:3100/loki/api/v1/push
  tempo:
    endpoint: http://tempo:3200

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [tempo]
    metrics:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]
```

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|---------------|-------------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | localhost:4317 | Endpoint OTLP |
| `OTEL_SERVICE_NAME` | auto | Nombre del servicio |
| `LOKI_URL` | http://loki:3100 | URL de Loki |
| `PROMETHEUS_URL` | http://prometheus:9090 | URL de Prometheus |
| `GRAFANA_URL` | http://grafana:3000 | URL de Grafana |
| `ALERTMANAGER_URL` | http://alertmanager:9093 | URL de AlertManager |
| `TRACE_SAMPLING_RATE` | 0.1 | 10% en producción |
| `LOG_LEVEL` | INFO | Nivel mínimo de log |

---

## Dependencias

- **Infraestructura**: Prometheus, Loki, Tempo, Grafana, AlertManager
- **Lenguajes**: OpenTelemetry SDK (Python, Go, Node.js)
- **Kubernetes**: Prometheus Operator, Loki Operator
- **Rendimiento**: 100GB/month logs, retention 30d

---

## Métricas de Éxito

- Cobertura de trazas: 95% de requests tienen trace
- Disponibilidad dashboards: 99.9%
- Latencia de logs: < 5s desde emisión a visible
- Alertamiento: 100% de errores críticos alertados en < 1min

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Loki no disponible | Logs se bufferizan en memoria (max 100MB), luego se dropean con warn |
| Prometheus down | Métricas se pierden, alerts basadas en últimos valores known |
| Sampling alto en prod | Si trace volume > 10MB/s, auto-reduce a 5% |
| Logs masivos | Rate limit a 10k logs/segundo por servicio |

---

## Notas

- Todos los logs deben ser JSON estructurado, nunca texto libre
- Los traces deben usar el header `traceparent` W3C estándar
- Los dashboards deben tener variables para filtrar por tenant/sede
- El retention de logs: 7 días hot, 30 días cold (S3/GCS)