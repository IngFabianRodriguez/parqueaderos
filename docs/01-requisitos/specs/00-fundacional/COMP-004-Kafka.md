# COMP-004 — Kafka

## Metadata

- **Nombre**: Apache Kafka — ParkCore Event Bus
- **Tipo**: Infraestructura (Message Broker)
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los microservicios
- **Componentes relacionados**: Todos los servicios internos, consumer groups

---

## Objetivo

Proporcionar un bus de mensajería de eventos para comunicación asíncrona entre microservicios. Kafka es elbackbone para eventos de dominio: ingresos de vehículos, cambios de estado de reservas, transacciones de pago, alertas IoT y logs de auditoría.

---

## Arquitectura

```
[Productores] → [Kafka Cluster] → [Consumidores]
                        ↓
               [Schema Registry]
                        ↓
               [Kafka Connect] → [S3 Sink]
```

### Topología de Cluster

| Nodo | Rol | specs |
|------|-----|-------|
| kafka-1 | Broker + Controller | 8 vCPU, 32GB RAM, 1TB SSD |
| kafka-2 | Broker | 8 vCPU, 32GB RAM, 1TB SSD |
| kafka-3 | Broker | 8 vCPU, 32GB RAM, 1TB SSD |

### Replication Factor

- Tópicos críticos: RF=3, min.insync.replicas=2
- Tópicos no críticos: RF=3, min.insync.replicas=1

### Configuración de Jvm

```properties
-Xms16g -Xmx16g
-XX:+UseG1GC
-XX:MaxGCPauseMillis=20
-XX:InitiatingHeapOccupancyPercent=35
-Djava.net.preferIPv4Stack=true
```

---

## Topics

| Topic | Particiones | RF | Retention | Descripción |
|-------|-------------|----|-----------|-------------|
| vehicle.ingress | 12 | 3 | 7 días | Eventos de ingreso ANPR |
| vehicle.egress | 12 | 3 | 7 días | Eventos de salida ANPR |
| reservation.created | 6 | 3 | 14 días | Nuevas reservas |
| reservation.updated | 6 | 3 | 14 días | Cambios de reserva |
| reservation.cancelled | 6 | 3 | 14 días | Cancelaciones |
| payment.initiated | 9 | 3 | 30 días | Inicio de pago |
| payment.completed | 9 | 3 | 30 días | Pago exitoso |
| payment.failed | 9 | 3 | 30 días | Pago fallido |
| iot.sensor-events | 12 | 3 | 3 días | Eventos de sensores IoT |
| iot.alerts | 6 | 3 | 30 días | Alertas de sensores |
| notification.push | 6 | 3 | 7 días | Envío de notificaciones push |
| notification.email | 6 | 3 | 7 días | Envío de emails |
| audit.logs | 12 | 3 | 90 días | Logs de auditoría |

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| KAFKA_VERSION | 3.6 | Versión de Kafka |
| NUM_PARTITIONS | 6 | Default partitions por topic |
| LOG_RETENTION_MS | 604800000 (7 días) | Retención default |
| LOG_RETENTION_BYTES | -1 (ilimitado) | Límite por segment |
| NUM_NETWORK_THREADS | 8 | Hilos de red |
| NUM_IO_THREADS | 32 | Hilos de I/O |
| SOCKET_SEND_BUFFER_BYTES | 102400 | Buffer send |
| SOCKET_RECEIVE_BUFFER_BYTES | 102400 | Buffer receive |
| LOG_SEGMENT_BYTES | 1073741824 (1GB) | Tamaño de segment |
| LOG_RETENTION_CHECK_INTERVAL_MS | 300000 (5 min) | Frecuencia de cleanup |
| AUTO_CREATE_TOPICS_ENABLE | false | No auto-crear topics |

---

## Consumers Groups

| Grupo | Serviços | Tópicos | Offset reset |
|-------|----------|---------|--------------|
| auth-events | auth-service | audit.logs | earliest |
| reservation-processor | sede-service | reservation.* | earliest |
| payment-processor | pagos-service | payment.* | earliest |
| anpr-processor | anpr-service | vehicle.* | earliest |
| iot-event-handler | iot-service | iot.sensor-events | latest |
| notification-handler | notif-service | notification.* | earliest |
| reports-aggregator | reports-service | vehicle.*, payment.* | earliest |

---

## Schema Registry

- URL: `http://schema-registry:8081`
- Compatibility: `BACKWARD`
- Serialization: Avro
- Subjects:

| Subject | Version |
|---------|---------|
| vehicle.ingress-value | 1 |
| vehicle.egress-value | 1 |
| reservation.created-value | 1 |
| payment.completed-value | 1 |
| iot.sensor-events-value | 1 |

---

## Seguridad

### Autenticación

- SASL/PLAIN para producers y consumers
- mTLS entre brokers (certificados internos)

### Autorización

- ACLs por principal
- Productors y consumers tienen permisos específicos por topic

### Encriptación

- TLS en todas las conexiones (SASL_SSL)
- Data at rest: encryption en volumes

---

## Comandos de Gestión

```bash
# Listar topics
kafka-topics --bootstrap-server kafka:9092 --list

# Describe topic
kafka-topics --bootstrap-server kafka:9092 --describe --topic vehicle.ingress

# Ver consumer groups
kafka-consumer-groups --bootstrap-server kafka:9092 --list

# Reset offset (cuidadoso!)
kafka-consumer-groups --bootstrap-server kafka:9092 --reset-offsets --group reports-aggregator --topic vehicle.ingress --to-earliest

# Ver lag de consumer
kafka-consumer-groups --bootstrap-server kafka:9092 --describe --group reservation-processor

# Producer de test
kafka-console-producer --bootstrap-server kafka:9092 --topic test-topic

# Consumer de test
kafka-console-consumer --bootstrap-server kafka:9092 --topic test-topic --from-beginning

# Ver segmentos de un topic
kafka-log-dirs --bootstrap-server kafka:9092 --describe --topic-list vehicle.ingress
```

---

## Monitoreo

### Métricas Clave

- `kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec`
- `kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec`
- `kafka.consumer:type=consumer-fetch-manager-metrics,client-id=.*,name=records-lag-max`
- `kafka.producer:type=producer-metrics,client-id=.*,name=record-send-rate`
- Under replicated partitions (URP)
- Offline partitions

### Alertas

| Condición | Severidad |
|-----------|-----------|
| URP > 0 | WARNING |
| URP > 0 por > 5 min | CRITICAL |
| Consumer lag > 10000 | WARNING |
| Consumer lag > 50000 | CRITICAL |
| Disk usage > 80% | WARNING |
| Disk usage > 90% | CRITICAL |

---

## Dependencias

- **Infraestructura**: Zookeeper (para Kafka < 3.6, o KRaft self-hosted), Persistent volumes
- **Secretos**: `KAFKA_SASL_PASSWORD` via Vault
- **Servicios**: Todos los productores y consumidores

---

## Métricas de Éxito

- Throughput: 100K msgs/s cluster-wide
- Latencia P99: < 100ms end-to-end
- Durabilidad: 0 data loss (min.insync.replicas=2)
- Disponibilidad: 99.95% uptime

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| Broker down | ISR shrinks, producers retry con backoff |
| Consumer crash | Offset no actualizado, rebalance triggered |
| Topic sin producers | Datos retention por configured time |
| Schema incompatible | Schema Registry rejects, mensaje no producido |

---

## Notas

- Usar transacciones Exactly-Once para payments
- Idempotent producers para todos los topics
- Max poll records: 500 (balance latency vs throughput)
- Session timeout consumers: 30s