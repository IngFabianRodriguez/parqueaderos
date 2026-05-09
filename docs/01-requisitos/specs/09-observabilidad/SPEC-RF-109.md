# SPEC-09-observabilidad-109 — El sistema debe recibir un heartbeat de cada talanquera y ANPR cada 60 segundos

## Metadata
- **RF origen**: RF-109
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sistema de monitoreo **quiero** recibir heartbeats periódicos de cada talanquera y cámara ANPR **para** detectar oportunamente cuando un dispositivo queda offline y evitar operaciones inconscientes. ---

## Objetivo
El sistema debe recibir un heartbeat de cada talanquera y ANPR cada 60 segundos. Si un heartbeat no llega dentro de ese intervalo, el dispositivo se marca como `offline` automáticamente y se genera una alerta para el tenant_admin. ---

## Comportamiento Específico

### Happy Path
1. El dispositivo (talanquera o ANPR) envía un heartbeat `POST /heartbeat` con `device_id`, `device_type`, `timestamp` y `status` 2. El servicio `device-monitor` recibe el heartbeat y actualiza el campo `last_heartbeat_at` del dispositivo en la base de datos 3. El sistema verifica que el heartbeat llegó dentro de la ventana de 60 segundos 4. Si el heartbeat es válido, el dispositivo se mantiene `online` 5. Un job programado (cron) ejecuta cada 60 segundos para verificar dispositivos que no enviaron heartbeat 6. Si un dispositivo no recibe heartbeat en 2 ciclos (120 segundos), se marca como `offline` 7. Se genera automáticamente una alerta de tipo `device_offline` ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | device_id | UUID | Identificador del dispositivo | | status | enum | Estado actualizado: `online` / `offline` | | last_heartbeat_at | timestamp | Fecha/hora del último heartbeat recibido | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | device_id | UUID | Identificador del dispositivo | | status | enum | Estado actualizado: `online` / `offline` | | last_heartbeat_at | timestamp | Fecha/hora del último heartbeat recibido | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todo dispositivo registrado envía un heartbeat al menos cada 60 segundos 2. Un dispositivo se marca como `offline` si no se recibe heartbeat en 120 segundos (2 ciclos) 3. La alerta `device_offline` se genera automáticamente al marcar un dispositivo offline 4. El estado `offline` se refleja en el dashboard de salud del módulo de Observabilidad 5. El campo `last_heartbeat_at` se actualiza en la base de datos para cada heartbeat exitoso ---

## Endpoints
- `POST /api/v1/devices/heartbeat` — Recibe heartbeat de talanquera o ANPR - `GET /api/v1/devices/{device_id}/status` — Consulta estado actual de un dispositivo ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se usa un scheduler basada en cron (cada 60s) para recorrer todos los dispositivos pendientes de heartbeat - Los heartbeats se procesan de forma asíncrona para no bloquear la respuesta del dispositivo - El umbral de 60s es configurable por tenant_admin en la configuración de alertas del módulo de observabilidad
