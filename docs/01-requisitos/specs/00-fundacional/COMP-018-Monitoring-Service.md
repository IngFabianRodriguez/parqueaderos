# COMP-018 — Monitoring Service

## Metadata

- **Nombre**: monitoring-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8018
- **DB**: PostgreSQL (schema `monitoring`)
- **Cache**: Redis
- **Servicios afectados**: Todos los microservicios
- **Componentes relacionados**: API Gateway, todos los servicios internos, observability-stack

---

## Objetivo

Centralizar la observabilidad del sistema: health checks, métricas, alertas, logs, tracing distribuido, y dashboards. Provee una vista unificada del estado de salud de todos los servicios, permite configurar alertas y thresholds, y mantiene ventanas de silencio para mantenimiento planificado.

---

## Tecnología

- **Runtime**: Go 1.21 (mejor rendimiento para collection intensivo)
- **DB**: PostgreSQL 15 (alertas, configuraciones, historial)
- **Cache**: Redis (estados de salud, caching de métricas)
- **Message Broker**: Kafka (eventos de métricas, alertas)
- **Protocolos**: Prometheus (scraping), OpenTelemetry (traces), Loki (logs)
- **Dashboards**: Integración con Grafana
- **Alerting**: AlertManager + PagerDuty/Slack integration
- **API**: REST + gRPC (interno)

---

## Modelo de Datos

### Tabla: service_health

```sql
id                  UUID PK
service_name        VARCHAR(100) NOT NULL UNIQUE
service_type        VARCHAR(50)  -- api, worker, background, external

version             VARCHAR(20)
environment         VARCHAR(20)  -- production, staging, dev

status              VARCHAR(20) DEFAULT 'unknown'  -- up, degraded, down, unknown
latency_ms          INTEGER

db_status            VARCHAR(20)
redis_status         VARCHAR(20)
kafka_status         VARCHAR(20)
external_dependencies JSONB DEFAULT '{}'

last_check_at       TIMESTAMPTZ DEFAULT NOW()
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: alert_rules

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

nombre              VARCHAR(255) NOT NULL
descripcion         TEXT

severidad           VARCHAR(10) NOT NULL  -- critical, warning, info
servicio            VARCHAR(100)  -- null = todos
metrica             VARCHAR(100) NOT NULL  -- ej: http_request_duration_seconds
condicion           VARCHAR(50) NOT NULL  -- >, <, ==, >=, <=
valor_threshold     DECIMAL(14,4) NOT NULL

ventana_segundos    INTEGER DEFAULT 300  -- ventana de evaluación
severidad_minima    VARCHAR(10) DEFAULT 'warning'  -- mínima para alertar

cooldown_segundos   INTEGER DEFAULT 300  -- tiempo antes de re-alertar

activo              BOOLEAN DEFAULT true

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: alerts

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

rule_id             UUID FK → alert_rules (nullable)
service_name        VARCHAR(100) NOT NULL

tipo                VARCHAR(50) NOT NULL  -- SERVICE_DOWN, HIGH_LATENCY, HIGH_ERROR_RATE, etc
severidad           VARCHAR(10) NOT NULL
mensaje             TEXT NOT NULL

valor_actual        DECIMAL(14,4)
threshold           DECIMAL(14,4)

estado              VARCHAR(20) DEFAULT 'firing'  -- firing, acknowledged, resolved
silenced            BOOLEAN DEFAULT false
silence_window_id   UUID FK → maintenance_windows (nullable)

notificado_a        JSONB DEFAULT '[]'  -- canales notificados

resolved_at         TIMESTAMPTZ (nullable)
resolved_by         UUID FK → usuarios (nullable)

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: maintenance_windows

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

nombre              VARCHAR(255) NOT NULL
razon               TEXT

start_time          TIMESTAMPTZ NOT NULL
end_time            TIMESTAMPTZ NOT NULL

servicios_afectados VARCHAR(255)[] DEFAULT '["all"]'
metricas_afectadas  VARCHAR(255)[]  -- null = todas
severidades_afectadas VARCHAR(10)[] DEFAULT '["critical", "warning", "info"]'

notify_on_end       BOOLEAN DEFAULT true

estado              VARCHAR(20) DEFAULT 'scheduled'  -- scheduled, active, completed, cancelled

creado_por          UUID FK → usuarios
ticket_id           VARCHAR(100)  -- ticket externo (Jira, etc)

created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: notification_channels

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

nombre              VARCHAR(100) NOT NULL
tipo                VARCHAR(30) NOT NULL  -- email, slack, pagerduty, webhook

configuracion       JSONB NOT NULL  -- email: addresses[], slack: webhook_url, pagerduty: integration_key

activo              BOOLEAN DEFAULT true

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: alert_notifications

```sql
id                  UUID PK
alert_id            UUID FK → alerts NOT NULL
channel_id          UUID FK → notification_channels NOT NULL

