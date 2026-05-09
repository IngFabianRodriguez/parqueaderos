# SPEC-07-079 — Registro de Transacciones Financieras Completas

## Metadata
- **RF origen**: RF-079
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, audit-service, payment-gateway

---

## User Story
**Como** administrador de un tenant **quiero** ver un registro completo e inmutable de todas las transacciones financieras (cobros, reembolsos, ajustes) **para** mantener la integridad contable y poder conciliarlas con mis estados de cuenta bancarios.

## Objetivo
El sistema debe registrar de forma inmutable cada transacción financiera: cobros de estacionamiento, pagos, reembolsos, y ajustes de crédito. Cada registro contiene el monto, método de pago, status, y referencia cruzada a la factura y al vehículo.

## Comportamiento Específico

### Registro de transacciones
1. Cuando se genera una factura (RF-009), se crea un registro en `financial_transactions`.
2. Cuando se recibe un pago, se actualiza `status = completed` y se registra `payment_reference`.
3. Cuando se hace un reembolso (RF-009), se crea un nuevo registro con `type = refund` y `parent_transaction_id` referenciando la transacción original.
4. Cuando se hace un ajuste, se crea un registro con `type = adjustment` y `reason`.

### Campos del registro
- `transaction_id`, `tenant_id`, `site_id`, `invoice_id`, `vehicle_id`
- `type`: `charge`, `payment`, `refund`, `adjustment`, `credit`
- `amount`, `currency`
- `payment_method`: `cash`, `card`, `transfer`, `wallet`
- `payment_reference`: código de autorización, referencia bancaria, etc.
- `status`: `pending`, `completed`, `failed`, `reversed`
- `parent_transaction_id` (para refunds)
- `user_id` (operador que procesó)
- `timestamp`

### Consulta
1. El admin accede a `Reports → Financial Transactions`.
2. Filtros: sede, tipo, método de pago, status, rango de fechas.
3. Exportación a CSV/Excel para contabilidad.

## Criterios de Aceptación
1. Cada operación financiera genera un registro en `financial_transactions`.
2. Los reembolsos referencian la transacción original (`parent_transaction_id`).
3. Los registros son inmutables: solo se actualiza `status`.
4. Cada registro incluye: monto, método de pago, status, timestamp, operador.
5. Los filtros disponibles incluyen: sede, tipo, método, status, rango de fechas.
6. Se puede exportar a CSV para conciliación contable.
7. Los datos se retienen por 5 años.