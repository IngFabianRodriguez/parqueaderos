# COMP-012 — Payments Service

## Metadata

- **Nombre**: payments-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8003
- **DB**: PostgreSQL (schema `payments`)
- **Servicios afectados**: tenant-service, iot-service, sede-service, notif-service

---

## Objetivo

Procesar pagos de parqueo (prepago, postpago, recarga), gestionar métodos de pago de clientes (tarjetas, Nequi, Daviplata), manejar transacciones, generar facturas electrónicas, y controlar suscripción de tenants.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0
- **DB**: PostgreSQL 15
- **Message Broker**: Kafka (topic `payments.events`, `payments.commands`)
- **Cache**: Redis (session de pago, rate limiting)
- **Payments Gateway**: Integration con provider de pagos (Stripe o similar)
- **Facturación**: DIAN API (Colombia)

---

## Modelo de Datos

### Tabla: metodos_pago

```
id              UUID PK
cliente_id      UUID FK → clientes
tipo            VARCHAR(30) NOT NULL  -- tarjeta_credito, tarjeta_debito, nequi, daviplata, efectivo
tokenizado      VARCHAR(255)  -- token del provider (Stripe card id, etc)
ultimos_digitos VARCHAR(4)
marca           VARCHAR(50)   -- Visa, Mastercard, Nequi, Daviplata
banco           VARCHAR(100)
es_default      BOOLEAN DEFAULT false
estado          VARCHAR(20) DEFAULT 'activo'  -- activo, inactivo, rechazado
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: transacciones

```
id                  UUID PK
tenant_id           UUID FK → tenants
cliente_id          UUID FK → clientes (nullable para pagos sin cuenta)
sede_id             UUID FK → sedes
tipo                VARCHAR(30) NOT NULL  -- prepago, postpago, recarga, reembolso
monto               DECIMAL(12,2) NOT NULL
moneda              VARCHAR(3) DEFAULT 'COP'
estado              VARCHAR(20) NOT NULL  -- pending, processing, completed, failed, refunded
referencia_externa  VARCHAR(100)  -- ID del provider de pagos
referencia_interna  VARCHAR(50)   -- nuestro reference number
descripcion         VARCHAR(500)
metadata            JSONB DEFAULT '{}'
pagado_en           TIMESTAMPTZ
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: cuentas_cliente

```
id              UUID PK
cliente_id      UUID FK → clientes
saldo           DECIMAL(12,2) DEFAULT 0.00
tipo_cuenta     VARCHAR(20) DEFAULT 'prepago'  -- prepago, postpago
topup_minimo    DECIMAL(10,2) DEFAULT 10000.00
credito_maximo  DECIMAL(12,2) DEFAULT 0.00  -- solo para postpago
used_credit     DECIMAL(12,2) DEFAULT 0.00
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: facturas

```
id                  UUID PK
tenant_id           UUID FK → tenants
cliente_id          UUID FK → clientes
transaccion_id      UUID FK → transacciones
numero_factura      VARCHAR(30) NOT NULL UNIQUE
serie               VARCHAR(10) NOT NULL
prefix              VARCHAR(10) NOT NULL
nit                 VARCHAR(20)
razon_social         VARCHAR(200)
direccion           VARCHAR(500)
subtotal            DECIMAL(12,2) NOT NULL
iva                 DECIMAL(12,2) NOT NULL
total               DECIMAL(12,2) NOT NULL
estado_dian         VARCHAR(20) DEFAULT 'pending'  -- pending, sent, accepted, rejected
dian_response       JSONB
fecha_emision       TIMESTAMPTZ DEFAULT NOW()
created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: suscripciones_tenant

