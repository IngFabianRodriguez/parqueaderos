# Manual de Operaciones (DevOps / SRE)

## Introducción

Este manual está dirigido al equipo de operaciones, DevOps e SRE de ParkCore. Contiene las guías, configuraciones y procedimientos necesarios para mantener la plataforma en producción.

---

## 1. Monitoreo

### Dashboards en Grafana

El monitoreo de infraestructura se realiza a través de **Grafana** accessible en `https://grafana.parkcore.internal`.

**Dashboards disponibles:**

| Dashboard | Descripción | Refresh |
|-----------|-------------|---------|
| Infrastructure Overview | Uso de CPU, RAM, disco, red de todos los nodos | 30s |
| API Performance | Latencia, requests/seg, errores por endpoint | 15s |
| ANPR Cameras | Estado de cámaras, fps, placas procesadas | 10s |
| Database PostgreSQL | Conexiones, queries lentas,Replication status | 30s |
| MQTT Broker | Mensajes/seg, clientes conectados, topics activos | 15s |
| Business Intelligence | Ingresos, parqueos/hora, ocupación por sede | 5min |

### Alertas en PagerDuty/Opsgenie

Las alertas se configuran en **PagerDuty** para on-call y **Opsgenie** como backup.

**Reglas de alerta configuradas:**

| Alerta | Condición de disparo | Severidad | Canal de notificación |
|--------|---------------------|-----------|----------------------|
| API Latency Alta | Latencia promedio > 1s por 5 minutos | P2 | PagerDuty (on-call) |
| Tasa de errores | Errors > 1% por 10 minutos | P2 | PagerDuty (on-call) |
| Talanquera sin responder | Sin respuesta > 30 segundos | P1 | PagerDuty (immediate) |
| Base de datos inalcanzable | PG unreachable por 30s | P1 | PagerDuty (immediate) |
| Disco crítico | Uso > 85% en cualquier nodo | P3 | Slack + Opsgenie |
| MQTT desconectado | Broker unreachable por 1min | P2 | PagerDuty (on-call) |

---

## 2. Logs

### Dónde encontrar los logs

**En contenedores Docker:**

```bash
# Logs de la API
docker logs -f parkcore-api

# Logs del worker de ANPR
docker logs -f parkcore-anpr-worker

# Logs del servicio de pagos
docker logs -f parkcore-payments

# Logs del broker MQTT
docker logs -f parkcore-mqtt-broker
```

**Logs persistidos en disco:**

```
/var/log/parkcore/
├── api/
│   ├── access.log
│   └── error.log
├── anpr/
│   ├── detector.log
│   └── ocr.log
├── payments/
│   └── transaction.log
└── mqtt/
    └── broker.log
```

### Formato estructurado JSON

Todos los logs de aplicación usan formato JSON estructurado para facilitar el parsing:

```json
{
  "timestamp": "2026-05-08T00:15:32.456Z",
  "level": "INFO",
  "service": "parkcore-api",
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "span_id": "xyz789",
  "message": "Pago confirmado exitosamente",
  "context": {
    "user_id": "usr_abc123",
    "transaction_id": "txn_xyz789",
    "amount": 12500,
    "method": "PSE"
  }
}
```

### Buscar por trace_id

Para seguir una transacción completa a través de todos los servicios:

```bash
# Buscar en todos los logs un trace_id específico
grep -r "a1b2c3d4-e5f6-7890-abcd-ef1234567890" /var/log/parkcore/

# En Docker, filtrar por trace_id
docker logs parkcore-api 2>&1 | grep "a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Usar jq para parsear logs JSON y filtrar por trace_id
cat /var/log/parkcore/api/access.log | jq 'select(.trace_id == "a1b2c3d4-e5f6-7890-abcd-ef1234567890")'
```

---

## 3. Variables de Entorno Críticas

Estas variables deben estar configuradas en todos los entornos. **Nunca exponer en repositorios públicos.**

### Variables de la Aplicación