estado_envio        VARCHAR(20) DEFAULT 'pending'  -- pending, sent, failed
error_mensaje       TEXT

sent_at             TIMESTAMPTZ (nullable)
created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: metric_samples

```sql
id                  BIGSERIAL PK
tenant_id           UUID FK → tenants NOT NULL
service_name        VARCHAR(100) NOT NULL

metrica             VARCHAR(100) NOT NULL
valor               DECIMAL(14,4) NOT NULL
labels              JSONB DEFAULT '{}'

recorded_at         TIMESTAMPTZ NOT NULL
created_at          TIMESTAMPTZ DEFAULT NOW()

PARTITION BY RANGE (recorded_at)
```

### Tabla: incident_escalations

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL

alert_id            UUID FK → alerts NOT NULL

nivel               INTEGER DEFAULT 1  -- 1, 2, 3
estado              VARCHAR(20) DEFAULT 'pending'  -- pending, notified, escalated

usuario_id          UUID FK → usuarios (nullable)
canal               VARCHAR(30) NOT NULL

notificado_at       TIMESTAMPTZ (nullable)
confirmado_at       TIMESTAMPTZ (nullable)
escalated_at        TIMESTAMPTZ (nullable)

created_at          TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints REST

### Health

```
GET    /api/v1/health                             Health del servicio
GET    /api/v1/health/live                       Liveness probe
GET    /api/v1/health/ready                      Readiness probe

GET    /api/v1/health/services                   Estado de todos los servicios
GET    /api/v1/health/services/{service_name}     Health específico
```

### Alertas

```
GET    /api/v1/alerts                            Lista alertas (filtros: severidad, servicio, estado)
GET    /api/v1/alerts/{alert_id}                 Detalle alerta
PATCH  /api/v1/alerts/{alert_id}/acknowledge    Confirmar alerta
PATCH  /api/v1/alerts/{alert_id}/resolve        Resolver alerta
POST   /api/v1/alerts/{alert_id}/silence         Silenciar alerta
```

### Reglas

```
GET    /api/v1/alerts/rules                      Lista reglas
POST   /api/v1/alerts/rules                      Crear regla
GET    /api/v1/alerts/rules/{rule_id}            Detalle regla
PUT    /api/v1/alerts/rules/{rule_id}            Actualizar regla
DELETE /api/v1/alerts/rules/{rule_id}            Eliminar regla
POST   /api/v1/alerts/rules/{rule_id}/test       Probar regla
```

### Maintenance Windows

```
GET    /api/v1/maintenance-windows               Lista ventanas
POST   /api/v1/maintenance-windows               Crear ventana
GET    /api/v1/maintenance-windows/{id}           Detalle ventana
PUT    /api/v1/maintenance-windows/{id}          Editar ventana
DELETE /api/v1/maintenance-windows/{id}          Cancelar ventana
PATCH  /api/v1/maintenance-windows/{id}/extend   Extender ventana activa
GET    /api/v1/maintenance-windows/{id}/silenced-alerts  Alertas silenciadas
GET    /api/v1/maintenance-windows/history        Historial de ventanas
```

### Canales de Notificación

```
GET    /api/v1/notification-channels             Lista canales
POST   /api/v1/notification-channels             Crear canal
GET    /api/v1/notification-channels/{id}         Detalle canal
PUT    /api/v1/notification-channels/{id}        Actualizar canal
DELETE /api/v1/notification-channels/{id}        Eliminar canal
POST   /api/v1/notification-channels/{id}/test    Probar canal
```

### Métricas

```
GET    /api/v1/metrics/services                  Métricas por servicio
GET    /api/v1/metrics/services/{service_name}    Métricas específicas
GET    /api/v1/metrics/query?metric=X&from=Y&to=Z  Query metrics raw
```

### Dashboards

```
GET    /api/v1/dashboards/overview                Dashboard overview
GET    /api/v1/dashboards/services                Dashboard services
GET    /api/v1/dashboards/alerts                   Dashboard alertas
```

---

## Endpoints gRPC (interno)

```protobuf
service MonitoringService {
  rpc GetServiceHealth(GetServiceHealthRequest) returns (ServiceHealth);
  rpc ListAlerts(ListAlertsRequest) returns (AlertList);
  rpc GetAlertMetrics(GetAlertMetricsRequest) returns (AlertMetrics);
  rpc IsSilenced(SilencedCheckRequest) returns (SilencedResponse);
}
```

---

## OpenTelemetry Integration

### Traces