```
id                  UUID PK
tenant_id           UUID FK → tenants
plan_id             VARCHAR(50) NOT NULL  -- basic, professional, enterprise
nombre_plan         VARCHAR(100)
precio_mensual      DECIMAL(10,2) NOT NULL
fecha_inicio        DATE NOT NULL
fecha_renovacion    DATE NOT NULL
estado              VARCHAR(20) DEFAULT 'active'  -- active, cancelled, past_due, trialing
metodo_pago_id      UUID FK → metodos_pago
stripe_subscription_id VARCHAR(100)
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints

### POST /api/v1/payments/prepago
Crear transacción de prepago (cliente reserva espacios).
```json
{
  "cliente_id": "uuid",
  "sede_id": "uuid",
  "monto": 20000,
  "metodo_pago_id": "uuid",
  "duracion_minutos": 60,
  "zona_id": "uuid"
}
```
**Response 201**:
```json
{
  "transaccion_id": "uuid",
  "estado": "pending",
  "monto": 20000,
  "reservation_id": "uuid"
}
```

### POST /api/v1/payments/postpago
Registrar salida y cobrar al cliente.
```json
{
  "cliente_id": "uuid",
  "sede_id": "uuid",
  "ingreso_id": "uuid",
  "metodo_pago_id": "uuid"
}
```
**Response 200**:
```json
{
  "transaccion_id": "uuid",
  "monto": 15000,
  "estado": "completed",
  "factura_id": "uuid"
}
```

### POST /api/v1/payments/recarga
Recargar saldo de cuenta prepago.
```json
{
  "cliente_id": "uuid",
  "monto": 50000,
  "metodo_pago_id": "uuid"
}
```

### GET /api/v1/payments/transacciones
Lista transacciones con filtros.
**Query params**: `cliente_id`, `sede_id`, `tipo`, `estado`, `from`, `to`, `limit`, `offset`

### GET /api/v1/payments/transacciones/:id
Detalle de transacción.

### POST /api/v1/payments/reembolso
Procesar reembolso (solo transacciones completed en últimas 24h).
```json
{
  "transaccion_id": "uuid",
  "motivo": "duplicada"
}
```

### GET /api/v1/payments/cliente/:cliente_id/cuenta
Consultar saldo y cuenta del cliente.
```json
{
  "cuenta_id": "uuid",
  "saldo": 35000,
  "tipo_cuenta": "prepago",
  "credito_disponible": 0
}
```

### GET /api/v1/payments/metodos
Lista métodos de pago del cliente autenticado.

### POST /api/v1/payments/metodos
Agregar método de pago (tokeniza con provider).
```json
{
  "tipo": "tarjeta_credito",
  "token": "tok_xxx",  // token de Stripe
  "es_default": true
}
```

### DELETE /api/v1/payments/metodos/:id
Eliminar método de pago (no puede ser el único si es default).

### PUT /api/v1/payments/metodos/:id/default
Marcar método de pago como default.

### GET /api/v1/payments/facturas
Lista facturas del cliente.

### GET /api/v1/payments/facturas/:id
Detalle de factura con PDF URL.

### GET /api/v1/payments/tenant/suscripcion
Suscripción actual del tenant.

### POST /api/v1/payments/tenant/suscripcion
Crear/modificar suscripción (upgrade/downgrade).
```json
{
  "plan_id": "professional",
  "metodo_pago_id": "uuid"
}
```

### POST /api/v1/payments/webhook
Webhook del provider de pagos (Stripe).
```json
{
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      "id": "pi_xxx",
      "amount": 20000
    }
  }
}
}
```

---

## Flujo de Prepago

```
1. Cliente selecciona duración y método de pago
2. POST /payments/prepago → crea transacción estado=pending
3. Charge con provider (Stripe) usando token
4. Si exitoso → estado=completed, generar reserva
5. Publicar evento payments.prepago_completed en Kafka
6. notif-service recibe evento → push confirmation
7. Si falla → estado=failed, notificar cliente
```

---

## Flujo de Postpago (Salida)

```
1. Operador registra salida → iot-service detecta
2. iot-service → POST /payments/postpago
3. payments-service calcula tarifa según tiempo y reglas
4. Verifica si cliente tiene cuenta con saldo suficiente
5. Si prepago con saldo: debitar de saldo interno
6. Si postpago o saldo insuficiente: cobrar via método default
7. Generar transacción estado=completed
8. Generar factura DIAN
9. Publicar payments.postpago_completed en Kafka
10. Enviar receipt via notif-service
```

---

## Integración con Providers de Pago

### Stripe (ejemplo)

```python
# Cargo con tarjeta guardada
stripe.PaymentIntent.create(
    amount=monto,
    currency='cop',
    customer=customer_stripe_id,
    payment_method=tokenizado,
    confirm=True,
    off_session=True
)
```

### Nequi/Daviplata

- SDK oficial de Davivienda para Nequi
- Webhooks para confirmación async
- Límites: max 1M COP por transacción, 5M COP diario

### Reconocimiento y Reintento

- Retry automático 3 veces con exponential backoff (1s, 3s, 10s)
- En caso de failure persistente: marcar transacción como failed, notificar al cliente, generar alerta ops

---

## Rate Limiting

- Prepago/recarga: 10 requests por minuto por cliente
- Postpago: 30 requests por minuto por sede
- Consulta saldo: 60 requests por minuto por cliente

---

## DIAN Integration (Facturación)

### Config

```python
DIAN_API_URL=https://factura-electronica.dian.gov.co
DIAN_WS_URL=wss://factura-electronica.dian.gov.co/ws
```

### Flujo de Factura

```
1. Transacción completed → crear factura en BD
2. POST /dian/invoice con datos obligatorios:
   - NIT emisor, nombre, dirección
   - NIT receptor (del cliente si es empresa)
   - Items: descripción, cantidad, valor unitario, IVA
