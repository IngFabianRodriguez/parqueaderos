# COMP-011 — IoT Service

## Metadata

- **Nombre**: iot-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8002
- **DB**: PostgreSQL (schema `iot`)
- **Servicios afectados**: sede-service, tenant-service, auth-service, api-gateway

---

## Objetivo

Gestionar la comunicación con dispositivos IoT (talanqueras, sensores de occupancy, cámaras ANPR) en tiempo real. Handle eventos de entrada/salida de vehículos, controlar apertura de talanqueras, monitorear estado de dispositivos, y publicar eventos al bus de Kafka.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0
- **DB**: PostgreSQL 15
- **Message Broker**: Kafka (topic `iot.events`, `iot.commands`)
- **Protocols**: MQTT (broker Mosquito), HTTP Webhook (para dispositivos legacy)
- **State**: Redis (cache estado dispositivos, TTL 60s)

---

## Modelo de Datos

### Tabla: dispositivos

```
id              UUID PK
tenant_id       UUID FK → tenants
sede_id         UUID FK → sedes
tipo            VARCHAR(30) NOT NULL  -- talanquera, anpr, sensor_occupancy
modelo          VARCHAR(100)
serial_number   VARCHAR(100) NOT NULL UNIQUE
ip_address      VARCHAR(45)
mac_address     VARCHAR(17)
estado          VARCHAR(20) DEFAULT 'offline'  -- online, offline, error, maintenance
ultimo_ping     TIMESTAMPTZ
latencia_ms     INTEGER
config          JSONB DEFAULT '{}'  -- settings específicos por tipo
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: eventos_dispositivo

```
id              UUID PK
dispositivo_id  UUID FK → dispositivos
tipo_evento     VARCHAR(50) NOT NULL  -- entrada, salida, barrera_open, barrera_close, error, heartbeat
payload         JSONB DEFAULT '{}'
timestamp       TIMESTAMPTZ NOT NULL
processed       BOOLEAN DEFAULT false
processed_at    TIMESTAMPTZ
```

### Tabla: comandos

```
id              UUID PK
dispositivo_id  UUID FK → dispositivos
comando         VARCHAR(50) NOT NULL  -- open_barrier, close_barrier, reboot, update_config
payload         JSONB
status          VARCHAR(20) DEFAULT 'pending'  -- pending, sent, acknowledged, failed
sent_at         TIMESTAMPTZ
acknowledged_at TIMESTAMPTZ
result          JSONB
created_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: occupancy_sensors

```
id              UUID PK
dispositivo_id  UUID FK → dispositivos
zona_id         UUID FK → zonas
espacios_total  INTEGER NOT NULL
espacios_ocupados INTEGER DEFAULT 0
ultima_actualizacion TIMESTAMPTZ
```

---

## Endpoints

### GET /api/v1/iot/devices
Lista todos los dispositivos con filtros.
**Query params**: `tenant_id`, `sede_id`, `tipo`, `estado`
**Response 200**:
```json
{
  "devices": [
    {
      "id": "uuid",
      "tipo": "talanquera",
      "serial_number": "TG-2024-001",
      "estado": "online",
      "latencia_ms": 45,
      "sede_id": "uuid"
    }
  ],
  "total": 42
}
```

### GET /api/v1/iot/devices/:id
Detalle de un dispositivo específico.

### POST /api/v1/iot/devices
Registrar nuevo dispositivo.
```json
{
  "tenant_id": "uuid",
  "sede_id": "uuid",
  "tipo": "talanquera",
  "modelo": "ZKTeco SB-T4",
  "serial_number": "TG-2024-001",
  "ip_address": "192.168.1.100",
  "config": { "relay_enabled": true, "sensor_loop": 1 }
}
```

### PATCH /api/v1/iot/devices/:id
Actualizar config o estado de dispositivo.

### POST /api/v1/iot/devices/:id/commands
Enviar comando a dispositivo.
```json
{
  "comando": "open_barrier",
  "payload": { "duration_ms": 5000 }
}
```
**Response 202**:
```json
{
  "command_id": "uuid",
  "status": "pending"
}
```

### GET /api/v1/iot/devices/:id/commands/:cmd_id
Estado de un comando.

### GET /api/v1/iot/occupancy
Occupancy actual por sede/zona.
**Query params**: `sede_id`, `zona_id`
```json
{
  "sede_id": "uuid",
  "zonas": [
    {
      "zona_id": "uuid",
      "zona_nombre": "Nivel 1",
      "espacios_total": 50,
      "espacios_ocupados": 32,
      "porcentaje_ocupacion": 64
    }
  ]
}
```

### POST /api/v1/iot/webhook
Endpoint para recibir eventos de dispositivos via HTTP webhook (dispositivos legacy sin MQTT).
```json
{
  "device_serial": "TG-2024-001",
  "event_type": "entrada",
  "timestamp": "2026-01-15T10:30:00Z",
  "payload": { "plate": "ABC123", "confidence": 0.95 }
}
```

### GET /api/v1/iot/events
Consulta histórica de eventos.
**Query params**: `device_id`, `tipo_evento`, `from`, `to`, `limit`, `offset`

