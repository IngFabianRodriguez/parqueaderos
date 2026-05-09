# SPEC-03-011 — Gestionar múltiples métodos de pago

## Metadata
- **RF origen**: RF-011
- **Módulo**: 03-crm-pagos
- **Prioridad**: Alta
- **Servicios**: payment-service, crm-service

---

## User Story
Como Operador de caja o Cliente (pago desde app) **quiero** registrar pagos usando efectivo, PSE, tarjeta débito/crédito, Nequi o Daviplata **para** cubrir todas las preferencias de mis clientes y garantizar que cada sesión de parqueo pueda cerrarse con el medio de pago disponible.

## Objetivo
El sistema debe soportar el registro y procesamiento de pagos mediante múltiples canales: efectivo (caja física), PSE (pago instantáneo banca colombiana), tarjetas débito/crédito (terminal POS integrada o link de pago), y wallets digitales Nequi y Daviplata. Cada transacción de pago debe quedar registrada con idempotencia para evitar cobros duplicados.

## Comportamiento Específico
### Happy Path (Pago en caja con efectivo)
1. Operador presenta al cliente el valor a pagar (calculado por RF-013)
2. Cliente entrega efectivo
3. Operador registra el pago ingresando monto recibido en el sistema
4. Sistema calcula cambio y lo muestra
5. Operador confirma el pago
6. Sistema registra transacción método=`efectivo`, estado=`completada`
7. Sistema actualiza sesión a `pagada`
8. Sistema genera comprobante
9. Sistema habilita apertura de talanquera (RF-018)

### Happy Path (Pago con PSE)
1. Sistema genera link de pago PSE con monto, reference y merchant_id
2. Cliente recibe link por pantalla o email/SMS
3. Cliente abre su banca en línea y realiza el pago PSE
4. Pasarela PSE confirma a webhook del sistema
5. Sistema valida signature del webhook
6. Sistema actualiza sesión a `pagada`
7. Sistema notifica al operador (push) y al cliente

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Pago PSE cae por timeout del banco (>30s) | Sistema marca pago como `pendiente` y activa job de polling cada 10s por 5 minutos |
| Tarjeta declinada | Sesión no cambia. Operador puede ofrecer otro método |
| Cliente intenta pagar sesión ya pagada | 409 Conflict con datos del pago original |
| Idempotency key duplicado | Retorna el pago original, no crea duplicado |
| PSE: cliente inicia pago pero no completa | Job de cleanup marca como `expirado` después de 30 min |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| sesion_id | UUID | ID de la sesión de parqueo a pagar | Sí |
| metodo_pago | VARCHAR | efectivo, pse, tarjeta_debito, tarjeta_credito, nequi, daviplata | Sí |
| monto | DECIMAL | Monto a pagar (validado contra sesión) | Sí |
| referencia_externa | VARCHAR | Referencia de la pasarela (PSE, Nequi, etc.) | No |
| idempotency_key | VARCHAR | UUID generado por cliente para evitar duplicados | Sí |
| usuario_id | UUID | Operador o cliente que inicia el pago | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| pago_id | UUID | — |
| sesion_id | UUID | — |
| metodo_pago | VARCHAR | — |
| monto | DECIMAL | — |
| estado | VARCHAR | completada, fallida, pendiente |
| timestamp | TIMESTAMP | — |
| comprobante_url | VARCHAR | Link al PDF del comprobante |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo pago genera un UUID único y se registra en la tabla `pago`
2. Pagos con mismo `idempotency_key` no generan duplicados — retornan el original
3. El estado de la sesión de parqueo se actualiza atómicamente al confirmar el pago
4. Sesión no puede pasar a `pagada` si el monto no coincide con lo calculado por RF-013
5. Timeouts de pasarelas externas no dejan la sesión en estado inconsistente
6. El sistema permite reintentar un pago fallido sin cerrar la sesión

## Endpoints
- `POST /api/v1/pagos` — Iniciar pago
- `GET /api/v1/pagos/{pago_id}` — Consultar estado de un pago
- `POST /api/v1/pagos/webhook/pse` — Webhook confirmación PSE
- `POST /api/v1/pagos/webhook/wallet` — Webhook confirmación Nequi/Daviplata
- `GET /api/v1/pagos/sesion/{sesion_id}` — Historial de pagos de una sesión

## Health Check
- `GET /health` → `{ "status": "ok", "service": "payment-service" }`

## Notas
- Idempotency key compuesta: `{tenant_id}-{sesion_id}-{idempotency_key}` para garantizar unicidad multi-tenant.
- Moneda: COP (pesos colombianos). No se soportan decimales más allá de 2 cifras.
- Terminal POS: el sistema solo recibe resultado final (aprobado/rechazado) del SDK del adquiriente.
- Para pagos parciales con wallet: el saldo disponible se aplica primero, el resto con otro método.