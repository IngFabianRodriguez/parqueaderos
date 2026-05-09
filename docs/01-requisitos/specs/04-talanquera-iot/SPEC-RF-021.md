# SPEC-04-021 — Registro de comando enviado a la talanquera

## Metadata
- **RF origen**: RF-021
- **Módulo**: 04-talanquera-iot
- **Prioridad**: Alta
- **Servicios**: iot-gateway, parking-service, audit-service

---

## User Story
Como Administrador de sede, Auditor de cumplimiento, Superadmin **quiero** que todo comando enviado a cualquier talanquera quede registrado de forma inmutable **para** poder auditar quién abrió cada talanquera, en qué momento, con qué motivo, y con qué resultado.

## Objetivo
Cada vez que el sistema envía un comando a una talanquera (OPEN, CLOSE, MANUAL_OPEN, RESET), debe crear un registro en la tabla `comando_talanquera` con todos los detalles del comando. Estos registros son inmutables (no se pueden modificar ni eliminar) y constituyen la base de la auditoría operativa.

## Comportamiento Específico
### Happy Path
1. Un actor (sistema u operador) solicita un comando de talanquera (apertura, cierre, reset)
2. Parking-service o el endpoint de API recibe la solicitud
3. Sistema crea registro PRELIMINAR en tabla `comando_talanquera` con: comando_id, tipo_comando, gate_id, sede_id, originator_type, originator_id, originator_ip, timestamp_solicitud, motivo_id, motivo_descripcion, parametros_json, resultado (PENDING)
4. Una vez creado el registro, se envía el comando al IoT-gateway
5. IoT-gateway ejecuta el comando en el dispositivo físico
6. IoT-gateway reporta resultado (SUCCESS, FAILED, TIMEOUT) a parking-service
7. Parking-service actualiza el registro de comando con: timestamp_resultado, resultado, error_description, device_response_time_ms
8. Si el comando fue MANUAL_OPEN, se crea registro adicional en log_auditoria

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Comando se envía pero dispositivo no responde (timeout 3s) | Registro se actualiza con resultado TIMEOUT, se genera alerta RF-022 |
| Comando genera error en el dispositivo | Registro se actualiza con resultado FAILED y error_description |
| Registro no se puede crear por falla de BD | Sistema no envía comando (fail-safe), retorna error al originador |
| Intento de modificar o eliminar registro de comando | Operación rechazada — logs son inmutables |
| Comando duplicado enviado (retry por timeout) | Se detecta duplicado por comando_id, se ignora segundo envío |
| Comando MANUAL_OPEN sin motivo | Se rechaza creación del registro hasta que motivo sea proporcionado |

## Datos de Entrada (Del comando)
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tipo_comando | VARCHAR(20) | OPEN, CLOSE, MANUAL_OPEN, RESET | Sí |
| gate_id | UUID | Identificador de la talanquera | Sí |
| sede_id | UUID | Identificador de la sede | Sí |
| originator_type | VARCHAR(20) | system, operator, admin, superadmin | Sí |
| originator_id | UUID | ID del usuario o "SYSTEM" | Sí |
| originator_ip | VARCHAR(45) | Dirección IP del solicitante | Sí |
| motivo_id | VARCHAR(50) | Código predefinido del motivo | Sí (para MANUAL_OPEN) |
| motivo_descripcion | TEXT | Descripción del motivo | No |
| entrada_id | UUID | Referencia a registro de entrada (si aplica) | No |
| salida_id | UUID | Referencia a registro de salida (si aplica) | No |
| timestamp_solicitud | TIMESTAMP | Momento en que se genera la solicitud | Sí |

## Datos de Salida (Del registro)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| comando_id | UUID | Identificador único del registro |
| tipo_comando | VARCHAR | Tipo de comando ejecutado |
| gate_id | UUID | Talanquera objetivo |
| sede_id | UUID | Sede donde se ejecuta |
| originator_type | VARCHAR | Tipo de originador |
| originator_id | VARCHAR | ID del originador |
| originator_ip | VARCHAR | IP del originador |
| motivo_codigo | VARCHAR | Código del motivo |
| motivo_descripcion | TEXT | Descripción del motivo |
| timestamp_solicitud | TIMESTAMP | Cuando se generó el comando |
| timestamp_envio | TIMESTAMP | Cuando se envió al IoT-gateway |
| timestamp_resultado | TIMESTAMP | Cuando se recibió respuesta del dispositivo |
| resultado | VARCHAR | PENDING, SUCCESS, FAILED, TIMEOUT |
| error_code | VARCHAR | Código de error (si falló) |
| error_description | TEXT | Descripción del error |
| device_response_time_ms | INTEGER | Tiempo de respuesta del dispositivo |
| timestamp_apertura_confirmada | TIMESTAMP | Cuando el sensor confirmó apertura física |
| timestamp_cierre_confirmada | TIMESTAMP | Cuando el sensor confirmó cierre físico |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo comando enviado a cualquier talanquera genera un registro en la tabla comando_talanquera
2. El registro se crea ANTES de enviar el comando al dispositivo (fail-safe)
3. Los registros son inmutables: no se puede UPDATE ni DELETE, solo INSERT nuevos registros
4. Cada registro contiene: comando_id, tipo, gate_id, sede_id, originator, IP, timestamp, motivo, resultado
5. Registros de apertura manual incluyen referencia al operador que autorizó

## Endpoints
- `POST /api/v1/gate/open` — Comando de apertura (genera registro)
- `POST /api/v1/gate/close` — Comando de cierre (genera registro)
- `POST /api/v1/gate/manual-open` — Apertura manual (genera registro + log_auditoria)
- `POST /api/v1/gate/reset` — Reset de talanquera en error (genera registro)
- `GET /api/v1/audit/gate-commands` — Consulta de comandos con filtros
- `GET /api/v1/gate/command/{command_id}` — Detalle de un comando específico

## Health Check
- `GET /health` → `{ "status": "ok", "service": "parking-service" }`

## Notas
- El patrón de registro antes de ejecutar (write-ahead log) asegura que nunca se pierde trazabilidad.
- Para compliance con regulaciones colombianas (SIC, DIAN), los logs deben mantenerse mínimo 5 años.
- Índices recomendados: gate_id, timestamp_solicitud, originator_id, tipo_comando.