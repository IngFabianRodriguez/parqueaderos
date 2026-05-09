# SPEC-10-informes-116 — El sistema debe generar un reporte de ingresos que muestre el total bruto, im...

## Metadata
- **RF origen**: RF-116
- **Módulo**: 10-informes
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de sede o tenant_admin **quiero** consultar un reporte consolidado de ingresos **para** conocer la facturación total, impuestos, descuentos y neto final desglosado por forma de pago y por sede. ---

## Objetivo
El sistema debe generar un reporte de ingresos que muestre el total bruto, impuestos aplicados, descuentos concedidos y el neto final de las transacciones cobradas. El reporte debe poder desglosarse por forma de pago (efectivo, tarjeta, transferencia, etc.) y por sede. Se calculan a partir de las transacciones cerradas en el período seleccionado. ---

## Comportamiento Específico

### Happy Path
1. El usuario selecciona el rango de fechas y opcionalmente filtra por sede (RF-117) 2. El `reporting-service` consulta `transaction-service` para obtener transacciones con estado `closed` en ese período 3. Para cada transacción se extraen: monto bruto, monto_impuesto, monto_descuento, forma_pago, sede_id 4. Se agregan los valores: `total_bruto = SUM(monto_bruto)`, `total_impuestos = SUM(monto_impuesto)`, `total_descuentos = SUM(monto_descuento)`, `neto = total_bruto + total_impuestos - total_descuentos` 5. Se desglosa por forma de pago: agrupar sumas según `forma_pago` 6. Se desglosa por sede: agrupar sumas según `sede_id` 7. Se retorna el reporte consolidado ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | total_bruto | decimal | Suma de todos los montos brutos | | total_impuestos | decimal | Suma de todos los impuestos | | total_descuentos | decimal | Suma de todos los descuentos | | neto_final | decimal | Resultado final (bruto + impuestos - descuentos) | | total_transacciones | integer | Cantidad de transacciones cerradas | | desglose_forma_pago | array | Lista de `{ forma_pago, subtotal, porcentaje }` | | desglose_sede | array | Lista de `{ sede_id, sede_nombre, subtotal }` | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | total_bruto | decimal | Suma de todos los montos brutos | | total_impuestos | decimal | Suma de todos los impuestos | | total_descuentos | decimal | Suma de todos los descuentos | | neto_final | decimal | Resultado final (bruto + impuestos - descuentos) | | total_transacciones | integer | Cantidad de transacciones cerradas | | desglose_forma_pago | array | Lista de `{ forma_pago, subtotal, porcentaje }` | | desglose_sede | array | Lista de `{ sede_id, sede_nombre, subtotal }` | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `neto_final` debe ser exactamente igual a `total_bruto + total_impuestos - total_descuentos` 2. La suma de `subtotal` en `desglose_forma_pago` debe ser igual a `total_bruto` 3. La suma de `subtotal` en `desglose_sede` debe ser igual a `total_bruto` 4. El reporte se genera en menos de 5 segundos para un período de hasta 1 año 5. Solo se incluyen transacciones con estado `closed` (no se incluyen `open` ni `cancelled`) ---

## Endpoints
- `GET /api/v1/reports/income` — Genera reporte de ingresos - `GET /api/v1/transactions?status=closed&date_from={}&date_to={}` — Consulta de transacciones ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los impuestos se asumen como un solo campo `monto_impuesto` por transacción; si hay múltiples tasas (IVA, impuesto local), se суммируют en ese campo - Los descuentos pueden provenir de cupones, tarifas promocionales o ajustes manuales - El reporte es de solo lectura; no modifica ningún registro de transacción
