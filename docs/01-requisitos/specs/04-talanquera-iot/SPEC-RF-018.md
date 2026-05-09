# SPEC-04-018 — Apertura de talanquera de salida con pago confirmado

## Metadata
- **RF origen**: RF-018
- **Módulo**: 04-talanquera-iot
- **Prioridad**: Alta
- **Servicios**: iot-gateway, parking-service, billing-service

---

## User Story
Como Sistema de Control de Talanquera IoT **quiero** abrir la talanquera de salida únicamente cuando el pago del vehículo esté confirmado **para** garantizar que no salga ningún vehículo sin pagar y evitar pérdidas económicas para el operador del parqueadero.

## Objetivo
El sistema debe enviar un comando de apertura a la talanquera de salida únicamente cuando la transacción de pago asociada al registro de salida tenga estado "confirmado" (pagado, exonerado o cubierto por prepago). Cualquier estado diferente (pendiente, fallido, en disputa) debe mantener la talanquera cerrada.

## Comportamiento Específico
### Happy Path
1. Sistema ANPR de salida reconoce la placa del vehículo (o ingreso manual por operador)
2. Parking-service busca el registro de entrada activo y genera cálculo de tarifa (RF-006)
3. Si hay saldo prepago suficiente, billing-service confirma pago directamente (wallet)
4. Si no hay wallet o saldo insuficiente, se presenta opción de pago
5. Usuario realiza el pago a través del medio elegido
6. Payment-gateway confirma la transacción y actualiza estado a "confirmado"
7. Parking-service valida que el estado de la transacción sea "pagado", "exonerado" o "prepago_aprobado"
8. Parking-service envía comando `OPEN_GATE` a IoT-gateway con entrada_id, salida_id, y motivo "pago_confirmado"
9. IoT-gateway valida que el comando proviene de parking-service autenticado
10. IoT-gateway envía señal de apertura al dispositivo
11. Dispositivo ejecuta apertura física
12. Transcurrido el tiempo de seguridad (configurable, default 5s), IoT-gateway envía comando `CLOSE_GATE`

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Pago en estado "pendiente" | Se rechaza apertura, se muestra mensaje "Espere confirmación de pago" |
| Pago en estado "fallido" | Se rechaza apertura, se muestra mensaje "Pago fallido — acercarse al punto de pago" |
| Pago en estado "reversado" | Se rechaza apertura, se bloquea salida |
| Placa no tiene registro de entrada (intento de fraude) | Se rechaza apertura, se genera alerta de seguridad, operador interviene |
| Saldo prepago mayor al valor (sobresaldo) | Se descuenta exacto, se abre talanquera, excedente permanece en wallet |
| Cliente con exoneración válida | Se confirma exonerado y se abre talanquera sin cobro |
| Pago confirmado pero dispositivo IoT no responde | Se genera alerta de falla (RF-022), operador puede realizar apertura manual (RF-019) |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| entrada_id | UUID | Identificador del registro de entrada | Sí |
| salida_id | UUID | Identificador del registro de salida | Sí |
| sede_id | UUID | Identificador de la sede | Sí |
| placa | VARCHAR(20) | Placa del vehículo | Sí |
| transaction_id | UUID | ID de la transacción de pago | Sí |
| estado_pago | VARCHAR(20) | Estado confirmado del pago | Sí |
| timestamp_solicitud | TIMESTAMP | Momento en que se solicita apertura | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| gate_command_id | UUID | Identificador del comando enviado |
| gate_status | VARCHAR | Estado de la talanquera: opened, closed, error, timeout |
| timestamp_apertura | TIMESTAMP | Momento exacto de apertura del brazo |
| timestamp_cierre | TIMESTAMP | Momento de cierre automático |
| mensaje_error | VARCHAR | Descripción de error si falla |
| duracion_apertura_ms | INTEGER | Tiempo que permaneció abierta en milisegundos |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. La talanquera de salida NO se abre si el estado de pago es diferente a "confirmado" (pagado/exonerado/prepago_aprobado)
2. Tiempo desde confirmación de pago hasta apertura de talanquera: < 1.5 segundos
3. Si la talanquera no responde al comando en 3 segundos, se genera alerta de falla (RF-022)
4. La talanquera se cierra automáticamente después del paso del vehículo (timer configurable)
5. Si el vehículo no pasa en 30 segundos (sensor de flujo no detecta paso), se cierra la talanquera y se genera alerta
6. El log de auditoría registra cada comando de apertura con timestamp, usuario, motivo y resultado

## Endpoints
- `POST /api/v1/salidas` — Registra salida del vehículo y genera cobro (RF-006)
- `POST /api/v1/pagos/confirmar` — Gateway de pago confirma transacción
- `POST /api/v1/gate/open` — IoT-gateway recibe comando de apertura
- `GET /api/v1/gate/status/{gate_id}` — Consulta estado actual de talanquera (RF-020)

## Health Check
- `GET /health` → `{ "status": "ok", "service": "iot-gateway" }`

## Notas
- Talanquera normally closed (fail-secure). Only opens with explicit command.
- No debe abrirse por simple presencia de vehículo — requiere flujo completo de pago.
- Comunicación entre parking-service e IoT-gateway debe ser sobre canal autenticado (JWT o mTLS).
- Circuit-breaker recomendado en el IoT-gateway para no enviar comandos a dispositivos que no responden.