```bash
# Base de datos
DATABASE_URL=postgresql://parkcore:${DB_PASSWORD}@pg-primary:5432/parkcore_db
DATABASE_URL_REPLICA=postgresql://parkcore:${DB_PASSWORD}@pg-replica:5432/parkcore_db

# Redis / Cache
REDIS_URL=redis://:${REDIS_PASSWORD}@redis-cluster:6379/0

# Autenticación JWT
JWT_SECRET=${JWT_SECRET}
JWT_EXPIRATION_HOURS=24

# Servicio ANPR
ANPR_API_URL=http://anpr-processor:8080
ANPR_API_KEY=${ANPR_API_KEY}
ANPR_MODEL_PATH=/models/lpr_yolo.onnx

# Pasarela de pagos — Wompi
PASARELA_WOMPI_KEY=${PASARELA_WOMPI_KEY}
PASARELA_WOMPI_PUBLIC_KEY=${PASARELA_WOMPI_PUBLIC_KEY}
PASARELA_WOMPI_EVENT_SECRET=${PASARELA_WOMPI_EVENT_SECRET}
PASARELA_WOMPI_ENV=sandbox  # Cambiar a 'production' en prod

# Broker MQTT
MQTT_BROKER_URL=mqtt://${MQTT_USER}:${MQTT_PASSWORD}@mqtt-broker:1883
MQTT_TOPIC_PREFIX=parkcore

# Correo / Notificaciones
SMTP_HOST=smtp.sendgrid.net
SMTP_USER=apikey
SMTP_PASSWORD=${SMTP_PASSWORD}
NOTIFICATION_EMAIL_FROM=noreply@parkcore.com
```

### Gestión de Secretos

- **Desarrollo local**: Usar `.env` file (no commitear)
- **Staging/Prod**: Usar **HashiCorp Vault** o **AWS Secrets Manager**
- Rotación de secrets cada 90 días

---

## 4. Backups

### PostgreSQL

**Configuración de backup automático:**

- **Frecuencia**: Diario a las 3:00 AM (hora del servidor)
- **Retención**: 30 días
- **Ubicación**: Bucket S3 `s3://parkcore-backups/postgresql/`
- **Herramienta**: `pgBackRest` con configuración en `/etc/pgbackrest/pgbackrest.conf`

**Comando para verificar estado de backups:**

```bash
pgbackrest info --stanza=parkcore
```

**Restauración de un backup ( Point-in-Time Recovery ):**

```bash
# 1. Detener la aplicación
docker-compose stop

# 2. Ejecutar restauración
pgbackrest restore --stanza=parkcore --type=time --target="2026-05-08 00:00:00"

# 3. Iniciar PostgreSQL en modo recovery
pg_ctl start -D /var/lib/postgresql/data

# 4. Verificar integridad
psql -U parkcore_user -d parkcore_db -c "SELECT 1;"

# 5. Reiniciar aplicación
docker-compose up -d
```

**Prueba de restore trimestral:**

- Se realiza cada **3 meses** (marzo, junio, septiembre, diciembre)
- Documentado en runbook `RUNBOOK-BACKUP-RESTORE-TEST.md`
- Verificar que datos restaurados coincidan con backup

---

## 5. Despliegues

### Despliegue estándar con Docker Compose

```bash
# 1. Pull de la última versión
docker-compose pull

# 2. Aplicar migraciones de BD (si hay nuevas)
docker-compose run --rm api python manage.py migrate

# 3. Reiniciar servicios con nuevas imágenes
docker-compose up -d

# 4. Verificar salud de los servicios
docker-compose ps
curl -f https://api.parkcore.com/health
```

### Blue-Green Deployment para APIs

Para minimizar downtime en actualizaciones de API:

1. **Desplegar nueva versión en paralelo**:
   ```bash
   # azul (versión actual)
   docker-compose -f docker-compose.blue.yml up -d
   
   # verde (nueva versión)
   docker-compose -f docker-compose.green.yml up -d
   ```

2. **Verificar nueva versión** en `api-green.parkcore.com`

3. **Switch de tráfico** via Nginx upstream

4. **Desactivar versión antigua** una vez validada

### Rollback

Si algo falla después del despliegue:

```bash
# Identificar la versión anterior
docker-compose images | grep parkcore

# Hacer rollback a versión específica
docker-compose down
git checkout v1.2.3
docker-compose up -d
```

---

## 6. Gestión de Incidentes

### Severidades

| Severidad | Definición | Tiempo de respuesta | Ejemplos |
|-----------|------------|--------------------|----------|
| **P1 — Crítica** | Sistema completamente caído o data en riesgo | Inmediato (< 5 min) | BD inalcanzable, talanquera abierta sin control, fuga de datos |
| **P2 — Alta** | Funcionalidad principal afectada, degradación significativa | 15 minutos | API lenta > 5s, pagos no procesando, ANPR fuera de línea |
| **P3 — Media** | Funcionalidad secundaria afectada, workaround disponible | 1 hora | Reportes lentos, notificaciones no enviadas |
| **P4 — Baja** | Issues menores, sin impacto en operación | Siguiente día hábil | UI con bugs cosméticos, logs excesivos |

### Canal de Comunicación

- **Slack**: Canal `#parkcore-ops` para coordinación en tiempo real
- **PagerDuty**: Escalamiento automático para P1 y P2
- **Jira**: Creación de incidentes para seguimiento post-mortem

