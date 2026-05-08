# Arquitectura de Microservicios — ParkCore

## Contexto y Objetivos

Este documento define la arquitectura de microservicios de ParkCore con enfoque en **mantenibilidad operacional**: cada servicio debe poder desplegarse, monitorearse, truncarse y recuperarse de forma independiente, sin afectar la operación de los demás. La arquitectura busca que cualquier ingeniero nuevo pueda entender el sistema en semanas, no meses.

> **Supuestos fundamentales**: Colombia, monetización SaaS, ANPR como diferenciador, 1–50+ sedes, equipo reducido de ingeniería.

---

## 1. Descomposición en Servicios

### 1.1 Mapa de Servicios

```
┌─────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                             │
│                   (Kong / NGINX + Lua)                          │
└──────────┬──────────┬──────────┬──────────┬──────────┬──────────┘
           │          │          │          │          │
     ┌─────┴──┐  ┌───┴───┐  ┌───┴───┐  ┌───┴───┐  ┌───┴───┐
     │  Auth  │  │Sedes  │  │ IoT   │  │Pagos  │  │Notif  │
     │Service │  │Service│  │Service│  │Service│  │Service│
     └────┬───┘  └───┬───┘  └───┬───┘  └───┬───┘  └───┬───┘
          │          │          │          │          │
     ┌────┴──────────┴──────────┴──────────┴──────────┴────┐
     │              Kafka (Event Bus)                       │
     │  topics: vehicle.entered | vehicle.exited | payment.confirmed │
     │          talanquera.commanded | notification.requested       │
     └─────────────────────────────────────────────────────────────┘
```

### 1.2 Servicios y Responsabilidad Única

| Servicio | Responsabilidad | DB propia | Puerto | SLO objetivo |
|----------|-----------------|-----------|--------|--------------|
| **auth-service** | JWT issuance, refresh rotation, RBAC enforcement, user sessions | PostgreSQL (auth schema) | 8001 | 99.9% |
| **sedes-service** | CRUD de sedes, zonas, espacios; disponibilidad en tiempo real | PostgreSQL (sedes schema) | 8002 | 99.5% |
| **iot-service** | ingestion de eventos MQTT, correlación con espacios, comando a talanqueras | PostgreSQL + TimescaleDB | 8003 | 99.5% |
| **pagos-service** | lifecycle de transacciones, integración con pasarelas (Wompi/ePayco), reembolsos | PostgreSQL (pagos schema) | 8004 | 99.9% |
| **notif-service** | push/SMS/email/wpp, plantillas, cola de envío con retry | PostgreSQL (notif schema) + Redis queue | 8005 | 99.0% |
| **anpr-service** | OCR de placas, correlación con registros, fallback manual | PostgreSQL (anpr schema) + S3 (imágenes) | 8006 | 99.5% |
| **api-gateway** | auth validation, rate limiting, routing, protocol translation | Ninguna | 8000 | 99.95% |

### 1.3 Reglas de Propiedad de Datos (Database per Service)

> **Regla dorada**: Cada servicio tiene su propia base de datos. Ningún servicio consulta directamente tablas de otro servicio.

Para obtener datos de otro servicio se usa:
- **API REST síncrona** para queries que requieren respuesta inmediata (ej: "¿este vehículo tiene pago confirmado?")
- **Events Kafka** para reaccionar a cambios de estado (ej: "cuando pago se confirme, notificar a iot-service para abrir talanquera")

**Ejemplo de comunicación entre servicios:**

```
Caso: Vehículo ABC-123 quiere salir

1. anpr-service detecta placa → publica event "vehicle.exited"
2. iot-service consume event → busca registro entrada activo
3. pagos-service consume event → verifica si hay pago confirmado
4. pagos-service responde por API REST a iot-service → "pago_confirmado: true"
5. pagos-service publica event "payment.validated"
6. iot-service consume event → envía comando MQTT a talanquera de salida
```

### 1.4 Contratos entre Servicios (API Contracts)

Cada servicio expone su API en `/docs/openapi.json` (OpenAPI 3.0). Los contratos se versionan con prefijos de URL: `/api/v1/`, `/api/v2/`. Cambios backward-incompatibles crean nueva versión.

**Contratos definidos:**

| Servicio | Contrato | Formato |
|----------|----------|---------|
| auth-service | `GET /api/v1/auth/me` | Devuelve usuario + roles del token |
| auth-service | `POST /api/v1/auth/validate` | Valida JWT y retorna claims |
| sedes-service | `GET /api/v1/sedes/{id}/disponibilidad` | Espacios disponibles |
| pagos-service | `POST /api/v1/pagos/validar` | Body: `{placa, sede_id}` → `{valido, monto}` |
| pagos-service | `GET /api/v1/pagos/estado/{id}` | Estado transacción |
| iot-service | `POST /api/v1/iot/comando/talanquera` | Body: `{sede_id, talanquera_id, accion}` |
| anpr-service | `POST /api/v1/anpr/registrar` | Body: `{placa, sede_id, talanquera_id, tipo}` |

