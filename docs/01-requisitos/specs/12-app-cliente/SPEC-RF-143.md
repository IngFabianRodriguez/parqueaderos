# SPEC-12-app-cliente-143 — El sistema debe permitir al cliente realizar un prepago de parqueo desde la a...

## Metadata
- **RF origen**: RF-143
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** pagar el parqueo anticipadamente desde la app y seleccionar la duración **para** asegurar mi lugar y evitar colas en la entrada. ---

## Objetivo
El sistema debe permitir al cliente realizar un prepago de parqueo desde la app, seleccionando la sede, zona (opcional), vehículo y duración deseada. El cliente selecciona un método de pago guardado o ingresa uno nuevo, confirma el monto y recibe una confirmación con un código de validación. ---

## Comportamiento Específico

### Happy Path
1. El cliente selecciona la opción "Prepagar Parqueo" desde la app. 2. El sistema muestra las sedes disponibles ordenadas por cercanía. 3. El cliente selecciona una sede. 4. El sistema consulta la disponibilidad y muestra las zonas disponibles (RF-142). 5. El cliente selecciona una zona o deixa "cualquiera" (zona libre asignada en entrada). 6. El cliente selecciona uno de sus vehículos registrados o indica que llegará con otro. 7. El cliente selecciona la duración del prepago (15 min, 30 min, 1h, 2h, 4h, 8h, 12h, 24h, o custom). 8. El sistema calcula el monto total basado en la tarifa vigente de la sede/zona (RF-161) y lo muestra con desglose. 9. El cliente selecciona un método de pago de los guardados o añade uno nuevo. 10. El cliente confirma la transacción. 11. El sistema procesa el pago con la pasarela correspondiente. 12. En caso de éxito, se genera el código de validación y se muestra la confirmación. 13. El sistema envía notificación push de confirmación al cliente (RF-149). 14. El registro de disponibilidad se actualiza para reflejar la reserva. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | parqueo_id | UUID | Identificador del parqueo/reserva | | codigo_validacion | string | Código QR o alfanumérico para presentar en entrada | | monto_cobrado | decimal | Monto finalmente cobrado | | sede_nombre | string | Nombre de la sede | | zona_nombre | string | Zona asignada (si se seleccionó específica) | | vehiculo_placa | string | Placa del vehículo | | hora_inicio | timestamp | Hora de inicio efectiva (cuando pase entrada) | | hora_fin_estimada | timestamp | Hora de fin estimada según prepago | | estado | string | Estado: "reservado_pendiente" | | url_qr | string | URL de la imagen QR para validar | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | parqueo_id | UUID | Identificador del parqueo/reserva | | codigo_validacion | string | Código QR o alfanumérico para presentar en entrada | | monto_cobrado | decimal | Monto finalmente cobrado | | sede_nombre | string | Nombre de la sede | | zona_nombre | string | Zona asignada (si se seleccionó específica) | | vehiculo_placa | string | Placa del vehículo | | hora_inicio | timestamp | Hora de inicio efectiva (cuando pase entrada) | | hora_fin_estimada | timestamp | Hora de fin estimada según prepago | | estado | string | Estado: "reservado_pendiente" | | url_qr | string | URL de la imagen QR para validar | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede seleccionar sede, zona, vehículo y duración. 2. El sistema muestra el cálculo de monto en tiempo real antes de confirmar. 3. El cliente puede usar un método de pago guardado o añadir uno nuevo. 4. Al confirmar, se procesa el pago y se muestra un código QR de validación. 5. El espacio对应的 se descuenta de la disponibilidad en tiempo real. 6. La transacción queda registrada en el historial del cliente (RF-147). 7. Si el pago falla, ningún espacio es bloqueado y el cliente puede reintentar. 8. El prepago puede cancelarse desde la app antes de que el vehículo pase la entrada (con reembolso total si no ha habido check-in). ---

## Endpoints
- `POST /api/v1/cliente/parqueos/prepago` — Crea una reserva de prepago - `POST /api/v1/cliente/pagos/procesar` — Procesa el pago con la pasarela - `GET /api/v1/cliente/metodos-pago` — Lista métodos de pago del cliente - `GET /api/v1/cliente/tarifas?sede_id=X` — Consulta tarifas vigentes ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El prepago tiene validez desde el momento de la compra hasta la hora de fin estimada; al pasar la entrada, el tiempo comienza a correr realmente. - Si el cliente no usa el prepago en 24 horas, se reembolsa automáticamente. - Las tarifas de prepago pueden incluir un pequeño descuento vs pago en sitio (para incentivar uso). - El código QR debe actualizarse dinámicamente (código rotativo) para evitar fraude por captura de pantalla.
