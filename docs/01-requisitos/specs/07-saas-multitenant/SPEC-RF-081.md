# SPEC-07-saas-multitenant-081 — El sistema debe generar una factura mensual consolidada por empresa B2B que i...

## Metadata
- **RF origen**: RF-081
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de una empresa B2B con flota de vehículos **quiero** recibir una factura consolidada mensual que muestre el detalle de uso por vehículo **para** poder allocate el costo de estacionamiento a los departamentos o centros de costo de mi empresa. ---

## Objetivo
El sistema debe generar una factura mensual consolidada por empresa B2B que incluya: el total facturado, un detalle por vehículo con las transacciones realizadas, el tiempo de permanencia y el monto facturado por cada uno. La factura se genera al final de cada ciclo de facturación (mensual) y se envía por email al contacto de facturación de la empresa. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | invoice_id | uuid | ID de la factura | | company_id | uuid | ID de la empresa | | billing_period | string | Período (ej: "2026-01") | | total_amount | decimal | Monto total facturado | | currency | string | Moneda | | status | enum | `pending`, `sent`, `paid`, `overdue` | | pdf_url | string | URL del PDF de la factura | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | invoice_id | uuid | ID de la factura | | company_id | uuid | ID de la empresa | | billing_period | string | Período (ej: "2026-01") | | total_amount | decimal | Monto total facturado | | currency | string | Moneda | | status | enum | `pending`, `sent`, `paid`, `overdue` | | pdf_url | string | URL del PDF de la factura | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Se genera una factura mensual por empresa B2B, sin importar cuántas transacciones tenga. 2. La factura incluye detalle por vehículo con cantidad de transacciones, tiempo y monto. 3. Los véhicules con dépassement de límite (RF-080) muestran el monto del surcharge como línea separada. 4. La factura se genera en PDF y se envía por email al `billing_email` de la empresa. 5. El `tenant_admin` puede ver, descargar y marcar como pagada cualquier factura de cualquier empresa de su tenant. 6. El `company_admin` puede ver y descargar sus facturas desde el portal de la empresa. 7. Las facturas se numeran secuencialmente (ej: `INV-2026-0001`). 8. Si la empresa tiene plan pre-pago, el consumo se descuenta del crédito disponible; la factura muestra el consumo residual. ---

## Endpoints
- `GET /api/v1/companies/{company_id}/invoices` — Listar facturas de la empresa - `GET /api/v1/companies/{company_id}/invoices/{invoice_id}` — Detalle de factura - `GET /api/v1/companies/{company_id}/invoices/{invoice_id}/pdf` — Descargar PDF - `PUT /api/v1/tenants/{tenant_id}/invoices/{invoice_id}/mark-paid` — Marcar como pagada (tenant_admin) - `POST /api/v1/companies/{company_id}/invoices/{invoice_id}/send` — Reenviar factura por email ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- La generación de facturas es un proceso batch que corre en background; no bloquea la operación. - Se recomienda guardar los PDFs en object storage (S3/GCS) y no en la base de datos. - La numeración de facturas es por tenant, no global; cada tenant tiene su propia secuencia de facturas. - El formato de la factura puede personalizarse con el logo de la empresa si la empresa tiene branding configurado.
