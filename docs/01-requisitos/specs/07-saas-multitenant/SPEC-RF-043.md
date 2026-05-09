# SPEC-07-043 — Generación de Invoices Internos Diferenciados

## Metadata
- **RF origen**: RF-043
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, invoice-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** ver invoices claras que separen la suscripción base, los excedentes y los impuestos **para** entender exactamente por qué se me cobra cada mes.

## Objetivo
El sistema debe generar invoices internos para cada ciclo de facturación que muestren de forma detallada y diferenciada: el cargo de la suscripción base, los cargos por excedentes (overage), y los impuestos aplicables (IVA 19% para Colombia), con totales claros y líneas descriptivas.

## Comportamiento Específico

### Happy Path
1. Al confirmarse el pago de renovación (webhook `invoice.payment_succeeded`), el sistema genera la invoice interna
2. Si no hay webhook (pago pendiente), el job nocturno del día `current_period_end` genera la invoice con estado `pending`
3. La invoice se construye con líneas diferenciadas: Suscripción base → Excedentes (si aplica) → Subtotal → IVA 19% → Total
4. Se almacena en `invoices` con campos: `invoice_id`, `tenant_id`, `stripe_invoice_id`, `period_start`, `period_end`, `lines` (JSON), `subtotal`, `tax`, `total`, `currency`, `status`
5. Se envía por email al tenant_admin con PDF adjunto
6. Se sincroniza con el módulo de contabilidad

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Sin overages en el mes | Invoice solo con línea de suscripción base; sin líneas de overage |
| Plan annual | Invoice mensual muestra cargo prorrateado; total anual como referencia |
| Invoice pendiente por pago fallido | Estado `pending`; al resolverse se actualiza a `paid` |
| Tenant solicita invoice para contabilidad | PDF descargable de cualquier invoice histórica |
| IVA exento (tenant con certificado) | Se omite línea de IVA; se marca `tax_exempt = true` |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| period_start | date | Inicio del periodo de facturación | Sí |
| period_end | date | Fin del periodo de facturación | Sí |
| subscription_charge | decimal | Cargo de la suscripción base | Sí |
| overage_charges | array | Lista de cargos de excedentes | Sí |
| tax_rate | decimal | Tasa de impuesto (0.19 para IVA) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| invoice_id | UUID | Identificador interno de la invoice |
| stripe_invoice_id | string | ID de la invoice en Stripe |
| lines | JSON | Detalle de líneas de la invoice |
| subtotal | decimal | Subtotal sin impuestos |
| tax_amount | decimal | Monto de IVA |
| total | decimal | Total a pagar |
| status | enum | `pending`, `paid`, `void` |
| due_date | date | Fecha de vencimiento (= period_end) |
| pdf_url | string | URL del PDF generado |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada invoice tiene líneas diferenciadas: suscripción base, overages (si aplica), IVA, total
2. La invoice está disponible en PDF y en la UI (Settings > Facturación > Invoices)
3. La invoice se envía por email al tenant_admin al momento de generarse
4. La invoice incluye el `stripe_invoice_id` para trazabilidad con Stripe
5. Los overages se facturan con el precio unitario definido en el plan (RF-039)
6. El IVA se calcula como 19% del subtotal (excepto si el tenant es tax_exempt)
7. Las invoices históricas están disponibles para consulta y descarga
8. La numeración de invoices sigue el formato: `INV-[YYYY]-[SEQ]`

## Endpoints
- `GET /api/v1/invoices` — Listar invoices del tenant
- `GET /api/v1/invoices/{invoice_id}` — Detalle de una invoice
- `GET /api/v1/invoices/{invoice_id}/pdf` — Descargar PDF de la invoice

## Health Check
- `GET /health` → { "status": "ok" }