# COMP-003 — PostgreSQL

## Metadata

- **Nombre**: PostgreSQL — ParkCore Database
- **Tipo**: Infraestructura (Database)
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los microservicios
- **Componentes relacionados**: Todos los servicios

---

## Objetivo

Proveer almacenamiento relacional transaccional para todos los servicios del sistema. PostgreSQL es la base de datos principal para datos estructurados: usuarios, tenants, sedes, reservas, transacciones de pago y logs de auditoría.

---

## Arquitectura

```
[Microservicios]
      ↓ lib/pq / psycopg2 / node-postgres
[PostgreSQL 16 — Primary]
      ↓ Streaming Replication
[PostgreSQL 16 — Replica (read-only)]
```

### Topología

| Nodo | Rol | specs |
|------|-----|-------|
| pg-primary | Primary R/W | 4 vCPU, 16GB RAM, 500GB SSD |
| pg-replica-1 | Read replica | 4 vCPU, 16GB RAM, 500GB SSD |

### Bases de datos por servicio

| Base | Propietario | Servicios |
|------|-------------|-----------|
| parkcore_auth | auth-service | auth-service |
| parkcore_tenants | tenant-service | tenant-service |
| parkcore_sedes | sedes-service | sedes-service |
| parkcore_pagos | pagos-service | pagos-service |
| parkcore_iot | iot-service | iot-service |
| parkcore_notif | notif-service | notif-service |
| parkcore_reports | reports-service | reports-service |

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| POSTGRES_VERSION | 16 | Versión del motor |
| POSTGRES_HOST | postgres-primary | Host del primary |
| POSTGRES_PORT | 5432 | Puerto de conexión |
| POSTGRES_MAX_CONNECTIONS | 200 | Conexiones max por servicio |
| POSTGRES_SHARED_BUFFERS | 4GB | Buffer cache |
| POSTGRES_EFFECTIVE_CACHE_SIZE | 12GB | Cache del OS |
| POSTGRES_MAINTENANCE_WORK_MEM | 1GB | Para VACUUM y CREATE INDEX |
| POSTGRES_WAL_LEVEL | logical | Para réplicas y CDC |
| POSTGRES_MAX_REPLICATION_SLOTS | 10 | Slots de replicación |
| POSTGRES_BGWRITER_LAPSE | 200ms | Frecuencia de flush |

---

## Seguridad

### Autenticación

- `pg_hba.conf`: solo允许来自 `10.0.0.0/8` y `172.16.0.0/12`
- Autenticación via SCRAM-SHA-256
- certificados TLS para conexiones entrantes

### Encriptación

- Data at rest: LUKS encryption en volumes
- WAL encryption: `postgresql.conf` → `wal_encryption = on`
- Backups encriptados con AES-256

### Roles y permisos

| Rol | Privilegios | servicios |
|-----|-------------|-----------|
| auth_svc | CONNECT + SELECT + UPDATE en auth | auth-service |
| tenant_svc | CONNECT + ALL en tenants | tenant-service |
| sedes_svc | CONNECT + ALL en sedes | sedes-service |
| pagos_svc | CONNECT + ALL en pagos | pagos-service |
| iot_svc | CONNECT + INSERT + SELECT en iot | iot-service |
| notif_svc | CONNECT + INSERT + SELECT en notif | notif-service |
| reports_svc | CONNECT + SELECT en todos | reports-service |
| backup_user | CONNECT + backup | pgbackrest |

---

## Respaldo y Recuperación

### Estrategia de Backup

| Tipo | Frecuencia | Retención |
|------|------------|-----------|
| Full backup | Diario 02:00 UTC | 30 días |
| WAL continuous | Cada 15 min | 7 días |
| Point-in-time recovery | Activado | 7 días |

### Política deRetención

- Backups diarios: 30 días
- WAL archives: 7 días
- Snapshots: 7 días (para disaster recovery)

### Comandos de Gestión

```bash
# Ver estado de replicación
SELECT * FROM pg_stat_replication;

# Ver retraso de replica
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;

# Forzar switch de WAL
SELECT pg_switch_wal();

# Checkpoint manual
SELECT pg_checkpoint();

# Ver conexiones activas
SELECT datname, numbackends, usename, state FROM pg_stat_activity;
```

---

## Monitoreo

### Métricas Clave

- `pg_stat_database.tup_fetched` / `tup_inserted` / `tup_updated` / `tup_deleted`
- `pg_stat_replication.lag` en bytes
- `pg_stat_activity.count` — conexiones activas
- `pg_bgwriter.buffers_checkpoint` — frecuencia de checkpoints
- WAL generation rate: MB/s

### Alertas

| Condición | Severidad |
|-----------|-----------|
| Lag de replicación > 10MB | WARNING |
| Lag > 100MB | CRITICAL |
| Conexiones > 180 | WARNING |
| Conexiones > 195 | CRITICAL |
| Disk usage > 80% | WARNING |
| Disk usage > 90% | CRITICAL |

---

## Dependencias

- **Infraestructura**: Volumes Persistence (no ephemeral), snapshot backups
- **Secretos**: `POSTGRES_PASSWORD` via Vault
- **Servicios**: Todos los microservicios

---

## Métricas de Éxito

- Disponibilidad: 99.99% uptime
- Tiempo de recuperación (RTO): < 15 min
- Punto de recuperación (RPO): < 15 min
- Latencia de queries P99: < 50ms (operaciones simples), < 500ms (joins complejos)

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| Primary falla | Promover replica a primary, reconfigure connections |
| Disk lleno | Alertar, rechazar writes, mantener reads |
| Conexiones agotadas | Retry con backoff exponencial |
| Corrupción de datos | Restore desde PITR, replay WAL |

---

## Notas

- Extensions recomendadas: `pg_stat_statements`, `pg_buffercache`, `pg_repack`
- conexión pooling via PgBouncer en capa de aplicación
- Vacuum automático cada 5 min para evitar bloat