---

## Flujo de Entrada/Salida de Vehículo

```
1. Sensor de occupancy detecta cambio → publica en MQTT
2. iot-service recibe mensaje MQTT → valida dispositivo
3. Busca cliente por placa (via anpr-service o registro manual)
4. Registra evento en eventos_dispositivo (status = pending)
5. Si entrada:
   - Crea registro de ingreso en tabela ingresos
   - Abre talanquera (comando open_barrier)
6. Si salida:
   - Consulta tarifa y calcula tiempo/monto
   - Verifica pago (consulta payment-service)
   - Si pagado → abre talanquera
   - Si no pagado → genera alerta a operador
7. Publica evento en Kafka topic iot.events
8. Marca evento como processed
```

---

## Protocolos de Comunicación

### MQTT (Dispositivos modernos)

```yaml
Broker: mosquitto (puerto 1883)
Topics:
  parkcore/devices/{serial}/events    # Inbound eventos
  parkcore/devices/{serial}/commands # Outbound comandos
  parkcore/devices/{serial}/status    # Heartbeat/estado
QoS: 1 (at least once delivery)
Retain: false
```

### HTTP Webhook (Dispositivos legacy)

- POST /api/v1/iot/webhook con firma HMAC-SHA256 en header `X-Signature`
- Retry: 3 intentos con exponential backoff (1s, 5s, 30s)
- Timeout: 10s por request

---

## Control de Talanqueras

### Comando: open_barrier

1. Validar que dispositivo es talanquera y está online
2. Verificar que no hay comando pendiendo previo
3. Publicar comando en MQTT topic `parkcore/devices/{serial}/commands`
4. Guardar comando en BD con status=pending
5. Esperar acknowledge (timeout 30s)
6. Si acknowledged → status=acknowledged, abrir talanquera
7. Si timeout → status=failed, registrar error

### Seguridad

- Cada talanquera tiene config de `relay_duration_ms` (default 5000ms)
- Rate limit: max 10 comandos por minuto por dispositivo
- Double-tap required: para abrir, se debe enviar comando 2 veces en < 2s

---

## Monitoreo de Estado

### Heartbeat

- Dispositivos envían heartbeat cada 30s via MQTT
- Si no hay heartbeat en 90s → estado = offline
- Si 3 heartbeats fallidos consecutivos → estado = error, alertar a ops

### Latencia

- Cada mensaje MQTT incluye timestamp del dispositivo
- iot-service calcula latencia = now - device_timestamp
- Si latencia > 5000ms → flag en dispositivo, alerta

---

## Kafka Integration

### Topics

| Topic | Direction | Partitions | Purpose |
|-------|-----------|------------|---------|
| `iot.events` | outbound | 8 | Todos los eventos de dispositivos |
| `iot.commands` | inbound | 8 | Comandos a dispositivos |
| `iot.devices.status` | outbound | 4 | Cambios de estado de dispositivos |

### Message Schemas

```json
// iot.events (entrada/salida)
{
  "event_id": "uuid",
  "tenant_id": "uuid",
  "sede_id": "uuid",
  "dispositivo_id": "uuid",
  "event_type": "entrada",
  "timestamp": "2026-01-15T10:30:00Z",
  "plate": "ABC123",
  "confidence": 0.95,
  "metadata": {}
}
```

```json
// iot.commands
{
  "command_id": "uuid",
  "dispositivo_id": "uuid",
  "comando": "open_barrier",
  "payload": {},
  "issued_by": "operator_id",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

---

## Dependencias

- **DB**: PostgreSQL `iot` schema
- **Kafka**: cluster con 3 brokers, topics iot.*
- **Redis**: cache estado dispositivos
- **MQTT Broker**: Mosquito (puede ser compartido con otros servicios IoT)
- **auth-service**: validación JWT para endpoints admin
- **anpr-service**: (integración) para enriquecimiento de eventos con OCR

---

## Métricas

- `iot_devices_total{tenant, tipo, estado}`
- `iot_events_received_total{tipo_evento}`
- `iot_commands_total{comando, status}`
- `iot_command_duration_ms`
- `iot_device_latency_ms`
- `iot_webhook_events_total`
- `iot_webhook_processing_duration_ms`

---

## Health Checks

- `GET /health` → `{ "status": "ok", "mqtt": "connected", "kafka": "connected" }`
- `GET /health/ready` → verifica DB, MQTT broker, Kafka
- `GET /health/live` → solo proceso corriendo
- `GET /api/v1/iot/health/:device_id` → health individual de dispositivo

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| MQTT broker down | Buffer en memoria (max 1000 eventos), retry con backoff |
| Comando a dispositivo offline | Status=failed, notificar a operador, no reintentar automáticamente |
| Webhook signature inválida | 401 Unauthorized, log evento sospechoso |
| Payload malformado | 400 Bad Request, log para debugging |
| Device ID desconocido | 404 Not Found, reject evento |
| Evento duplicado (same event_id) | Deduplicate basado en event_id + timestamp, procesar solo uno |