---

## 2. Comunicación Inter-Servicios

### 2.1 Patrones de Comunicación

| Patrón | Cuándo usar | Implementación |
|--------|-------------|----------------|
| **Request/Response síncrono** | Queries que requieren respuesta inmediata (< 200ms) | REST (FastAPI interno), gRPC para alta frecuencia |
| **Publicar/Consumir eventos** | Acciones que no requieren respuesta inmediata, múltiples suscriptores | Kafka topics |
| **Saga / Orquestación** | Transacciones distribuidas que abarcan múltiples servicios | Orchestrator en pagos-service |

### 2.2 Kafka Topics (Event-Driven)

```
vehicle.entered        — publicado por anpr-service cuando placa ingresa
vehicle.exited         — publicado por anpr-service cuando placa sale
payment.confirmed      — publicado por pagos-service cuando pago aprobado
payment.failed         — publicado por pagos-service cuando pago rechazado
payment.validated      — publicado por pagos-service para consulta de validación
talanquera.commanded   — publicado por iot-service cuando envía orden a hardware
notification.requested — publicado por cualquier servicio que necesita notificar
session.created        — publicado por auth-service cuando usuario inicia sesión
```

**Consumer groups por servicio:**

```
anpr-service:          [vehicle.entered, vehicle.exited]
iot-service:           [vehicle.entered, vehicle.exited, payment.validated, talanquera.commanded]
pagos-service:         [vehicle.entered, vehicle.exited, notification.requested]
notif-service:         [notification.requested]
sedes-service:         [] (solo consume vía REST, no suscribe events)
auth-service:          [session.created]
```

### 2.3 gRPC para Alta Frecuencia

Para la comunicación de menor latency entre `iot-service` y el edge gateway (MQTT bridge local), se usa **gRPC con Protobuf** en lugar de HTTP/JSON. Esto aplica únicamente para el flujo crítico de apertura de talanquera donde cada milisegundo cuenta.

```
EdgeGateway (MQTT bridge) ←→ iot-service (gRPC)
```

---

## 3. API Gateway

### 3.1 Responsabilidades

El API Gateway (Kong + Lua custom) centraliza:
- **Autenticación**: Valida JWT en cada request, extrae claims, inyecta headers `X-User-Id`, `X-Rol`, `X-Sede-Id`
- **Rate limiting**: Sliding window por token/IP/endpoint (Redis backend)
- **Routing**: direciona a microservicio según path
- **SSL termination**: TLS 1.3, certificados Let's Encrypt con auto-renew
- **Circuit breaker**: Kong plugin `circuit-breaker` con umbrales configurables

### 3.2 Configuración de Rutas

```yaml
# Kong declarative config (deck)
routes:
  - name: auth
    paths: [/api/v1/auth]
    service: auth-service:8001
    plugins: [jwt-auth, rate-limit-50]

  - name: sedes
    paths: [/api/v1/sedes]
    service: sedes-service:8002
    plugins: [jwt-auth, rate-limit-100]

  - name: pagos
    paths: [/api/v1/pagos]
    service: pagos-service:8004
    plugins: [jwt-auth, rate-limit-30]

  - name: iot
    paths: [/api/v1/iot]
    service: iot-service:8003
    plugins: [jwt-auth, rate-limit-200]

  - name: anpr
    paths: [/api/v1/anpr]
    service: anpr-service:8006
    plugins: [jwt-auth, rate-limit-100]
```

---

## 4. Patrón Saga para Transacciones Distribuidas

### 4.1 Flujo de Pago (Saga)

```
Cliente paga → pagos-service crea transacción (estado: PENDIENTE)
           → pagos-service llama pasarela (Wompi/ePayco)
           → si OK → publica "payment.confirmed" (estado: CONFIRMADO)
           → si FALLA → publica "payment.failed" (estado: FALLIDO)
           → notif-service consume y envía notificación al cliente
           → iot-service consume y actualiza disponibilidad
```

### 4.2 Compensaciones (Rollback)

| Step | Acción | Compensación |
|------|--------|--------------|
| Crear transacción PENDIENTE | Guardar en BD pagos | Eliminar registro |
| Reservar espacio (iot-service) | Actualizar espacio a OCUPADO | Liberar espacio |
| Confirmar pago externamente | Registrar en BD pagos | Revertir en pasarela (si soporta) |
| Enviar notificación | push/SMS enviado | N/A (idempotente) |

