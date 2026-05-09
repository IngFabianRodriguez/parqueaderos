# SPEC-11-app-operador-135 — Después de calcular el valor a pagar (RF-134), el operador registra el pago d...

## Metadata
- **RF origen**: RF-135
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** registrar el pago de un vehículo (efectivo o transferencia) desde la app **para** cerrar el ticket y liberar el espacio sin necesidad de un sistema POS externo. ---

## Objetivo
Después de calcular el valor a pagar (RF-134), el operador registra el pago directamente desde la app móvil. El sistema acepta efectivo (con cálculo de cambio si aplica) y transferencia (con registro del método). Una vez confirmado el pago, el ticket se cierra y el espacio se libera. ---

## Comportamiento Específico

### Happy Path
1. Desde la pantalla de resumen de salida (RF-134), el operador toca "Registrar Pago". 2. El operador selecciona el método de pago: - **Efectivo**: ingresa el monto recibido; el sistema calcula el cambio. - **Transferencia**: registra el número de referencia de la transferencia. 3. El operador confirma los datos del pago. 4. El operador toca "Confirmar Pago". 5. El sistema valida: - El monto recibido >= total a pagar (efectivo). - La referencia de transferencia no esté duplicada en las últimas 2 horas. 6. El sistema registra el pago y actualiza el ticket a CERRADO. 7. El espacio se marca como disponible. 8. Se muestra confirmación con: ticket cerrado, monto pagado, método, número de comprobante. 9. Opcionalmente, el operador puede imprimir o enviar el comprobante por WhatsApp/email. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | pago_id | UUID | Identificador del pago | | ticket_id | UUID | Identificador del ticket | | numero_comprobante | String | Número de comprobante (ej: "PAG-2024-00847") | | monto_pagado | Decimal | Monto total pagado | | monto_cambio | Decimal | Cambio devuelto (0 si no aplica) | | metodo_pago | Enum | Método utilizado | | referencia | String | Referencia del pago | | fecha_hora | DateTime | Timestamp del pago | | ticket_estado | Enum | CERRADO | | espacio_liberado | Boolean | Si el espacio fue liberado | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | pago_id | UUID | Identificador del pago | | ticket_id | UUID | Identificador del ticket | | numero_comprobante | String | Número de comprobante (ej: "PAG-2024-00847") | | monto_pagado | Decimal | Monto total pagado | | monto_cambio | Decimal | Cambio devuelto (0 si no aplica) | | metodo_pago | Enum | Método utilizado | | referencia | String | Referencia del pago | | fecha_hora | DateTime | Timestamp del pago | | ticket_estado | Enum | CERRADO | | espacio_liberado | Boolean | Si el espacio fue liberado | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El operador puede registrar un pago en menos de 10 segundos. 2. El sistema calcula correctamente el cambio para pagos en efectivo. 3. El ticket pasa a estado CERRADO inmediatamente tras la confirmación. 4. El espacio se libera al mismo tiempo que el cierre del ticket. 5. No se permite registrar un pago sobre un ticket ya cerrado. 6. El comprobante contiene: número de ticket, placa, hora entrada/salida, monto, método, operador. 7. La referencia de transferencia se valida contra duplicados en las últimas 2 horas. 8. Los ingresos del día se actualizan en el dashboard tras el pago. ---

## Endpoints
- `POST /api/v1/operator/payments` — Registrar un pago - `GET /api/v1/operator/payments/{id}/receipt` — Generar comprobante - `GET /api/v1/operator/tickets/{id}` — Verificar estado del ticket ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Para pagos en efectivo, siempre se debe mostrar el cálculo de cambio al operador antes de confirmar. - El comprobante debe poder enviarse por WhatsApp con un botón directo. - Si la sede requiere imprimmir ticket en cada salida, se envía a una impresora Bluetooth conectada.