3. DIAN responde con CUFE y estado
4. Actualizar factura con estado_dian = 'sent'
5. Esperar async callback con acceptance/rejection
6. Guardar respuesta DIAN en dian_response
```

### Retries Facturas DIAN

- 3 intentos con backoff (30s, 2min, 10min)
- Almacenar en cola si provider DIAN no disponible
- Alertas si > 5 facturas pendientes > 1 hora

---

## Kafka Events

### Topic: payments.events

```json
{
  "event_id": "uuid",
  "tenant_id": "uuid",
  "event_type": "prepago_completed",
  "transaccion_id": "uuid",
  "cliente_id": "uuid",
  "sede_id": "uuid",
  "monto": 20000,
  "timestamp": "2026-01-15T10:30:00Z"
}
```

```json
{
  "event_id": "uuid",
  "event_type": "postpago_completed",
  "transaccion_id": "uuid",
  "ingreso_id": "uuid",
  "factura_id": "uuid",
  "timestamp": "2026-01-15T10:35:00Z"
}
```

```json
{
  "event_id": "uuid",
  "event_type": "reembolso_processed",
  "transaccion_original_id": "uuid",
  "monto_reembolsado": 20000,
  "timestamp": "2026-01-15T11:00:00Z"
}
```

---

## Dependencias

- **DB**: PostgreSQL `payments` schema
- **Kafka**: payments.events, payments.commands
- **Redis**: cache de sesión de pago
- **auth-service**: JWT validation
- **notif-service**: notificaciones de pago
- **iot-service**: para flujo de postpago
- **stripe**: payment provider
- **dian**: facturación electrónica Colombia

---

## Métricas

- `payments_transacciones_total{tipo, estado}`
- `payments_monto_total{tipo, sede_id}`
- `payments_procesamiento_duration_ms`
- `payments_reembolsos_total`
- `payments_facturas_dian_total{estado}`
- `payments_method_added_total{tipo}`
- `payments_suscripciones_total{plan, estado}`

---

## Health Checks

`GET /health` → `{ "status": "ok", "db": "connected", "kafka": "connected", "stripe": "connected" }`
`GET /health/ready` → DB + Stripe connectivity
`GET /health/live` → proceso corriendo

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Provider pago down | Buffer transacciones, retry luego, notificar ops si > 5 min |
| Saldo insuficiente postpago | Rechazar apertura talanquera, notificar cliente, registrar alerta |
| Tarjeta rechazada | Marcar método como rechazado, notificar cliente, sugerir otro método |
| DIAN down | Guardar facturas en cola, retry automático, alerta ops si > 1h |
| Reembolso > 24h | 400 Bad Request, sugerir contactar soporte |
| Duplicar prepago (mismo cliente + sede + 1min) | Deduplicate, return existing transaction |
| Cliente sin métodos de pago | 402 Payment Required, sugerir agregar método |