---

## 5. Observabilidad Distribuida

### 5.1 Las Tres Pilares

**Logs**: Formato JSON estructurado con `trace_id` injectado por API Gateway. Agregación en Loki. Búsqueda por trace_id, user_id, sede_id.

**Métricas**: Prometheus exporta metrics de cada servicio. Dashboards en Grafana por servicio:

```
parkcore-auth:    tokens_issued_total, token_validation_duration_ms, auth_errors
parkcore-sedes:  disponibilidad_requests, espacios_consultados, cache_hit_rate
parkcore-iot:     eventos_recibidos, comandos_talanquera, latencia_mqtt_ms
parkcore-pagos:   transacciones_pendientes, transacciones_confirmadas, monto_total
parkcore-anpr:    placas_leidas, confianza_promedio, fallback_manual_count
```

**Traces**: Jaeger con instrumentación automática (OpenTelemetry SDK). Cada request recibe `trace_id` único propagado en headers entre servicios.

### 5.2 Dashboard por Servicio (Grafana)

Para cada servicio existe un dashboard estándar con:

- **Rendimiento**: Latencia p50, p95, p99 por endpoint
- **Throughput**: Requests/segundo, errores/segundo
- **Salud**: Uptime últimas 24h, MTTR, MTBF
- **Recursos**: CPU%, RAM%, conexiones DB, conexiones Redis

### 5.3 Alertas Operacionales

| Alerta | Condición | Acción |
|--------|-----------|--------|
| Auth service down | `up{job="auth-service"} == 0` | PagerDuty P1 |
| Latencia auth > 500ms | `histogram_quantile(0.95, rate(auth_latency_ms[5m])) > 500` | PagerDuty P2 |
| Pagos con errores > 5% | `rate(pago_errors_total[5m]) / rate(pago_requests_total[5m]) > 0.05` | PagerDuty P2 |
| IoT sin eventos > 5min | `rate(iot_events_total[5m]) == 0` | Slack + Opsgenie |
| Kafka consumer lag > 1000 | `consumer_lag > 1000` | Slack |

---

## 6. Despliegue Independendiente por Servicio

### 6.1 Docker Compose por Servicio

Cada servicio tiene su propio `docker-compose.yml` mínimo:

```yaml
# pagos-service/docker-compose.yml
services:
  pagos-service:
    build: ./pagos-service
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql://${PG_USER}:${PG_PASS}@pg-primary:5432/pagos
      - REDIS_URL=redis://:${REDIS_PASS}@redis:6379/1
      - KAFKA_BROKERS=kafka:9092
      - JWT_PUBLIC_KEY=${JWT_PUBLIC_KEY}
    depends_on:
      - pg-primary
      - redis
      - kafka
    healthcheck:
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
      command: curl -f http://localhost:8004/health || exit 1
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 128M

  pagos-worker:
    build: ./pagos-worker
    environment:
      - KAFKA_BROKERS=kafka:9092
    depends_on:
      - kafka
    restart: unless-stopped
```

### 6.2 Estrategias de Despliegue

**Rolling update** (default): Kong balancea gradualmente al nuevo pod mientras el antiguo sigue sirviendo requests. Zero downtime.

**Blue-Green** (para pagos-service): Despliega nueva versión en paralelo, switch de tráfico una vez validado, rollback instantáneo.

**Canary** (para auth-service): 5% del tráfico a nueva versión por 10 min, monitoreo de errores, si OK → rollout completo.

### 6.3 Helm Charts

Cada servicio tiene su chart en `/infra/helm/<servicio>/`:

```
infra/helm/
├── auth-service/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── ingress.yaml
│       ├── hpa.yaml
│       └── configmap.yaml
├── pagos-service/
├── iot-service/
└── ... (uno por servicio)
```

**values.yaml por ambiente:**

```yaml
# values-staging.yaml
replicaCount: 2
image:
  repository: parkcore/pagos-service
  tag: "1.2.3"
env:
  DATABASE_URL: postgresql://...@pg-staging:5432/pagos
  LOG_LEVEL: DEBUG
  KAFKA_BROKERS: kafka-staging:9092
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
  targetCPUUtilizationPercentage: 70
```

---

## 7. Contratos de Servicio y Contract Testing

### 7.1 Contract Testing con Pacts

Cada consumer define los contratos que espera del producer. Los contratos se verifican automáticamente en CI.

```
pagos-service (consumer) ←→ sedes-service (producer)
pagos-service (consumer) ←→ auth-service (producer)
iot-service (consumer) ←→ pagos-service (producer)
```

