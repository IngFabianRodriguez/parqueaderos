# SPEC-12-app-cliente-144 — El sistema debe enviar una notificación push al cliente cuando falten 15 minu...

## Metadata
- **RF origen**: RF-144
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** recibir un recordatorio cuando mi tiempo de parqueo pagado esté por vencer **para** evitar multas o recargos y poder renovar fácilmente desde la app. ---

## Objetivo
El sistema debe enviar una notificación push al cliente cuando falten 15 minutos para que venza su parqueo activo. La notificación debe incluir la opción de renovar directamente desde la notificación o desde la app sin necesidad de ir al punto de pago. ---

## Comportamiento Específico

### Happy Path
1. El sistema ejecuta un job de verificación cada 5 minutos que revisa parqueos activos con vencimiento en los siguientes 20 minutos. 2. Para cada parqueo que cumpla la condición y no haya sido notificado aún: a. Se evalúa si el cliente tiene notificaciones push habilitadas (RF-149). b. Se envía notificación push con: sede, vehículo, tiempo restante, botón "Renovar". 3. El cliente recibe la notificación en su dispositivo. 4. Si el cliente pulsa "Renovar" en la notificación: a. Se abre la app en la pantalla de renovación con los datos precargados. b. Se muestran opciones de duración (15 min, 30 min, 1h, 2h) con el costo asociado. c. El cliente selecciona la duración y confirma. d. El sistema cobra al método de pago default del cliente (o muestra selector si hay más de uno). e. Se confirma la renovación y se extiende el parqueo. 5. Si el cliente abre la app manualmente y va a "Mi Parqueo Activo": a. Ve el tiempo restante y el botón "Renovar" visible. b. El flujo de renovación es el mismo del paso 4. 6. Si el cliente no renueva y el parqueo vence: a. El sistema permite que el operador regulate la salida normalmente. b. Se genera la diferencia a pagar según las reglas del parqueadero. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | parqueo_id | UUID | Identificador actualizado del parqueo | | hora_fin_anterior | timestamp | Hora de fin anterior | | hora_fin_nueva | timestamp | Nueva hora de fin tras la renovación | | monto_cobrado | decimal | Monto cobrado por la renovación | | notificacion_id | UUID | ID de la notificación enviada | | estado | string | Estado actualizado del parqueo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | parqueo_id | UUID | Identificador actualizado del parqueo | | hora_fin_anterior | timestamp | Hora de fin anterior | | hora_fin_nueva | timestamp | Nueva hora de fin tras la renovación | | monto_cobrado | decimal | Monto cobrado por la renovación | | notificacion_id | UUID | ID de la notificación enviada | | estado | string | Estado actualizado del parqueo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente recibe una notificación push 15 minutos antes del vencimiento de su parqueo activo. 2. La notificación muestra: nombre de la sede, placa del vehículo, tiempo restante. 3. Desde la notificación, el cliente puede pulsar "Renovar" y ver opciones de duración con costos. 4. La renovación se completa en máximo 3 pasos (seleccionar duración → confirmar → receipt). 5. El cobro se realiza al método de pago default sin necesidad de volver a ingresar datos. 6. La nueva hora de fin se refleja inmediatamente en la app y en el sistema del parqueadero. 7. Se envía confirmación por push tras una renovación exitosa. 8. Si el cliente ignora la notificación y el parqueo vence, puede still renovar desde la app (mientras el vehículo esté aún dentro) pero se le cobra la diferencia desde el vencimiento. ---

## Endpoints
- `POST /api/v1/cliente/parqueos/{parqueo_id}/renovar` — Renovar parqueo activo - `GET /api/v1/cliente/parqueos/activos` — Obtener parqueo activo actual - `GET /api/v1/cliente/tarifas?sede_id=X` — Consultar tarifas para renovación - `POST /api/v1/notificaciones/push/enviar` — Enviar notificación push ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El job de notificación se ejecuta cada 5 minutos para no saturar el sistema. - La标记 "ya_notificado_vencimiento" en el parqueo evita notificaciones duplicadas. - Si el parqueo fue renovado recientemente (última hora), no se envía recordatorio aunque falten 15 min. - El límite de renovación desde la app es hasta 24h total (prepago + renovaciones acumuladas).
