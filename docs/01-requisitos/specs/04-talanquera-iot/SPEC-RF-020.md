# SPEC-04-020 — Monitoreo de estado de talanquera en tiempo real

## Metadata
- **RF origen**: RF-020
- **Módulo**: 04-talanquera-iot
- **Prioridad**: Alta
- **Servicios**: iot-gateway, parking-service, websocket-service

---

## User Story
Como Administrador de sede, Operador de control **quiero** conocer el estado actual de cada talanquera (abierta, cerrada, en movimiento, error, offline) en tiempo real **para** tomar decisiones operativas inmediatas, detectar fallas y mantener la operación fluida del parqueadero.

## Objetivo
El sistema debe monitorear y reportar el estado de cada talanquera en tiempo real, con actualización menor a 5 segundos. El estado debe incluir: posición física del brazo, estado de comunicación con el dispositivo, nivel de batería si aplica, última actividad registrada, y alertas activas.

## Comportamiento Específico
### Happy Path
1. Dispositivo IoT de la talanquera envía heartbeat cada 10 segundos a IoT-gateway
2. Heartbeat incluye: estado del relé, posición del brazo, voltaje batería, temperatura, timestamp
3. IoT-gateway procesa heartbeat y actualiza estado en memoria local
4. IoT-gateway envía actualización de estado a parking-service via MQTT o HTTP POST
5. Parking-service actualiza base de datos con estado actual de la talanquera
6. Parking-service emite evento por websocket a todos los clientes conectados (dashboard)
7. Dashboard recibe evento y actualiza interfaz visual para el operador
8. Si el estado recibido indica "error" o "offline", se genera alerta inmediata

### Estados de Talanquera
| Estado | Descripción |
|--------|-------------|
| CLOSED | Brazo abajo, talanquera en posición de cierre, lista para funcionar |
| OPEN | Brazo arriba, vehículo puede pasar |
| OPENING | Brazo en movimiento hacia arriba |
| CLOSING | Brazo en movimiento hacia abajo |
| ERROR | Dispositivo reporta error interno o falla de hardware |
| OFFLINE | Dispositivo no responde a heartbeats (>30s sin comunicación) |
| BLOCKED | Talanquera bloqueada por protocolo de seguridad (ej: falla detectada) |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Dispositivo no envía heartbeat por 30s | Sistema marca como OFFLINE, genera alerta, reintenta conexión cada 10s |
| Dispositivo envía estado contradictorio (brazo arriba pero relé cerrado) | Se registra anomalía en log, se muestra advertencia en dashboard |
| Múltiples dispositivos de la misma sede offline simultáneamente | Se genera alerta crítica de "Falla de comunicación masiva" |
| Falla de base de datos al actualizar estado | IoT-gateway mantiene estado en caché y reintenta; no bloquea dispositivo |

## Datos de Entrada (Heartbeat del dispositivo)
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| device_id | UUID | Identificador único del dispositivo IoT | Sí |
| gate_id | UUID | Identificador lógico de la talanquera | Sí |
| relay_state | BOOLEAN | Estado del relé (true = energizado/abierto) | Sí |
| arm_position | VARCHAR | Posición física: up, down, moving | Sí |
| battery_voltage | DECIMAL | Voltaje de batería (si aplica) | No |
| signal_strength | INTEGER | Intensidad de señal RSSI | No |
| temperature | DECIMAL | Temperatura del dispositivo (°C) | No |
| timestamp | TIMESTAMP | Timestamp del dispositivo | Sí |
| error_code | VARCHAR | Código de error si hay falla | No |

## Datos de Salida (API de estado)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| gate_id | UUID | Identificador de la talanquera |
| gate_name | VARCHAR | Nombre descriptivo (ej: "Salida Principal Norte") |
| sede_id | UUID | Identificador de la sede |
| current_status | VARCHAR | Estado actual |
| last_heartbeat | TIMESTAMP | Timestamp del último heartbeat recibido |
| last_command_timestamp | TIMESTAMP | Timestamp del último comando enviado |
| last_command_type | VARCHAR | Tipo del último comando (OPEN, CLOSE, MANUAL_OPEN) |
| error_description | VARCHAR | Descripción del error actual (si aplica) |
| uptime_hours | INTEGER | Horas de operación continua sin reiniciar |
| battery_level | INTEGER | Porcentaje de batería (si aplica) |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Estado de talanquera se actualiza en el dashboard en < 5 segundos desde que el dispositivo reporta cambio
2. El sistema detecta y marca como OFFLINE cualquier dispositivo sin heartbeat por > 30 segundos
3. El dashboard muestra todos los estados posibles: CLOSED, OPEN, OPENING, CLOSING, ERROR, OFFLINE, BLOCKED
4. Cada cambio de estado genera un evento en el log de auditoría
5. El operador recibe notificación push/email/SMS ante estado ERROR u OFFLINE

## Endpoints
- `GET /api/v1/gates/status` — Lista todos los estados de talanqueras de una sede
- `GET /api/v1/gate/status/{gate_id}` — Estado de una talanquera específica
- `GET /api/v1/gate/history/{gate_id}` — Historial de estados (últimas 24h)
- `WebSocket /ws/gates` — Canal de actualizaciones en tiempo real
- `POST /api/v1/devices/heartbeat` — Endpoint para recibir heartbeats de dispositivos IoT

## Health Check
- `GET /health` → `{ "status": "ok", "service": "iot-gateway" }`

## Notas
- Se recomienda usar MQTT para comunicación dispositivo-gateway por eficiencia de recursos.
- BLOCKED es un estado de seguridad que impide cualquier comando de apertura hasta que un admin lo limpie manualmente.
- Dashboard debe mostrar una representación visual (icono/color) por cada talanquera para facilitar monitoreo rápido.