### Runbooks para P1

#### Runbook: Talanquera no abre tras pago confirmado

```
1. VERIFICAR: ¿El pago está confirmado en la BD? (SELECT * FROM payments WHERE status='confirmed')
2. VERIFICAR: ¿El broker MQTT está activo? (docker ps | grep mqtt)
3. VERIFICAR: ¿El servicio de talanquera recibe mensajes? (docker logs parkcore-boom barrier)
4. ACCIÓN: Reiniciar servicio de talanquera si no responde
   docker-compose restart barrier-controller
5. ACCIÓN: Si persiste, abrir talanquera manualmente vía botón físico (registrar en log)
6. NOTIFICAR: Informar al líder de operaciones y al cliente afectado
7. post-mortem: Documentar causa raíz en las siguientes 48h
```

#### Runbook: ANPR caído

```
1. VERIFICAR: ¿El servicio de ANPR está corriendo? (docker ps | grep anpr)
2. VERIFICAR: ¿Las cámaras tienen conexión de red? (ping cam-ip)
3. VERIFICAR: ¿El modelo LPR está cargado? (docker logs anpr-worker | grep "model loaded")
4. ACCIÓN: Reiniciar contenedor ANPR
   docker-compose restart anpr-worker
5. ACCIÓN: Si el modelo falla, recargar desde S3
   aws s3 cp s3://parkcore-models/lpr_yolo.onnx /models/
6. ACCIÓN: Habilitar modo manual fallback en caseta
7. NOTIFICAR: Al equipo de infraestructura para escalar
8. post-mortem: Documentar causa raíz
```

#### Runbook: Base de datos inalcanzable

```
1. VERIFICAR: ¿PG primary está corriendo? (docker ps | grep postgres)
2. VERIFICAR: ¿PG replica está sincronizada? (pg_stat_replication)
3. ACCIÓN: Si primary caída:
   - Promote replica a primary: pg_ctl promote
   - Actualizar DATABASE_URL en configuración
   - Restart aplicación
4. ACCIÓN: Si conexión de red, verificar firewall y NAT
5. NOTIFICAR: P1 inmediata, invocar plan de DR si PG inaccesible > 10 min
6. post-mortem: Documentar causa raíz
```

---

## 7. Escalado

### Escalado Horizontal (Más instancias/replicas)

Para aumentar la capacidad de procesamiento de la API:

```bash
# Escalar API a 4 réplicas
docker-compose up -d --scale api=4

# Verificar que el balanceador de carga reconoce las nuevas réplicas
docker-compose ps

# Monitorear load balancer en Grafana
# Endpoint: https://grafana.parkcore.internal/d/api-load-balancer
```

**Consideraciones:**
- El API gateway debe tener health checks configurados
- Las sesiones deben estar en Redis (no locales)
- La base de datos es el bottleneck más común — monitorear conexiones PG

### Escalado Vertical (Más recursos)

Para PostgreSQL en RDS:

```bash
# Cambiar clase de instancia RDS (requiere restart)
# via AWS Console o CLI:
aws rds modify-db-instance \
  --db-instance-identifier parkcore-pg \
  --db-instance-class db.r6g.xlarge \
  --apply-immediately

# Verificar que los nuevos recursos son utilizados
SELECT * FROM pg_stat_activity ORDER BY query_start;
```

**Métricas a monitorear después de escalar:**
- CPU utilization (target < 70%)
- Memory usage
- connections (max_connections vs used)
- disk I/O

---

## 8. Health Checks

### Endpoint `/health` — Salud general

Retorna `200 OK` si la aplicación está corriendo y puede responder requests básicos.

```
GET /health

Response 200:
{
  "status": "OK",
  "version": "1.2.3",
  "uptime_seconds": 86400
}
```

### Endpoint `/health/ready` — Readiness

Retorna `200 OK` solo si **todas** las dependencias están conectadas (BD, Redis, MQTT).

```
GET /health/ready

Response 200:
{
  "status": "ready",
  "checks": {
    "database": "connected",
    "redis": "connected",
    "mqtt": "connected",
    "anpr_service": "available"
  }
}

Response 503 (si alguna dependencia falla):
{
  "status": "not_ready",
  "checks": {
    "database": "connected",
    "redis": "disconnected",
    "mqtt": "connected"
  }
}
```

### Verificación manual

```bash
# Health check rápido en todos los servicios
for service in api anpr-worker payments mqtt-broker; do
  echo "Checking $service..."
  docker inspect --format='{{.State.Health.Status}}' parkcore-$service
done
```

---

*Documento actualizado: Mayo 2026*
*Versión: 1.0*
*ParkCore — Operaciones*