**Ejemplo de pacto (pagos-service → auth-service):**

```json
{
  "consumer": "pagos-service",
  "provider": "auth-service",
  "interactions": [
    {
      "description": "GET /api/v1/auth/validate with valid JWT",
      "request": {
        "method": "GET",
        "path": "/api/v1/auth/validate",
        "headers": { "Authorization": "Bearer <token>" }
      },
      "response": {
        "status": 200,
        "body": {
          "user_id": "string (UUID)",
          "rol": "string",
          "exp": "number (unix timestamp)"
        }
      }
    }
  ]
}
```

### 7.2 Consumer-Driven Contracts en CI

```yaml
# .github/workflows/contracts.yml
- name: Run contract tests
  run: |
    # Verify consumer contracts against providers
    ./pact/bin/pact-verifier \
      --provider-base-url=http://auth-service-staging:8001 \
      --pact-dir=./pacts
```

---

## 8. Resiliencia y Manejo de Fallos

### 8.1 Circuit Breaker (Kong + Python)

```python
# iot-service/resilience.py
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=30)
def validar_pago_con_pagos_service(placa: str, sede_id: str) -> bool:
    """Si pagos-service falla 5 veces, el circuit abre 30s."""
    response = httpx.get(
        f"http://pagos-service:8004/api/v1/pagos/validar",
        params={"placa": placa, "sede_id": sede_id},
        timeout=2.0
    )
    return response.json()["valido"]
```

### 8.2 Retry con Exponential Backoff

```python
# Todos los clientes HTTP usan retry configurado
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
def llamar_servicio_externo(url: str):
    ...
```

### 8.3 Fallback en Cascada

| Servicio caído | Fallback | Impacto |
|----------------|----------|---------|
| pagos-service | `iot-service` permite salida si pago pendiente < 15 min (offline queue) | Manual, no automático |
| auth-service | API Gateway cachea JWT validation por 5 min (Redis) | Lectura de dashboards solo |
| iot-service | Edge gateway opera en modo offline con última config | Operación local completa |
| sedes-service | `nginx` retorna последний known availability desde cache | Disponibilidad eventualmente stale |

---

## 9. Seguridad por Servicio

### 9.1 mTLS entre Servicios

Todos los servicios en producción usan **mTLS** con certificados emitidos por Vault PKI:

```
auth-service ←→ pagos-service: mTLS (CN=pagos-service, CA=parkcore-internal)
auth-service ←→ iot-service: mTLS (CN=iot-service, CA=parkcore-internal)
pagos-service ←→ anpr-service: mTLS
```

### 9.2 Network Policies (Kubernetes)

```yaml
# iot-service/network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: iot-service-policy
spec:
  podSelector:
    matchLabels:
      app: iot-service
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: api-gateway
      ports:
        - protocol: TCP
          port: 8003
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: kafka
      ports:
        - protocol: TCP
          port: 9092
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - protocol: TCP
          port: 5432
```

---

## 10. Catálogo de Eventos (Event Schema Registry)

Todos los eventos en Kafka tienen schema versionado en JSON Schema (guardado en `/schemas/` del repo):

```json
// schemas/vehicle.entered/v1.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VehicleEntered",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "placa", "sede_id", "timestamp", "source"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "placa": { "type": "string", "pattern": "^[A-Z]{3}[0-9]{3}$" },
    "sede_id": { "type": "string", "format": "uuid" },
    "talanquera_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "confianza_anpr": { "type": "number", "minimum": 0, "maximum": 100 },
    "source": { "type": "string", "enum": ["anpr", "manual", "emergency"] }
  }
}
```

---

## 11. Checklist de Mantenibilidad

Antes de desplegar cualquier nuevo servicio, verificar:

- [ ] Servicio tiene su propia DB (no share tables)
- [ ] Health endpoint `/health` y `/health/ready` implementados
- [ ] Métricas Prometheus exportadas en `/metrics`
- [ ] Trace ID propagado en todos los logs
- [ ] OpenAPI spec en `/docs/openapi.json`
- [ ] Contract tests con consumer-driven contracts
- [ ] Docker image < 200MB (distroless base)
- [ ] HPA configurada con mínimo 2 réplicas
- [ ] Network policy K8s definida
- [ ] Runbook de incidentes documentado
- [ ] Dashboards Grafana creados (rendimiento, salud, errores)
- [ ] Alerts configuradas en PagerDuty
- [ ] Rollback procedure documentada
- [ ] Secrets en Vault (no hardcoded)
- [ ] CI/CD pipeline pasando (test → build → deploy staging → smoke test → deploy prod)