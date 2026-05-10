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

## Datos de Entrada
- **tenant_id** — ID del tenant (UUID, required, auto del contexto)
- **site_id** — ID de la sede donde ocurrió la transacción (UUID, required)
- **invoice_id** — ID de la factura asociada (UUID, required para charges/payments)
- **vehicle_id** — ID del vehículo asociado (UUID, required)
- **type** — Tipo de transacción (enum: `charge`, `payment`, `refund`, `adjustment`, `credit`, required)
- **amount** — Monto de la transacción (decimal, required)
- **currency** — Moneda del monto (string, required, ISO 4217)
- **payment_method** — Método de pago (enum: `cash`, `card`, `transfer`, `wallet`, required)
- **payment_reference** — Referencia de pago (string, optional): código de autorización, ref bancaria
- **parent_transaction_id** — ID de transacción original para reembolsos (UUID, conditional, required si type = refund)
- **user_id** — ID del operador que procesa la transacción (UUID, required)
- **reason** — Razón del ajuste si type = adjustment (string, conditional)

## Datos de Salida
- **financial_transactions** — Tabla con registro inmutable de transacciones:
  - `transaction_id` (UUID)
  - `tenant_id`, `site_id`, `invoice_id`, `vehicle_id`
  - `type`, `amount`, `currency`
  - `payment_method`, `payment_reference`
  - `status` (`pending`, `completed`, `failed`, `reversed`)
  - `parent_transaction_id`, `user_id`, `timestamp`
- **Respuesta al consultar** — Lista filtrada de transacciones con totales