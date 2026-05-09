# SPEC-09-observabilidad-110 — El sistema debe trackear la latencia comando-respuesta de cada talanquera: el...

## Metadata
- **RF origen**: RF-110
- **Módulo**: 09-observabilidad
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** sistema de monitoreo **quiero** medir el tiempo entre enviar un comando de apertura a una talanquera y recibir la confirmación de que se abrió **para** detectar dispositivos con latencia anormal que puedan indicar fallas o congestión de red. ---

## Objetivo
El sistema debe trackear la latencia comando-respuesta de cada talanquera: el tiempo transcurrido desde que se envía el comando "abrir" hasta que la talanquera confirma "abierta". Si la latencia excede 3 segundos, se debe generar una alerta de tipo `latency_warning`. ---

## Comportamiento Específico

### Happy Path
1. El operador o sistema envía comando `POST /api/v1/talanqueras/{id}/abrir` 2. El servicio `talanquera-service` registra en la base de datos el timestamp de envío del comando (`command_sent_at`) 3. La talanquera recibe el comando y ejecuta la apertura 4. La talanquera envía confirmación `POST /api/v1/talanqueras/{id}/confirm` con `command_id` y `status=opened` 5. El servicio `device-monitor` recibe la confirmación, calcula la latencia: `confirm_received_at - command_sent_at` 6. Si latencia ≤ 3s: se registra en tabla `command_latencies` sin alerta 7. Si 3s < latencia ≤ 10s: se genera alerta `latency_warning` con nivel "warning" 8. Si latencia > 10s: se genera alerta `command_timeout` con nivel "critical" 9. El dashboard de latencias muestra en tiempo real el promedio de los últimos 5 comandos por talanquera ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | talanquera_id | UUID | Identificador de la talanquera | | latency_ms | integer | Latencia en milisegundos | | latency_category | enum | `normal` (≤3s), `warning` (3-10s), `critical` (>10s) | | alert_triggered | boolean | Si se generó alerta | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | talanquera_id | UUID | Identificador de la talanquera | | latency_ms | integer | Latencia en milisegundos | | latency_category | enum | `normal` (≤3s), `warning` (3-10s), `critical` (>10s) | | alert_triggered | boolean | Si se generó alerta | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La latencia comando-respuesta se calcula con precisión de milisegundos 2. Toda latencia > 3s genera una alerta `latency_warning` 3. Toda latencia > 10s genera una alerta `command_timeout` 4. El dashboard muestra el promedio de latencia de los últimos 5 comandos por talanquera 5. Las alertas se notifican según la configuración de canales del tenant_admin (RF-107) 6. Los datos de latencia se retienen por 30 días para análisis histórico ---

## Endpoints
- `POST /api/v1/talanqueras/{id}/abrir` — Envía comando de apertura - `POST /api/v1/talanqueras/{id}/confirm` — Recibe confirmación de la talanquera - `GET /api/v1/talanqueras/{id}/latency` — Consulta historial de latencias de una talanquera ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El umbral de 3 segundos es configurable por el tenant_admin a través del módulo de alertas (RF-106) - Se usa una ventana móvil de los últimos 5 comandos para calcular el promedio y detectar tendencias - El campo `latency_avg` en la tabla `devices` permite al admin ver rápidamente si una talanquera tiene problemas recurrentes - Este requerimiento complementa RF-111 (alerta por talanquera sin responder 2 min) — aquí se mide la latencia de comandos exitoso, mientras RF-111 detecta dispositivos completamente sin respuesta
