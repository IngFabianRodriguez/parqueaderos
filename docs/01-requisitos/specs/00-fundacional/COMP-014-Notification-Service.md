# COMP-014 — Notification Service

## Metadata

- **Nombre**: notif-service
- **Tipo**: Microservicio
- **Prioridad**: Alta
- **Puerto**: 8005
- **DB**: PostgreSQL (schema `notif`)
- **Servicios afectados**: todos los servicios (consumidor), auth-service (envío emails)

---

## Objetivo

Centralizar el envío de notificaciones a usuarios: push notifications (FCM/APNS), emails (SMTP/SendGrid), SMS (Twilio), y webhooks. Proveer API para envío transaccional, templates personalizables, tracking de entrega, y preferencias de usuario por canal.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0
- **DB**: PostgreSQL 15
- **Cache**: Redis (queue de mensajes pendientes, deduplicación)
- **Message Broker**: Kafka (topic `notif.commands`, `notif.events`)
- **Push**: Firebase Cloud Messaging (FCM), Apple Push Notification Service (APNS)
- **Email**: SendGrid API o SMTP
- **SMS**: Twilio API
- **Templates**: Jinja2 para email y SMS

---

## Modelo de Datos

### Tabla: notificaciones

```
id                  UUID PK
tenant_id           UUID FK → tenants
user_id             UUID FK → users (nullable para broadcast)
cliente_id          UUID FK → clientes (nullable)
tipo                VARCHAR(30) NOT NULL  -- push, email, sms, webhook
categoria           VARCHAR(50) NOT NULL  -- transaccional, marketing, sistema
template_id         VARCHAR(100)
title               VARCHAR(200)
body                TEXT
data_payload        JSONB DEFAULT '{}'  -- datos adicionales para push
status              VARCHAR(20) DEFAULT 'pending'  -- pending, sent, delivered, failed, bounced
channel             VARCHAR(20) NOT NULL  -- push, email, sms, webhook
priority            VARCHAR(10) DEFAULT 'normal'  -- low, normal, high, critical
scheduled_at        TIMESTAMPTZ          -- para envío programado
sent_at             TIMESTAMPTZ
delivered_at        TIMESTAMPTZ
read_at             TIMESTAMPTZ
opened_at           TIMESTAMPTZ           -- para email/push
clicked_at          TIMESTAMPTZ
failure_reason      TEXT
retry_count         INTEGER DEFAULT 0
max_retries         INTEGER DEFAULT 3
created_at          TIMESTAMPTZ DEFAULT NOW()
updated_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: templates

```
id              UUID PK
tenant_id       UUID FK → tenants
nombre          VARCHAR(100) NOT NULL
categoria       VARCHAR(50) NOT NULL  -- transaccional, marketing, sistema
canal           VARCHAR(20) NOT NULL  -- push, email, sms, all
asunto          VARCHAR(300)          -- para email
title           VARCHAR(200)          -- para push
body_template   TEXT NOT NULL         -- Jinja2 template
variables       JSONB DEFAULT '[]'    -- variables esperadas
is_active       BOOLEAN DEFAULT true
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: preferencias_notificacion

```
id              UUID PK
user_id         UUID FK → users
email_enabled   BOOLEAN DEFAULT true
push_enabled    BOOLEAN DEFAULT true
sms_enabled     BOOLEAN DEFAULT false
email_frequency VARCHAR(20) DEFAULT 'instant'  -- instant, daily_digest, weekly
push_sound      VARCHAR(100) DEFAULT 'default'
push_vibration  BOOLEAN DEFAULT true
quiet_hours_start TIME
quiet_hours_end   TIME
created_at      TIMESTAMPTZ DEFAULT NOW()
updated_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: dispositivos_push

```
id              UUID PK
user_id         UUID FK → users
token           VARCHAR(500) NOT NULL
platform        VARCHAR(10) NOT NULL  -- ios, android, web
device_id       VARCHAR(100)
is_active       BOOLEAN DEFAULT true
last_used       TIMESTAMPTZ
created_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: webhooks_config

```
id              UUID PK
tenant_id       UUID FK → tenants
nombre          VARCHAR(100) NOT NULL
url             VARCHAR(500) NOT NULL
event_types     VARCHAR(50)[] DEFAULT '{}'  -- tipos de eventos a enviar
headers         JSONB DEFAULT '{}'  -- headers personalizados (auth)
is_active       BOOLEAN DEFAULT true
secret          VARCHAR(255)  -- para HMAC signature
last_triggered  TIMESTAMPTZ
failure_count   INTEGER DEFAULT 0
created_at      TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: webhook_logs

```
id              UUID PK
webhook_config_id UUID FK → webhook_configs
notificacion_id UUID FK → notificaciones
request_id      VARCHAR(100)
status_code     INTEGER
request_payload TEXT
response_body   TEXT
duration_ms     INTEGER
timestamp       TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints

