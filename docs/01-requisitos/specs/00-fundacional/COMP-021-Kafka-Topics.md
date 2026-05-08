# COMP-021 — Event Schema Registry & Kafka Topics

## Metadata

- **Nombre**: Event Schema Registry + Kafka Topics
- **Tipo**: Mensajería Asíncrona (Event-Driven)
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los microservicios

---

## Objetivo

Definir todos los topics de Kafka, sus schemas (JSON Schema), consumer groups, y las reglas de evolución de eventos. Todo evento publicado a Kafka debe estar versionado y ser backward-compatible.

---

## Schema Registry

- **Ubicación**: `/schemas/` en el repo, versionado en Git
- **Formato**: JSON Schema draft-07
- **Naming**: `{topic_name}/{version}.json`
- **Validation**: Cada servicio valida su input/output contra el schema antes de publicar/consumir
- **Tool**: Confluent Schema Registry (auto-registro) o validación manual con `ajv`

---

## Catálogo de Topics

### Topic: `vehicle.entered`

**Publicado por**: anpr-service
**Consumido por**: iot-service, pagos-service, notif-service, sedes-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VehicleEntered",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "placa", "sede_id", "talanquera_id", "timestamp", "source"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "placa": { "type": "string", "pattern": "^[A-Z0-9]{5,7}$" },
    "sede_id": { "type": "string", "format": "uuid" },
    "talanquera_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "confianza_anpr": { "type": "number", "minimum": 0, "maximum": 100 },
    "espacio_id": { "type": "string", "format": "uuid", "nullable": true },
    "source": { "type": "string", "enum": ["anpr", "manual", "emergency"] }
  }
}
```

### Topic: `vehicle.exited`

**Publicado por**: anpr-service
**Consumido por**: iot-service, pagos-service, notif-service, sedes-service, billing-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VehicleExited",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "placa", "sede_id", "talanquera_id", "timestamp", "registro_entrada_id"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "placa": { "type": "string", "pattern": "^[A-Z0-9]{5,7}$" },
    "sede_id": { "type": "string", "format": "uuid" },
    "talanquera_id": { "type": "string", "format": "uuid" },
    "registro_entrada_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" },
    "duracion_minutos": { "type": "integer", "minimum": 0 },
    "source": { "type": "string", "enum": ["anpr", "manual", "emergency"] }
  }
}
```

### Topic: `payment.confirmed`

**Publicado por**: pagos-service
**Consumido por**: iot-service, notif-service, billing-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PaymentConfirmed",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "pago_id", "registro_entrada_id", "monto", "forma_pago", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "pago_id": { "type": "string", "format": "uuid" },
    "registro_entrada_id": { "type": "string", "format": "uuid" },
    "cliente_id": { "type": "string", "format": "uuid" },
    "monto": { "type": "number", "minimum": 0 },
    "forma_pago": { "type": "string", "enum": ["efectivo", "tarjeta", "transferencia", "prepago", "nequi", "daviplata"] },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Topic: `payment.failed`

**Publicado por**: pagos-service
**Consumido por**: notif-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PaymentFailed",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "pago_id", "registro_entrada_id", "razon", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "pago_id": { "type": "string", "format": "uuid" },
    "registro_entrada_id": { "type": "string", "format": "uuid" },
    "razon": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Topic: `talanquera.commanded`

**Publicado por**: iot-service
**Consumido por**: none (solo para logging/auditoría)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TalanqueraCommanded",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "talanquera_id", "sede_id", "comando", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "talanquera_id": { "type": "string", "format": "uuid" },
    "sede_id": { "type": "string", "format": "uuid" },
    "comando": { "type": "string", "enum": ["abrir", "cerrar", "bloquear"] },
    "usuario_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Topic: `notification.requested`

