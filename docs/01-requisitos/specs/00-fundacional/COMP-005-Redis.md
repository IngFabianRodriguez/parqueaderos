# COMP-005 — Redis

## Metadata

- **Nombre**: Redis — ParkCore Cache & Session Store
- **Tipo**: Infraestructura (Cache/Session)
- **Prioridad**: Alta
- **Servicios afectados**: API Gateway, auth-service, todos los microservicios
- **Componentes relacionados**: API Gateway, todos los servicios

---

## Objetivo

Proveer cache en memoria y store de sesiones para el sistema. Redis se usa para: rate limiting en el API Gateway, sesión de usuarios (JWT blacklist), cache de consultas frecuentes, cola de jobs (via Redis Streams), y pub/sub para eventos en tiempo real.

---

## Arquitectura

```
[Microservicios / API Gateway]
        ↓ RESP/RESP3
[Redis Cluster — 3 nodes]
        ↓ Sentinel
[Redis Sentinel — 3 nodes]
```

### Topología

| Nodo | Rol | specs |
|------|-----|-------|
| redis-1 | Master | 8 vCPU, 32GB RAM, 200GB SSD |
| redis-2 | Replica | 8 vCPU, 32GB RAM, 200GB SSD |
| redis-3 | Replica | 8 vCPU, 32GB RAM, 200GB SSD |
| sentinel-1 | Sentinel | 2 vCPU, 4GB RAM |
| sentinel-2 | Sentinel | 2 vCPU, 4GB RAM |
| sentinel-3 | Sentinel | 2 vCPU, 4GB RAM |

### Modo de operación

- Redis Cluster en modo `cluster-enabled yes`
- 3 shards, 1 master + 1 replica por shard
- Mínimo 2 replicas para quorum

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| REDIS_VERSION | 7.2 | Versión de Redis |
| MAXMEMORY | 24gb | Memoria maxima por node |
| MAXMEMORY_POLICY | allkeys-lru | Policy de eviction |
| TCP_BACKLOG | 511 | Cola de conexiones |
| TIMEOUT | 300 | Conexiones timeout (seg) |
| TCP_KEEPALIVE | 300 | Keepalive TCP |
| LAZYFREE_LAZY_EVICTION | yes | Lazy free en eviction |
| LAZYFREE_LAZY_EXPIRE | yes | Lazy free en expire |
| APPENDONLY | yes | AOF persistence |
| APPENDFSYNC | everysec | Fsync cada segundo |
| SAVE | 900 1 300 10 60 10000 | RDB snapshots |
| HZ | 100 | HZ del server |

---

## Keys y Estructuras de Datos

### Rate Limiting (API Gateway)

```
Key: ratelimit:{tenant_id}:{user_id}:{minute}
Type: String (contador)
TTL: 60 segundos
```

### Sesiones de Usuario (JWT Blacklist)

```
Key: jwt:blacklist:{jti}
Type: String
TTL: TTL del JWT original
```

### Cache de Consultas Frecuentes

```
Key: cache:{service}:{resource}:{id}
Type: String (JSON serializado)
TTL: configurable por recurso (default 5 min)
```

### Colas de Jobs (Redis Streams)

```
Stream: jobs:{service}
Consumer Group: {service}-workers
```

### Pub/Sub Canales

| Canal | Usado por | Descripción |
|-------|-----------|-------------|
| notifications:{tenant_id} | notif-service | Notificaciones en tiempo real |
| iot:alerts:{sede_id} | iot-service, sede-service | Alertas de sensores |
| reservation:updates:{tenant_id} | reservation-service | Actualizaciones de reserva |

---

## Seguridad

### Autenticación

- `requirepass` via env var (AUTH_PASSWORD)
- Solo accesibles desde red interna (`10.0.0.0/8`, `172.16.0.0/12`)
- TLS para todas las conexiones (configurado en приложение)

### Autorización

- No se usa ACLs individuales (auth a nivel de aplicación)
- Red es trusted network

### Encriptación

- Data at rest: encryption en volumes (no Redis-native)
- TLS en tránsito para clients que lo soporten

---

## Comandos de Gestión

```bash
# Info del cluster
redis-cli --cluster info

# Ver uso de memoria por key
redis-cli --bigkeys

# Scan de keys (con pattern)
redis-cli --scan --pattern 'cache:*' | head -100

#统计
redis-cli info stats | grep -E 'keyspace|hits|misses'

# Ver conexiones
redis-cli client list | wc -l

# Clean cache de un servicio
redis-cli -n {db} KEYS "cache:{service}:*" | xargs redis-cli DEL

# Monitorear comandos en tiempo real
redis-cli monitor --limit 100

# Analizar latencia
redis-cli --latency
```

---

## Monitoreo

### Métricas Clave

- `used_memory_human` / `used_memory_peak_human`
- `keyspace_hits` / `keyspace_misses` (hit ratio)
- `instantaneous_ops_per_sec`
- `connected_clients`
- `repl_backlog_size` / `repl_offset`
- `cluster_stats_messages_received`

### Alertas

| Condición | Severidad |
|-----------|-----------|
| used_memory > 80% maxmemory | WARNING |
| used_memory > 90% maxmemory | CRITICAL |
| hit_ratio < 0.8 (sustained) | WARNING |
| connected_clients > 10000 | WARNING |
| blocked_clients > 0 | WARNING |

---

## Dependencias

- **Infraestructura**: Persistent volumes, Sentinel for failover
- **Secretos**: `REDIS_AUTH_PASSWORD` via Vault
- **Servicios**: API Gateway, auth-service, todos los servicios (cache)

---

## Métricas de Éxito

- Hit ratio: > 85% para cache reads
- Latencia P99: < 10ms para reads, < 20ms para writes
- Disponibilidad: 99.9% uptime (failover automático < 30s)
- Memoria utilizada: < 85% en operación normal

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| Memoria agotada | LRU eviction, logs warning |
| Master down | Sentinel promueve replica, clients reconn |
| Cluster split-brain | Quorum-based election, minority partition readonly |
| Key no existe | Retorna nil, aplicación maneja cache miss |

---

## Notas

- Usar `MGET`/`MSET` para operaciones batch (reduce round trips)
- TTL debe ser setteado en todas las keys para evitar memory leaks
- Connection pooling: max 50 connections por cliente
- Streams para jobs queue (no usar Redis Lists para queues nuevos)