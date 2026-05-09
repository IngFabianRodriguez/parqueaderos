# SPEC-12-app-cliente-148 — El sistema debe permitir al cliente acceder a sus facturas electrónicas gener...

## Metadata
- **RF origen**: RF-148
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** ver y descargar mis facturas electrónicas (CDT o equivalentes) **para** usarlas como comprobante tributario y para miControl personal de gastos. ---

## Objetivo
El sistema debe permitir al cliente acceder a sus facturas electrónicas generadas por cada transacción o agrupadas por período. El cliente puede ver el detalle de cada factura en la app y descargar el PDF para almacenamiento o envío. ---

## Comportamiento Específico

### Happy Path
1. El cliente accede a "Mi Cuenta" → "Facturas Electrónicas". 2. El sistema muestra el listado de facturas: número de factura, fecha, monto total, estado (activa, cancelada). 3. El cliente puede filtrar por rango de fechas o buscar por número de factura. 4. El cliente pulsa sobre una factura para ver el detalle: - Datos del emisor (nombre del tenant, NIT, dirección). - Datos del receptor (nombre del cliente, CC/NIT). - Detalle de los conceptos (parqueo, zona, vehículo, tiempos). - Subtotal, impuestos, total. - QR de verificación de la DIAN. 5. El cliente puede pulsar "Descargar PDF" para guardar o compartir el archivo. 6. El cliente puede pulsar "Enviar por email" e ingresar una dirección de correo para enviar la factura. 7. Si la factura está cancelada, se muestra un banner indicando el estado. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | factura_id | UUID | Identificador de la factura | | numero_factura | string | Número secuencial de la factura (ej: "FE-2024-001234") | | fecha_emision | timestamp | Fecha y hora de emisión | | sede_nombre | string | Nombre de la sede | | nit_tenant | string | NIT del tenant(emisor) | | nombre_tenant | string | Nombre del tenant | | nit_cliente | string | CC/NIT del cliente(receptor) | | nombre_cliente | string | Nombre del cliente | | subtotal | decimal | Subtotal antes de impuestos | | impuestos | decimal | Monto de impuestos | | total | decimal | Total a pagar | | estado | string | 'activa', 'cancelada', 'reembolsada' | | url_pdf | string | URL del PDF de la factura | | conceptos | array | Lista de conceptos facturados | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | factura_id | UUID | Identificador de la factura | | numero_factura | string | Número secuencial de la factura (ej: "FE-2024-001234") | | fecha_emision | timestamp | Fecha y hora de emisión | | sede_nombre | string | Nombre de la sede | | nit_tenant | string | NIT del tenant(emisor) | | nombre_tenant | string | Nombre del tenant | | nit_cliente | string | CC/NIT del cliente(receptor) | | nombre_cliente | string | Nombre del cliente | | subtotal | decimal | Subtotal antes de impuestos | | impuestos | decimal | Monto de impuestos | | total | decimal | Total a pagar | | estado | string | 'activa', 'cancelada', 'reembolsada' | | url_pdf | string | URL del PDF de la factura | | conceptos | array | Lista de conceptos facturados | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede ver el listado de sus facturas ordenadas por fecha descendente. 2. El cliente puede filtrar por rango de fechas y estado. 3. El cliente puede buscar por número de factura. 4. El cliente puede abrir la factura y ver el detalle completo (emisor, receptor, conceptos). 5. El cliente puede descargar el PDF de la factura al dispositivo. 6. El cliente puede enviar la factura por email a una dirección específica. 7. Las facturas canceladas se muestran diferenciadas y no permiten descarga. 8. La factura incluye QR de verificación de la autoridad fiscal. ---

## Endpoints
- `GET /api/v1/cliente/facturas` — Lista las facturas del cliente - `GET /api/v1/cliente/facturas/{factura_id}` — Detalle de una factura - `GET /api/v1/cliente/facturas/{factura_id}/pdf` — Descarga el PDF - `POST /api/v1/cliente/facturas/{factura_id}/enviar` — Envía la factura por email ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las facturas se generan en formato XML/XPDF según la resolución de facturación electrónica vigente en Colombia. - Se agrupan transacciones del mismo mes en una sola factura mensual si el tenant tiene esa configuración. - El QR de verificación permite validar la autenticidad de la factura consultando el servicio de la DIAN.