### POST /api/v1/notif/send
Enviar notificación imediata.
```json
{
  "user_id": "uuid",
  "tipo": "push",
  "template_id": "parking_reminder",
  "variables": { "placa": "ABC123", "horas": 2 },
  "priority": "high"
}
```

### POST /api/v1/notif/send-batch
Enviar a múltiples usuarios.
```json
{
  "user_ids": ["uuid1", "uuid2"],
  "tipo": "email",
  "template_id": "promo_20off",
  "variables": {}
}
```

### POST /api/v1/notif/schedule
Programar notificación futura.
```json
{
  "user_id": "uuid",
  "tipo": "sms",
  "template_id": "appointment_reminder",
  "variables": { "fecha": "2026-01-20", "hora": "14:00" },
  "scheduled_at": "2026-01-20T10:00:00Z"
}
```

### GET /api/v1/notif/notifications
Lista notificaciones del usuario.
**Query params**: `status`, `tipo`, `from`, `to`, `limit`, `offset`

### GET /api/v1/notif/notifications/:id
Detalle de notificación.

### PUT /api/v1/notif/notifications/:id/read
Marcar como leída.

### GET /api/v1/notif/templates
Lista templates disponibles.
**Query params**: `tenant_id`, `categoria`, `canal`

### POST /api/v1/notif/templates
Crear template.
```json
{
  "tenant_id": "uuid",
  "nombre": "recordatorio_vencimiento",
  "categoria": "transaccional",
  "canal": "push",
  "title": "Tu parqueo está por vencer",
  "body_template": "Hola {{nombre}}, tu vehículo {{placa}} lleva {{horas}} horas. ¿Deseas renovar?",
  "variables": ["nombre", "placa", "horas"]
}
```

### PUT /api/v1/notif/templates/:id
Actualizar template.

### GET /api/v1/notif/preferences
Preferencias de notificación del usuario autenticado.

### PUT /api/v1/notif/preferences
Actualizar preferencias.
```json
{
  "push_enabled": true,
  "email_enabled": false,
  "sms_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "07:00"
}
```

### POST /api/v1/notif/devices
Registrar dispositivo push.
```json
{
  "token": "firebase_token_here",
  "platform": "android",
  "device_id": "device-uuid"
}
```

### DELETE /api/v1/notif/devices/:id
Eliminar dispositivo push.

### GET /api/v1/notif/webhooks
Lista webhooks configurados.

### POST /api/v1/notif/webhooks
Crear webhook.
```json
{
  "tenant_id": "uuid",
  "nombre": "ERP Integration",
  "url": "https://erp.cliente.com/webhook/parkcore",
  "event_types": ["pago_completed", "ingreso_creado"],
  "headers": { "Authorization": "Bearer xxx" },
  "secret": "webhook_secret_xyz"
}
```

### POST /api/v1/notif/webhooks/:id/test
Probar webhook (envía dummy payload).

---

## Flujo de Envío

### Notificación Push

```
1. Servicio origen → POST /notif/send (user_id, template_id, variables)
2. notif-service consulta preferencias (push_enabled?)
3. Obtener device tokens del usuario (puede tener múltiples)
4. Render template con variables
5. Enviar a FCM/APNS con data_payload
6. Guardar notificación en BD
7. Esperar delivery receipt (FCM callback)
8. Actualizar status delivered + timestamps
9. Si failure → retry según max_retries
```

### Notificación Email

```
1. Render template (subject + body Jinja2)
2. Texto plano → HTML (para emails con styling)
3. Enviar via SendGrid API
4. Escuchar bounce/complaint webhooks
5. Actualizar status según respuesta
```

### Webhook Delivery

```
1. Evento llega (pago_completed, etc)
2. Buscar webhooks activos para ese event_types
3. Para cada webhook:
   a. Generar payload JSON
   b.添字 HMAC-SHA256 signature en header X-Signature
   c. POST al url configurado
   d. Log request + response
   e. Si falla → retry con backoff
```

---

## Templates

### Ejemplo: recordatorio_vencimiento (push)

```jinja2
Title: Tu parqueo está por vencer
Body: Hola {{ nombre }}, tu vehículo {{ placa }} lleva {{ horas }} horas en {{ sede }}.
     ¿Deseas renovar desde la app?
```

### Ejemplo: factura_generada (email)

```jinja2
Subject: Factura #{{ numero_factura }} - {{ sede }}
Body HTML:
<html>
<body>
<h2>Factura electrónica</h2>
<p>Hola {{ nombre }},</p>
<p>Se ha generado la factura #{{ numero_factura }} por valor de ${{ total }}</p>
<p>Sede: {{ sede }}</p>
<p>Fecha: {{ fecha }}</p>
<a href="{{ factura_url }}">Descargar PDF</a>
</body>
</html>
```

### Variables Disponibles

- `{{ nombre }}`, `{{ email }}`, `{{ telefono }}`
- `{{ placa }}`, `{{ sede }}`, `{{ zona }}`
- `{{ monto }}`, `{{ fecha }}`, `{{ hora }}`
- `{{ numero_factura }}`, `{{ tiempo_minutos }}`
- `{{ link_app }}`, `{{ link_web }}`