**Publicado por**: cualquier servicio
**Consumido por**: notif-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NotificationRequested",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "destinatario_id", "tipo", "canal", "template_id", "payload", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "destinatario_id": { "type": "string", "format": "uuid" },
    "destinatario_tipo": { "type": "string", "enum": ["cliente", "operador", "admin"] },
    "tipo": { "type": "string", "enum": ["entrada", "salida", "pago", "mora", "alerta", "promocion"] },
    "canal": { "type": "string", "enum": ["push", "sms", "email", "whatsapp"] },
    "template_id": { "type": "string" },
    "payload": { "type": "object" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Topic: `session.created`

**Publicado por**: auth-service
**Consumido por**: audit-service, notif-service (para login alerts)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SessionCreated",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "user_id", "tenant_id", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "user_id": { "type": "string", "format": "uuid" },
    "tenant_id": { "type": "string", "format": "uuid", "nullable": true },
    "ip_address": { "type": "string" },
    "user_agent": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### Topic: `tenant.lifecycle`

**Publicado por**: tenant-service
**Consumido por**: billing-service, metrics-service, notif-service

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TenantLifecycle",
  "version": "1.0.0",
  "type": "object",
  "required": ["event_id", "tenant_id", "evento", "timestamp"],
  "properties": {
    "event_id": { "type": "string", "format": "uuid" },
    "tenant_id": { "type": "string", "format": "uuid" },
    "evento": { "type": "string", "enum": ["created", "trial_started", "converted", "upgraded", "downgraded", "suspended", "churned"] },
    "plan_id": { "type": "string", "format": "uuid" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

---

## Consumer Groups

| Consumer Group | Topics | Servicio |
|----------------|--------|----------|
| `anpr-service-consumers` | vehicle.entered, vehicle.exited | anpr-service |
| `iot-service-consumers` | vehicle.entered, vehicle.exited, payment.confirmed, talanquera.commanded | iot-service |
| `pagos-service-consumers` | vehicle.entered, vehicle.exited, notification.requested | pagos-service |
| `notif-service-consumers` | notification.requested, payment.confirmed, payment.failed, session.created, tenant.lifecycle | notif-service |
| `billing-service-consumers` | payment.confirmed, tenant.lifecycle | billing-service |
| `audit-service-consumers` | session.created, talanquera.commanded, tenant.lifecycle | audit-service |
| `metrics-service-consumers` | vehicle.entered, vehicle.exited, payment.confirmed, tenant.lifecycle | metrics-service |

---

## Reglas de Evolución de Schemas

1. **Adición de campos**: Solo agregar campos opcionales (con `nullable: true` o `default`)
2. **Eliminación de campos**: Nunca eliminar campos, marcarlos como deprecated en la文档
3. **Cambio de tipo**: Crear nuevo schema versionado; no cambiar tipos existentes
4. **Validación**: Antes de publicar, validar contra schema con `ajv` (Python) o `ajv` (JS/TS)

---

## Retención y Throughput Estimado

| Topic | Retención | Particiones | Throughput estimado |
|-------|----------|-------------|---------------------|
| vehicle.entered | 7 días | 16 | 100/segundo peak |
| vehicle.exited | 7 días | 16 | 100/segundo peak |
| payment.confirmed | 30 días | 8 | 50/segundo peak |
| payment.failed | 7 días | 4 | 10/segundo peak |
| talanquera.commanded | 30 días | 4 | 20/segundo peak |
| notification.requested | 3 días | 8 | 200/segundo peak |
| session.created | 30 días | 4 | 10/segundo peak |
| tenant.lifecycle | 365 días | 2 | 1/minuto |

---

## Seguridad

- **SASL/SCRAM**: Auth con username/password para cada consumer/producer
- **TLS**: Encriptación en tránsito (certificado interno)
- **Topic ACLs**: Cada servicio solo puede producir/consumir sus topics asignados

---

## Comandos de Gestión

```bash
# Listar topics
kafka-topics.sh --bootstrap-server kafka:9092 --list

# Describe topic
kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic vehicle.entered

# Reset consumer group offset
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group iot-service-consumers --topic vehicle.entered \
  --reset-offsets --to-earliest --execute

# Ver consumer lag
kafka-consumer-groups.sh --bootstrap-server kafka:9092 \
  --group iot-service-consumers --describe
```

---

## Dependencias

- **Infraestructura**: Kafka cluster (3+ brokers), ZooKeeper o KRaft
- **Schema Registry**: Confluent Schema Registry o archivo JSON en Git
- **Clients**: confluent-kafka-python (Python), kafkajs (Node.js)

---

## Métricas

- `kafka_consumer_lag{topic, group}` —滞后 (alert si > 1000)
- `kafka_messages_produced_total{topic}` — throughput publicado
- `kafka_messages_consumed_total{topic, group}` — throughput consumido
- `kafka_schema_validation_errors{topic}` — errores de validación (alert si > 0)