- Todos los servicios deben enviar traces a OpenTelemetry Collector (puerto 4317)
- El monitoring-service consume traces desde Tempo
- Trace ID propagado en headers `traceparent`, `tracestate`

### Métricas (Prometheus)

```
# Métricas de negocio
parkcore_transacciones_total{sede_id, tipo}
parkcore_ingresos_mensuales{tenant_id, sede_id}
parkcore_espacios_ocupados{sede_id, zona_id}
parkcore_tasa_ocupacion{sede_id}
parkcore_tickets_soporte_total{sede_id, estado}

# Métricas técnicas
http_requests_total{service, method, status}
http_request_duration_seconds{service, quantile}
db_query_duration_seconds{service}
redis_operations_total{operation}
kafka_messages_produced_total{topic}

# Métricas de salud
service_up{service}
circuit_breaker_state{service}
rate_limit_hits_total{service}
```

---

## Alertamiento

### Reglas por Default

| Alerta | Condición | Severidad | Canal |
|--------|-----------|-----------|-------|
| ServiceDown | service_up == 0 por 2min | critical | PagerDuty + Slack |
| HighErrorRate | error_rate > 5% por 5min | warning | Slack |
| HighLatency | P99 > 1s por 10min | warning | Slack |
| DiskSpaceLow | disk > 85% | warning | Slack |
| DatabaseSlow | db_p99 > 2s por 5min | warning | Slack |

### Workflow de Alerta

```
1. Rule triggered → Alert created (estado=firing)
2. Alert evaluated against maintenance windows
3. If silenced: alert.silenced=true, no notification
4. If not silenced: route to notification channels
5. User acknowledges → estado=acknowledged
6. Condition clears → estado=resolved
```

---

## Eventos Kafka

### Topic: `parkcore.monitoring`

```json
{
  "event_type": "alert.firing",
  "alert_id": "uuid",
  "service_name": "billing-service",
  "severity": "critical",
  "timestamp": "2026-05-08T10:00:00Z",
  "data": { "message": "Service is down", "value": 0, "threshold": 1 }
}
```

Eventos:
- `service.health_changed`
- `alert.firing`, `alert.acknowledged`, `alert.resolved`, `alert.silenced`
- `maintenance_window.started`, `maintenance_window.ended`
- `notification.sent`, `notification.failed`
- `escalation.triggered`

---

## Rate Limiting

- Health checks: sin límite (para probes de K8s)
- Consulta de métricas: 60 rpm por cliente
- Configuración de reglas: 20 rpm
- Crear maintenance windows: 10 rpm

---

## Dependencias

- **DB**: PostgreSQL `monitoring` schema
- **Redis**: Cache de health checks, estados de alertas
- **Kafka**: Eventos de monitoreo y alertas
- **Prometheus**: Collection de métricas
- **Loki**: Logs estructurados (JSON)
- **Tempo**: Distributed tracing
- **Grafana**: Dashboards (acceso externo)
- **AlertManager**: Routing de alertas
- **Todos los servicios**: Emisión de health y métricas

---

## Métricas

- `monitoring_health_checks_total{service, status}`
- `monitoring_alerts_firing_total{severity, service}`
- `monitoring_alerts_resolved_total{time_to_resolve_minutes}`
- `monitoring_maintenance_windows_active`
- `monitoring_notifications_sent_total{channel_type}`
- `monitoring_sla_compliance_rate`
- `monitoring_mttr_minutes` (Mean Time To Recovery)

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "kafka": "connected" }
GET /health/ready → verifica DB, Redis, Kafka, Prometheus endpoint
GET /health/live → solo proceso activo
```

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|-----------------|
| Prometheus down | Métricas se pierden, alerts basadas en último valor known |
| Loki down | Logs se bufferizan en memoria (max 100MB), luego se dropean |
| Maintenance window se cruza con otra | Error 409, no permitir crear |
| Service health no reportado > 5min | Marcar como unknown, alertar |
| Alert re-dispara durante cooldown | No enviar notificación, registrar en log |
| Más de 100 alertas firing | Rate limit a nuevas alertas, marcar como 'queued' |

---

## Notas

- Go usado por rendimiento en collection de métricas intensivo
- Particionamiento de `metric_samples` por tiempo para optimizar queries históricos
- Sampling de traces: 10% en producción, 100% en errores
- Logs siempre JSON estructurado, nivel configurable (INFO/WARN/ERROR/DEBUG)
- Dashboard Grafana integra Loki, Prometheus, Tempo en una sola interfaz
- Maintenance windows silencian alertas pero las guardan para reporte post-mantenimiento
- Alertas silenciadas se marcan con `silenced: true` y `silence_window_id`
- Se implementa buffer local para métricas si Kafka está temporalmente no disponible