# SPEC-03-017 — Prepago (billetera virtual) con cargo y descuento automático

## Metadata
- **RF origen**: RF-017
- **Módulo**: 03-crm-pagos
- **Prioridad**: Media
- **Servicios**: wallet-service, payment-service, crm-service

---

## User Story
Como Cliente frecuente o Corporativo **quiero** cargar dinero anticipado en una billetera virtual asociada a mi cuenta **para** que mis pagos se ejecuten automáticamente sin pasar por caja y sin efectivo.

## Objetivo
El sistema debe permitir al cliente contar con una billetera virtual (wallet) vinculada a su perfil, donde puede cargar saldo mediante múltiples métodos de pago. Este saldo se descuenta automáticamente al realizar un pago de parqueo, en parte o en su totalidad.

## Comportamiento Específico
### Happy Path (Cliente recarga billetera desde app)
1. Cliente abre app y accede a sección "Mi Wallet"
2. Selecciona "Recargar"
3. Ingresa monto a recargar
4. Selecciona método de pago (PSE o transferencia)
5. Sistema genera referencia de pago
6. Cliente realiza el pago desde su banco
7. Pasarela confirma a webhook
8. Sistema incrementa saldo de wallet
9. Notificación enviada al cliente confirmando recarga

### Happy Path (Descuento automático en pago de parqueo)
1. Vehículo con placa asociada a cliente con wallet
2. Sesión se cierra y precio calculado (RF-013)
3. Sistema verifica si cliente tiene wallet con saldo > 0
4. Si hay saldo: aplica descuento del wallet hasta cubrir el monto total o hasta agotar saldo
5. Si queda monto pendiente: puede usar otro método (efectivo, PSE, etc.)
6. Si el wallet cubre todo: sesión marcada como `pagada`, comprobante generado

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Recarga vía PSE no se confirma en 30 min | Se marca como `pendiente`. Si no llega confirmación, se elimina la reserva y alerta al admin |
| Cliente intenta usar wallet con saldo 0 | Sistema no aplica descuento. Operador/cliente debe usar otro método |
| Saldo insuficiente para cubrir todo el parqueo | Sistema descuenta lo que hay y el cliente paga la diferencia con otro método |
| Recarga duplicate (misma idempotency key reenviada) | Retorna la transacción original, no crea duplicado |
| Cargo mensual corporativo falla (sin saldo) | Admin alertado. Vehicles can still park but admin must recharge manually |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| cliente_id | UUID | Dueño de la wallet | Sí |
| monto | DECIMAL | Monto a recargar o valor a descontar | Sí |
| tipo_transaccion | VARCHAR | recarga, descuento, reversión, cargo_mensual | Sí |
| metodo_pago | VARCHAR | pse, transferencia, efectivo, cargo_tarjeta | Sí |
| referencia_externa | VARCHAR | ID de la transacción en la pasarela | No |
| idempotency_key | VARCHAR | Para evitar duplicados en recarga | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| wallet_id | UUID | — |
| cliente_id | UUID | — |
| saldo_actual | DECIMAL | — |
| transaccion_id | UUID | — |
| monto | DECIMAL | — |
| tipo | VARCHAR | — |
| timestamp | TIMESTAMP | — |
| saldo_nuevo | DECIMAL | Balance después de la transacción |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Wallet creada automáticamente al registrar cliente (RF-010)
2. Cada recarga y descuento genera transacción con UUID y timestamp
3. Saldo de wallet nunca es negativo
4. Idempotencia garantizada para recargas (evitar duplicados por reintentos)
5. Descuento automático en pago respetado si wallet tiene saldo > 0
6. Historial de transacciones de wallet consultable por cliente y admin
7. Plan mensual corporativo se descuenta automáticamente del wallet

## Endpoints
- `POST /api/v1/wallet/recargar` — Recargar saldo
- `GET /api/v1/wallet/saldo?cliente_id=X` — Consultar saldo
- `GET /api/v1/wallet/transacciones?cliente_id=X` — Historial de transacciones
- `POST /api/v1/wallet/recargar/caja` — Recarga en caja por operador

## Health Check
- `GET /health` → `{ "status": "ok", "service": "wallet-service" }`

## Notas
- Recargas de wallet no son pagos de parqueo, no disparan facturación electrónica inmediatamente.
- Cuando el wallet se usa para pagar una sesión de parqueo, ese pago sí genera factura (RF-012).
- Minimum recharge amount: $10,000 COP (~$2.50 USD).
- Maximum balance: $500,000 COP (anti-money laundering).
- Corporate plans: monthly billing se descuenta del wallet de la empresa en la fecha de renovación.