---

## Channels

### Push (FCM)

```python
# Firebase Admin SDK
message = messaging.MulticastMessage(
    notification=messaging.Notification(
        title=title,
        body=body
    ),
    data=data_payload,
    tokens=device_tokens
)
response = messaging.send_multicast(message)
```

### Email (SendGrid)

```python
# SendGrid API
message = Mail(
    from_email='no-reply@parkcore.io',
    to_emails=user_email,
    subject=subject,
    html_content=html_body
)
sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
sg.send(message)
```

### SMS (Twilio)

```python
client = Client(twilio_account, twilio_token)
message = client.messages.create(
    body=sms_body,
    from_=twilio_from,
    to=f'+57{phone_number}'
)
```

---

## Rate Limits y Cuotas

| Channel | Límite | Notas |
|---------|--------|-------|
| Push FCM | 500k/day por proyecto | Warning si > 80% |
| Email SendGrid | 100k/month basic | Upgrade si se requiere |
| SMS Twilio | $500/month | Cost per SMS ~$0.05 |

### Rate Limiting Interno

- Push: 50 por usuario por minuto
- Email: 10 por usuario por minuto
- SMS: 5 por usuario por minuto
- Webhooks: 20 por minuto por endpoint

---

## Retry Logic

- Retry 1: 30 segundos
- Retry 2: 2 minutos
- Retry 3: 10 minutos
- Después de 3 retries → status=failed, no más retry
- Alertas a ops si > 10 failures en 1 hora

---

## Quiet Hours

```python
# No enviar push/email/sms durante quiet hours
# Excepto para priority=critical
def should_send(user_id, channel, priority):
    if priority == 'critical':
        return True
    prefs = get_preferences(user_id)
    if not prefs[f'{channel}_enabled']:
        return False
    now = datetime.now()
    if in_quiet_hours(now, prefs):
        return False
    return True
```

---

## Kafka Integration

### Topic: notif.commands (consumed)

```json
{
  "command_id": "uuid",
  "tipo": "enviar",
  "user_id": "uuid",
  "canal": "push",
  "template_id": "pago_confirmado",
  "variables": {},
  "priority": "high",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

### Topic: notif.events (published)

```json
{
  "event_id": "uuid",
  "notificacion_id": "uuid",
  "user_id": "uuid",
  "event_type": "notif_sent",
  "canal": "push",
  "timestamp": "2026-01-15T10:30:00Z"
}
```

```json
{
  "event_id": "uuid",
  "event_type": "notif_delivered",
  "notificacion_id": "uuid",
  "delivered_at": "2026-01-15T10:30:05Z"
}
```

---

## Eventos desde Otros Servicios

### payments-service → notif-service

```json
{
  "event_type": "pago_completed",
  "cliente_id": "uuid",
  "transaccion_id": "uuid",
  "monto": 15000,
  "metodo": "nequi"
}
```

### iot-service → notif-service

```json
{
  "event_type": "vehiculo_sin_pago",
  "sede_id": "uuid",
  "ingreso_id": "uuid",
  "placa": "ABC123",
  "horas_estacionado": 4
}
```

---

## Dependencias

- **DB**: PostgreSQL `notif` schema
- **Redis**: queue de mensajes pendientes
- **Kafka**: notif.commands, notif.events
- **FCM**: Firebase Cloud Messaging
- **APNS**: Apple Push Notification Service
- **SendGrid**: email transactional
- **Twilio**: SMS
- **auth-service**: (usado para verificar usuarios)

---

## Métricas

- `notif_sent_total{canal, categoria, status}`
- `notif_delivered_total{canal}`
- `notif_failed_total{canal, failure_reason}`
- `notif_retry_total`
- `notif_webhook_delivery_total{status_code}`
- `notif_webhook_duration_ms`
- `notif_queue_size` (Redis pending messages)
- `notif_templates_total{tenant}`

---

## Health Checks

`GET /health` → `{ "status": "ok", "fcm": "connected", "sendgrid": "connected", "twilio": "connected" }`
`GET /health/ready` → DB + Redis + proveedores externos
`GET /health/live` → proceso corriendo

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| FCM down | Buffer push en Redis, retry con backoff, fallback a email si priority=high |
| Email bounce | Marcar notificación failed, registrar bounce, no reintentar |
| Twilio API error | Retry 3x, luego marcar failed, alerta ops |
| Usuario sin device tokens | Fallback a email si email_enabled=true |
| Template con variable faltante | Log warning, skip variable, no fallar envío |
| Quiet hours active | Buffer notificación, entregar al final del período |
| Webhook URL returning 4xx/5xx | Retry 3x, luego marcar failed, alert ops |
| Duplicar envío (mismo user+template+1min) | Deduplicate en Redis (key: hash), evitar spam |