# SPEC-11-app-operador-134 — El operador debe poder buscar un ticket abierto por placa o número de ticket,...

## Metadata
- **RF origen**: RF-134
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** registrar la salida de un vehículo manualmente y ver el cálculo del valor a pagar **para** cobrar correctamente al conductor en operaciones donde el vehículo no tiene ticket automático o hay discrepancia. ---

## Objetivo
El operador debe poder buscar un ticket abierto por placa o número de ticket, y al registrar la salida, el sistema debe calcular automáticamente el valor a pagar mostrando un resumen detallado: tiempo de permanencia, tarifas aplicadas, descuentos, y total a pagar. El operador puede confirmar la salida o cancelar si hay algún problema. ---

## Comportamiento Específico

### Happy Path
1. El operador toca "Registrar Salida" en el dashboard o menú. 2. El operador busca el ticket por: - Escanear código QR del ticket. - Escribir la placa. - Escribir el número de ticket. 3. El sistema muestra los datos del ticket encontrado: placa, hora de entrada, zona, espacio. 4. El operador confirma que es el vehículo correcto y toca "Calcular". 5. El sistema calcula el monto a pagar: - Tiempo transcurrido (entrada → ahora). - Tarifa de la zona según tabla de tarifas. - Aplicar fracciones (ej: cada 15 minutos). - Descuentos o promociones si aplica. - Monto mínimo si aplica. 6. Se muestra el resumen al operador: - Placa y número de ticket. - Hora de entrada y hora actual. - Duración: X horas Y minutos. - Tarifa aplicada: $X/hora. - Subtotal, descuentos, total. - **Total a pagar: $MMM** 7. El operador muestra este total al conductor. 8. El operador toca "Confirmar Salida" para proceder al pago (RF-135), o "Cancelar" para abortar. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | UUID | Identificador del ticket | | numero_ticket | String | Número legible del ticket | | placa | String | Placa del vehículo | | fecha_hora_entrada | DateTime | Timestamp de entrada | | fecha_hora_salida | DateTime | Timestamp de salida (now, editable) | | duracion_minutos | Integer | Tiempo total en minutos | | zona_nombre | String | Nombre de la zona | | espacio_numero | String | Número del espacio | | tarifa_nombre | String | Nombre de la tarifa aplicada | | tarifa_monto | Decimal | Monto de la tarifa por hora | | subtotal | Decimal | Monto antes de descuentos | | descuentos | Decimal | Monto descontado | | total_pagar | Decimal | Monto final a pagar | | estado_ticket | Enum | ABIERTO (pendiente de pago) | | puede_cerrar | Boolean | Si el ticket puede ser cerrado | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | UUID | Identificador del ticket | | numero_ticket | String | Número legible del ticket | | placa | String | Placa del vehículo | | fecha_hora_entrada | DateTime | Timestamp de entrada | | fecha_hora_salida | DateTime | Timestamp de salida (now, editable) | | duracion_minutos | Integer | Tiempo total en minutos | | zona_nombre | String | Nombre de la zona | | espacio_numero | String | Número del espacio | | tarifa_nombre | String | Nombre de la tarifa aplicada | | tarifa_monto | Decimal | Monto de la tarifa por hora | | subtotal | Decimal | Monto antes de descuentos | | descuentos | Decimal | Monto descontado | | total_pagar | Decimal | Monto final a pagar | | estado_ticket | Enum | ABIERTO (pendiente de pago) | | puede_cerrar | Boolean | Si el ticket puede ser cerrado | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La búsqueda de ticket devuelve resultados en < 2 segundos. 2. El cálculo de tarifas se realiza correctamente según la tabla de tarifas de la sede. 3. El resumen muestra claramente el total a pagar al conductor. 4. El ticket queda en estado ABIERTO pero con obligación de pago hasta que se cierre. 5. El espacio se marca como disponible solo al confirmar el cierre. 6. Si el operador cancela, ningún registro se modifica. 7. El registro de salida manual tiene marca "MANUAL" en el log. 8. El operador puede editar la fecha/hora de salida antes de confirmar si hubo un error. ---

## Endpoints
- `GET /api/v1/operator/tickets/search?placa={placa}` — Buscar ticket por placa - `GET /api/v1/operator/tickets/{id}` — Detalle del ticket - `POST /api/v1/operator/tickets/{id}/calculate-exit` — Calcular monto a pagar - `POST /api/v1/operator/tickets/{id}/exit` — Confirmar salida ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El operador NO cierra el ticket en este paso; aquí solo se registra la salida y se calcula el monto. El cierre definitivo ocurre tras el registro del pago (RF-135). - Si el vehículo tiene un bloqueo activo, se debe mostrar alerta al operador antes de permitir la salida. - La pantalla de resumen debe permitir al operador tocar "Imprimir ticket" para generar una versión impresa del resumen de salida.
