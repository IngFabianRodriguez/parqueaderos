# SPEC-11-app-operador-133 — El operador debe poder crear un ticket de entrada manualmente desde la app mó...

## Metadata
- **RF origen**: RF-133
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador de parqueadero **quiero** registrar la entrada de un vehículo manualmente **para** atender vehículos sin placa, con placa no leída por la cámara, o situaciones especiales donde el registro automático no aplica. ---

## Objetivo
El operador debe poder crear un ticket de entrada manualmente desde la app móvil, ingresando la placa del vehículo (manualmente o seleccionando de una lista de placas frecuentes), fecha y hora de entrada, y una observación opcional. El sistema genera el ticket y, si hay una talanquera de entrada asociada, la abre automáticamente. ---

## Comportamiento Específico

### Happy Path
1. El operador toca el botón "+ Entrada" en el dashboard o en la pantalla de registro. 2. Se abre la pantalla de registro manual de entrada. 3. El operador ingresa la placa del vehículo: - Escribiendo manualmente la placa. - O seleccionando de la lista de últimos vehículos registrados (sin pago Pendiente). - O escaneando un código QR/código de vehículo. 4. El operador selecciona la zona de destino (opcional, default: cualquier zona disponible). 5. El operador ajusta la fecha y hora si difiere del momento actual (default: ahora). 6. El operador ingresa una observación (opcional): e.g., "Sin placa visible", "Vehículo de visitante". 7. El operador toca "Registrar Entrada". 8. El sistema: - Valida que no exista un ticket abierto para esa placa. - Asigna un espacio en la zona. - Genera el número de ticket. - Registra la creación manual (origen="MANUAL"). 9. Si la talanquera está configurada para apertura automática, se envía la instrucción de apertura. 10. Se muestra confirmación con el número de ticket y el espacio asignado. 11. Se actualiza el dashboard con los nuevos espacios disponibles. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | UUID | Identificador único del ticket | | numero_ticket | String | Número legible del ticket (ej: "TK-2024-00847") | | placa | String | Placa registrada | | zona_nombre | String | Nombre de la zona asignada | | espacio_numero | String | Número del espacio asignado | | fecha_hora_entrada | DateTime | Timestamp de entrada | | estado | Enum | ABIERTO | | created_by | UUID | ID del operador que creó el ticket | | talanquera_abierta | Boolean | Si la talanquera se abrió exitosamente | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | ticket_id | UUID | Identificador único del ticket | | numero_ticket | String | Número legible del ticket (ej: "TK-2024-00847") | | placa | String | Placa registrada | | zona_nombre | String | Nombre de la zona asignada | | espacio_numero | String | Número del espacio asignado | | fecha_hora_entrada | DateTime | Timestamp de entrada | | estado | Enum | ABIERTO | | created_by | UUID | ID del operador que creó el ticket | | talanquera_abierta | Boolean | Si la talanquera se abrió exitosamente | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El operador puede registrar una entrada manual en menos de 15 segundos. 2. El ticket se genera con un número único y legible. 3. El espacio se asigna correctamente en la zona correspondiente. 4. No se permite crear dos tickets abiertos para la misma placa. 5. Si la talanquera está configurada, se abre automáticamente tras el registro. 6. El operador recibe confirmación visual clara del ticket creado. 7. La acción queda registrada en el log con el origen MANUAL. 8. El dashboard se actualiza para reflejar el nuevo espacio ocupado. ---

## Endpoints
- `POST /api/v1/operator/tickets/entry` — Registra entrada manual - `GET /api/v1/operator/vehicles/recent` — Lista de placas frecuentes - `GET /api/v1/operator/zones/{id}/spaces/available` — Espacios disponibles por zona ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El registro manual debe tener una marca visual distintiva en el ticket (ej: etiqueta "MANUAL") para diferenciarlo de los automáticos. - Se debe permitir al operador editar la placa antes de confirmar si se dio cuenta del error. - La lista de placas frecuentes debe incluir solo placas de vehículos que actualmente NO tienen ticket abierto, para evitar sélection accidental de un vehículo ya dentro.
