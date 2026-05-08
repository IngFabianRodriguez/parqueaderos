# COMP-001 — API Gateway

## Metadata

- **Nombre**: API Gateway — ParkCore
- **Tipo**: Infraestructura (Middleware)
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los servicios internos
- **Componentes relacionados**: auth-service, todos los microservicios

---

## Objetivo

Centralizar el punto de entrada de toda petición externa al sistema. El API Gateway se encarga de autenticación JWT, rate limiting, routing a microservicios, SSL termination, circuit breaking y propagando headers de contexto (`X-User-Id`, `X-Rol`, `X-Tenant-Id`, `X-Trace-ID`) a los servicios internos.

---

## Arquitectura

```
[Cliente/App/Frontend]
        ↓ HTTPS (TLS 1.3)
[API Gateway — Kong + Lua]
        ├── Validar JWT
        ├── Extraer claims → inyectar headers
        ├── Rate limiting (Redis backend)
        ├── Routing por path → servicio:port
        ├── Circuit breaker
        └── TRACE injection
```

### Servicios internos (destinos):

| Servicio | Puerto | Path base |
|----------|--------|-----------|
| auth-service | 8001 | /api/v1/auth |
| tenant-service | 8002 | /api/v1/tenants |
| sedes-service | 8003 | /api/v1/sedes |
| iot-service | 8004 | /api/v1/iot |
| pagos-service | 8005 | /api/v1/pagos |
| anpr-service | 8006 | /api/v1/anpr |
| notif-service | 8007 | /api/v1/notif |
| reports-service | 8008 | /api/v1/reports |

### Headers inyectados por el Gateway:

```
X-User-Id: UUID del usuario autenticado
X-Rol: tenant_admin | sede_manager | operador | cliente
X-Tenant-Id: UUID del tenant
X-Sede-Id: UUID de la sede (si aplica)
X-Trace-ID: UUID v4 para trazabilidad distributed
X-Request-Timestamp: unix timestamp
```

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| JWT_PUBLIC_KEY | env var | RSA public key para validar RS256 |
| REDIS_URL | redis://redis:6379/0 | Backend rate limiting |
| KAFKA_BROKERS | kafka:9092 | Broker para eventos |
| LOG_LEVEL | INFO | Nivel de logs |
| CIRCUIT_BREAKER_THRESHOLD | 5 | Errores consecutivos para abrir |
| CIRCUIT_BREAKER_TIMEOUT | 30 | Segundos antes de intentar de nuevo |
| RATE_LIMIT_DEFAULT | 100 rpm | Límite por defecto |

---

## Rate Limiting por Plan

| Plan | Límite |
|------|--------|
| Starter | 60 rpm |
| Professional | 300 rpm |
| Enterprise | 1000 rpm |
| Custom | configurable |

---

## Comandos de Gestión

```bash
# Validar configuración
deck gateway validate

# Sync config a Kong
deck gateway sync

# Ver estado de salud
curl -s https://api.parkcore.io/health

# Ver métricas Prometheus
curl -s https://api.parkcore.io/metrics
```

---

## Dependencias

- **Infraestructura**: Redis (rate limiting), Kong (API Gateway)
- **Secretos**: JWT_PUBLIC_KEY (vault o env var)
- **Servicios**: Todos dependen del gateway para recibir tráfico

---

## Métricas de Éxito

- Disponibilidad: 99.95% uptime
- Latencia P99: < 50ms (sin contar upstream)
- Rate limit violations: rastreables portrace
- Circuit breaker activations: alertables

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| JWT inválido o expirado | 401 Unauthorized, no se rutea |
| Rate limit excedido | 429 Too Many Requests, retry-after header |
| Servicio upstream down | Circuit breaker abre, 503 con mensaje |
| JWT malformado | 400 Bad Request |
| Trace ID no presente | Generar UUID v4 y inyectar |

---

## Notas

- Kong se configura via declarative config (`deck` CLI)
- Todas las respuestas de error siguen formato: `{ "error": "code", "message": "human readable", "trace_id": "..." }`
- El gateway NO modifica el body de las respuestas upstream
- Health check: `GET /health` retorna `{ "status": "ok", "services": {...} }`