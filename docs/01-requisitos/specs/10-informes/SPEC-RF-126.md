# SPEC-10-informes-126 — El sistema debe permitir consultar un reporte consolidado del historial de un...

## Metadata
- **RF origen**: RF-126
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede **quiero** consultar el historial detallado de un cliente **para** conocer su comportamiento de visitas, tiempo promedio de estadía, gasto total acumulado y métodos de pago preferidos. ---

## Objetivo
El sistema debe permitir consultar un reporte consolidado del historial de un cliente, incluyendo: número total de visitas, fecha de primera y última visita, tiempo promedio de estadía, monto total gastado, desglose por método de pago utilizado, y un resumen de los últimos movimientos. Este reporte aplica tanto a clientes eventuales como a clientes de flota (B2B). ---

## Comportamiento Específico

### Happy Path
1. El usuario accede al módulo de Reportes y selecciona la categoría "Historial de Cliente". 2. El usuario ingresa la placa del vehículo o el identificador único del cliente. 3. El sistema valida que el cliente exista y que el usuario tenga permisos sobre esa información. 4. El sistema consulta las transacciones asociadas: a. **Conteo de visitas**: Cantidad total de transacciones (excluyendo canceladas). b. **Primera y última visita**: Fechas mínima y máxima de las transacciones. c. **Tiempo promedio**: Promedio de duración entre entrada y salida en minutos. d. **Gasto total**: Sumatoria de todos los pagos realizados por el cliente. e. **Desglose por método de pago**: Distribución de pagos entre efectivo, transferencia, PSE, QR, etc. f. **Últimas 10 visitas**: Detalle de las transacciones más recientes. 5. El sistema compila los datos y presenta el reporte. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | cliente_id | UUID | Identificador único del cliente | | placa | String | Placa del vehículo principal | | nombre | String | Nombre del cliente (si está registrado) | | tipo_cliente | Enum | EVENTUAL, FLOTA, SUSCRIPTOR | | total_visitas | Integer | Número total de visitas/transacciones | | primera_visita | DateTime | Fecha de la primera transacción | | ultima_visita | DateTime | Fecha de la última transacción | | tiempo_promedio_minutos | Integer | Duración promedio de estadía | | gasto_total | Decimal | Sumatoria de montos pagados (COP) | | metodos_pago | JSON | Desglose por método: {EFECTIVO: 45%, TRANSFERENCIA: 30%, PSE: 20%, QR: 5%} | | ultima_visita_detallada | Object | Datos de la última transacción (fecha, monto, sede, método) | | visitas_recientes | Array | Array de las últimas 10 transacciones con detalle | | estado | Enum | ACTIVO, BLOQUEADO, SUSPENDIDO | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | cliente_id | UUID | Identificador único del cliente | | placa | String | Placa del vehículo principal | | nombre | String | Nombre del cliente (si está registrado) | | tipo_cliente | Enum | EVENTUAL, FLOTA, SUSCRIPTOR | | total_visitas | Integer | Número total de visitas/transacciones | | primera_visita | DateTime | Fecha de la primera transacción | | ultima_visita | DateTime | Fecha de la última transacción | | tiempo_promedio_minutos | Integer | Duración promedio de estadía | | gasto_total | Decimal | Sumatoria de montos pagados (COP) | | metodos_pago | JSON | Desglose por método: {EFECTIVO: 45%, TRANSFERENCIA: 30%, PSE: 20%, QR: 5%} | | ultima_visita_detallada | Object | Datos de la última transacción (fecha, monto, sede, método) | | visitas_recientes | Array | Array de las últimas 10 transacciones con detalle | | estado | Enum | ACTIVO, BLOQUEADO, SUSPENDIDO | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El reporte muestra exactamente los campos descritos: visitas, tiempos promedios, gasto total y desglose por método de pago. 2. El campo `gasto_total` coincide con la suma de todos los pagos del cliente en la base de datos. 3. El tiempo promedio se calcula solo sobre transacciones con entrada y salida registradas (excluye transacciones abiertas). 4. El reporte es exportable a Excel (.xlsx), CSV y PDF. 5. El sistema responde en < 3 segundos para clientes con hasta 1,000 transacciones. 6. Un cliente puede tener varias placas asociadas; todas se incluyen en el historial. ---

## Endpoints
- `GET /api/v1/reports/customer/history` — Consulta historial de un cliente - `GET /api/v1/reports/customer/history/export` — Exporta el historial ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Para clientes de flota (B2B), el reporte adicionalmente puede incluir el contrato asociado y el límite de crédito剩余 si se solicita. - Si el cliente tiene transacciones en múltiples sedes, el reporte agrega la información y indica en cada visita la sede correspondiente. - El campo `metodos_pago` es un JSON con porcentajes y montos absolutos por método.
