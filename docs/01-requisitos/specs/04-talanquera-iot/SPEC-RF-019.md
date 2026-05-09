# SPEC-04-019 — Apertura manual de talanquera por operador en emergencia

## Metadata
- **RF origen**: RF-019
- **Módulo**: 04-talanquera-iot
- **Prioridad**: Alta
- **Servicios**: iot-gateway, parking-service, audit-log

---

## User Story
Como Operador de parqueadero **quiero** poder abrir manualmente la talanquera en situaciones de emergencia (falla del sistema, vehículo con problemas técnicos, falla de pago, etc.) **para** resolver situaciones excepcionales rápidamente sin bloquear la salida de vehículos.

## Objetivo
El sistema debe permitir que un operador con rol apropiado (admin_sede, operador) ejecute una apertura manual de la talanquera en cualquier momento, independientemente del estado de pago. Esta apertura debe estar protegida por autenticación, debe registrar el motivo obligatorio, y debe generar trazabilidad completa en el log de auditoría.

## Comportamiento Específico
### Happy Path
1. Operador identifica situación que requiere apertura manual
2. Operador ingresa al panel de control de talanqueras
3. Sistema solicita autenticación del operador (si no hay sesión activa)
4. Operador identifica la talanquera a abrir (entrada o salida, por sede)
5. Operador selecciona opción "Apertura Manual de Emergencia"
6. Sistema presenta formulario con campos obligatorios: Motivo, Placa (si aplica), Confirmación
7. Operador llena el formulario y confirma la acción
8. Sistema valida que el operador tiene rol con permisos de apertura manual
9. Sistema registra la solicitud en log de auditoría antes de ejecutar
10. Sistema envía comando `MANUAL_OPEN` a IoT-gateway
11. Dispositivo de talanquera ejecuta apertura física
12. Sistema actualiza log de auditoría con resultado y timestamp de ejecución

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Operador sin rol adecuado intenta apertura manual | Se rechaza acción, mensaje "No tiene permisos para apertura manual" |
| Dispositivo IoT no responde al comando | Se muestra error "Talanquera no responde", se genera alerta RF-022 |
| Se intenta abrir una talanquera que ya está abierta | Se muestra mensaje "La talanquera ya está abierta" y no se reenvía comando |
| Múltiples operadores intentan abrir la misma talanquera simultáneamente | Se procesa la primera solicitud válida, las demás reciben mensaje de "Operación en curso" |
| Apertura manual durante falla de red | IoT-gateway opera en modo offline y registra la acción para sincronización posterior |
| Placa no existe en el sistema y operador la proporciona | Se crea registro de salida improvisado con placa proporcionada para trazabilidad |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| gate_id | UUID | Identificador de la talanquera a abrir | Sí |
| operador_id | UUID | ID del operador que ejecuta la acción | Sí (autenticado) |
| sede_id | UUID | Identificador de la sede | Sí |
| motivo_codigo | VARCHAR(50) | Código predefinido del motivo | Sí |
| motivo_descripcion | TEXT | Descripción adicional del motivo | Sí |
| placa_vehiculo | VARCHAR(20) | Placa del vehículo implicado (si aplica) | No |
| confirmacion_operador | BOOLEAN | Operador confirma que la acción queda registrada | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| command_id | UUID | Identificador del comando ejecutado |
| gate_status | VARCHAR | Estado resultante: opened, error, timeout |
| timestamp_apertura | TIMESTAMP | Momento de apertura efectiva |
| timestamp_cierre_programado | TIMESTAMP | Momento en que se cerrará automáticamente |
| auditoria_id | UUID | Referencia al registro en log de auditoría |
| mensaje_error | VARCHAR | Descripción de error si falla |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Solo operadores con rol admin_sede, operador o superior pueden ejecutar apertura manual
2. El campo "motivo" es obligatorio y no puede ser vacío
3. Toda apertura manual queda registrada en log de auditoría con operador, timestamp, motivo y resultado
4. La apertura manual se completa en < 2 segundos si el dispositivo responde
5. El sistema genera alerta cuando más de 3 aperturas manuales ocurren en la misma sede en 1 hora
6. Si el dispositivo no responde, el operador recibe mensaje de error claro

## Endpoints
- `POST /api/v1/gate/manual-open` — Ejecuta apertura manual con autenticación
- `POST /api/v1/gate/open` — Comando de apertura (usado por ambos flujos)
- `GET /api/v1/gate/status/{gate_id}` — Consulta estado de talanquera (RF-020)
- `GET /api/v1/audit/logs?filter=manual_open` — Consulta de logs de aperturas manuales

## Health Check
- `GET /health` → `{ "status": "ok", "service": "iot-gateway" }`

## Notas
- Motivos predefinidos: FALLA_SISTEMA, FALLA_PAGO, VEHICULO_VARADO, EMERGENCIA_MEDICA, OPERADOR_ERROR, OTRO.
- La apertura manual es un mecanismo de contingencia y no debe ser la vía normal de salida.
- Se recomienda limitar la cantidad de aperturas manuales por operador para prevenir abusos.
- La apertura manual debe poder ejecutarse incluso si el billing-service está caído (fallback).