# SPEC-04-022 — Detección de falla de talanquera y generación de alerta inmediata

## Metadata
- **RF origen**: RF-022
- **Módulo**: 04-talanquera-iot
- **Prioridad**: Alta
- **Servicios**: iot-gateway, parking-service, notification-service, alert-service

---

## User Story
Como Operador de control, Administrador de sede, Soporte técnico **quiero** recibir alertas inmediatas cuando una talanquera no responde al comando de apertura en el tiempo esperado (3 segundos) **para** poder actuar rápidamente, despejar la salida, contactar soporte técnico y evitar que vehículos queden bloqueados en el parqueadero.

## Objetivo
El sistema debe monitorear cada comando enviado a una talanquera. Si el dispositivo no confirma la apertura en 3 segundos, el sistema debe: (1) marcar la talanquera como estado ERROR o BLOCKED, (2) generar una alerta inmediata, (3) notificar al operador de turno y al administrador de sede.

## Comportamiento Específico
### Happy Path (Detección de timeout)
1. Parking-service o IoT-gateway envía comando OPEN a la talanquera
2. IoT-gateway inicia timer de 3 segundos esperando respuesta del dispositivo
3. Si dispositivo responde dentro de 3s → timer se cancela, flujo normal continúa
4. Si timer expira (3s) sin respuesta del dispositivo:
   a. IoT-gateway marca comando como TIMEOUT
   b. IoT-gateway reporta timeout a parking-service
   c. Parking-service actualiza estado de talanquera a ERROR
   d. Alert-service crea alerta con severidad ALTA
   e. Alert-service determina destinatarios según reglas de notificación
   f. Notification-service envía push al operador de turno (dashboard + app móvil)
   g. Notification-service envía email/SMS a admin de sede
   h. Si falla persiste > 5 minutos, se escala a soporte técnico (nivel 2)
5. Operador recibe alerta y puede intentar apertura manual (RF-019) como fallback

### Tipos de Falla Detectados
| Tipo de Falla | Descripción | Detección |
|---------------|-------------|-----------|
| TIMEOUT_APERTURA | Talanquera no responde al comando OPEN en 3s | Timer expira |
| TIMEOUT_CIERRE | Talanquera no confirma cierre después de timer de cierre | Timer expira |
| SENSOR_FALLA | Sensor de posición reporta valor inválido | Estado contradictorio |
| COMUNICACION_PERDIDA | No heartbeats por > 30s | Heartbeat missing |
| ERROR_INTERNO | Dispositivo reporta error_code | Campo error_code presente |
| BLOQUEO_MECANICO | Brazo no completa movimiento (detenido a mitad) | Timeout + posición incompleta |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Falla persiste > 30 minutos sin resolución | Se genera alerta CRITICAL escalated a soporte nivel 3 (gerencia) |
| Múltiples talanqueras fallan simultáneamente | Se genera alerta de "Falla masiva" y se considera caída de red/dispositivo |
| Dispositivo se recupera solo antes de que operador atienda | Sistema marca como AUTO_RESOLVED, alerta se cierra |
| Falla en talanquera de ENTRADA (no permite entrar) | Se genera alerta de disponibilidad (mayor urgencia) — afecta capacidad |
| Operador intenta apertura manual durante falla | Se permite (RF-019), pero alerta se mantiene hasta que dispositivo confirme funcionamiento |

## Datos de Entrada (De la Alerta Generada)
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| alert_id | UUID | Identificador único de la alerta | Sí |
| gate_id | UUID | Talanquera con falla | Sí |
| sede_id | UUID | Sede de la talanquera | Sí |
| tipo_falla | VARCHAR | Código del tipo de falla | Sí |
| comando_id | UUID | Referencia al comando que falló | Sí |
| timestamp_falla | TIMESTAMP | Momento de detección | Sí |
| severity | VARCHAR | CRITICAL, HIGH, MEDIUM | Sí |
| device_status | VARCHAR | Estado actual del dispositivo | Sí |
| intentos_anteriores | INTEGER | Número de comandos fallidos consecutivos | No |

## Datos de Salida (Del registro de alerta)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| alert_id | UUID | — |
| gate_id | UUID | — |
| gate_name | VARCHAR | Nombre descriptivo de la talanquera |
| sede_name | VARCHAR | Nombre de la sede |
| tipo_falla | VARCHAR | Código legible de falla |
| descripcion | TEXT | Descripción detallada de la falla |
| timestamp_inicio | TIMESTAMP | Momento en que ocurrió la falla |
| timestamp_resolucion | TIMESTAMP | Momento en que se resolvió (null si no resuelta) |
| duracion_minutos | INTEGER | Tiempo que duró la falla |
| estado | VARCHAR | ACTIVA, RESUELTA, ESCALADA |
| resolucion_por | VARCHAR | operador_id, soporte_id, o "AUTO_RESOLVED" |
| nota_resolucion | TEXT | Nota del operador o soporte sobre cómo se resolvió |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Si la talanquera no responde al comando OPEN en 3 segundos, se genera alerta en < 5 segundos
2. Alerta se muestra en el dashboard del operador de turno inmediatamente
3. Admin de sede recibe notificación por email/SMS/push en < 30 segundos de generada la alerta
4. La talanquera en falla se marca como BLOCKED — no acepta comandos automáticos hasta que se limpie
5. El operador puede limpiar la alerta solo si la talanquera funciona (prueba de apertura manual exitosa)
6. Si hay más de 2 fallas en la misma talanquera en 24 horas, se genera alerta de mantenimiento preventivo

## Endpoints
- `POST /api/v1/alerts` — Crear alerta (interno, llamado por parking-service)
- `GET /api/v1/alerts/active` — Listar alertas activas
- `PUT /api/v1/alerts/{alert_id}/resolve` — Marcar alerta como resuelta
- `POST /api/v1/gate/manual-open` — Operador ejecuta apertura manual como fallback
- `GET /api/v1/gate/status/{gate_id}` — Ver estado de talanquera

## Health Check
- `GET /health` → `{ "status": "ok", "service": "alert-service" }`

## Notas
- Timeout de 3 segundos es configurable por sede/dispositivo. Valor mínimo: 2s, máximo: 10s.
- Se recomienda implementar "retry inteligente": reintentar comando 1 vez antes de declarar falla, siempre que el dispositivo esté en estado online.
- BLOCKED es estado de seguridad: ningún comando automático puede ejecutarse en talanquera bloqueada. Solo un operador puede limpiar el estado (después de verificar que funciona).
- MTTR (Mean Time To Resolve): meta < 10 minutos.