# COMP-016 — Support Service

## Metadata

- **Nombre**: support-service
- **Tipo**: Microservicio
- **Prioridad**: Crítica
- **Puerto**: 8016
- **DB**: PostgreSQL (schema `soporte`)
- **Cache**: Redis (sesiones de chat, estado de tickets)
- **Servicios afectados**: notification-service, websocket-service, feedback-service, analytics-service
- **Componentes relacionados**: notification-service, sedes-service, tenant-service

---

## Objetivo

Gestionar el sistema de soporte al cliente: creación y atención de tickets de soporte, chat en tiempo real entre cliente y operador, tracking de SLA por ticket, feedback post-transacción, y dashboard NPS para tenant admin. Permite que clientes creen tickets, operadores los atiendan, y admins midan satisfacción.

---

## Tecnología

- **Runtime**: Python 3.11 + FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **DB**: PostgreSQL 15
- **Cache**: Redis (estados de ticket, presencia de chat)
- **Message Broker**: Kafka (eventos de tickets, notificaciones)
- **WebSocket**: Socket.io (chat real-time)
- **API**: REST + WebSocket

---

## Modelo de Datos

### Tabla: soporte_tickets

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
sede_id             UUID FK → sedes NOT NULL

numero_ticket        VARCHAR(20) NOT NULL  -- TK-YYYYMMDD-XXXX (único)

cliente_id          UUID FK → clientes NOT NULL
operador_id         UUID FK → usuarios (nullable)

categoria           VARCHAR(50) NOT NULL  -- problema_pago, incidencia_entrada_salida, consulta_factura, sugerencia, otro
titulo              VARCHAR(100) NOT NULL
descripcion          TEXT NOT NULL
prioridad           VARCHAR(10) DEFAULT 'media'  -- baja, media, alta

estado              VARCHAR(20) DEFAULT 'abierto'  -- abierto, respondio, en_proceso, resuelto, cerrado

fecha_limite_sla_primera_respuesta   TIMESTAMPTZ
fecha_limite_sla_resolucion          TIMESTAMPTZ
primera_respuesta_at                 TIMESTAMPTZ
resuelto_at                          TIMESTAMPTZ

sla_primera_respuesta_cumplido       BOOLEAN
sla_resolucion_cumplido              BOOLEAN

transaction_id        UUID FK → transacciones (nullable)  -- transacción relacionada
archivo_ids          UUID[] DEFAULT '{}'  -- archivos adjuntos

created_at           TIMESTAMPTZ DEFAULT NOW()
updated_at           TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: soporte_ticket_archivos

```sql
id                  UUID PK
ticket_id           UUID FK → soporte_tickets NOT NULL

nombre_original     VARCHAR(255) NOT NULL
storage_url         VARCHAR(500) NOT NULL
mime_type           VARCHAR(100)
tamano_bytes        INTEGER

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: soporte_ticket_mensajes

```sql
id                  UUID PK
ticket_id           UUID FK → soporte_tickets NOT NULL

tipo                VARCHAR(20) NOT NULL  -- texto, imagen, sistema
contenido           TEXT
imagen_url          VARCHAR(500)

emisor_tipo         VARCHAR(20) NOT NULL  -- cliente, operador, sistema
emisor_id           UUID NOT NULL

leido               BOOLEAN DEFAULT false
leido_at            TIMESTAMPTZ

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: soporte_ticket_auditoria

```sql
id                  UUID PK
ticket_id           UUID FK → soporte_tickets NOT NULL

accion              VARCHAR(50) NOT NULL  -- creado, respondido, estado_cambiado, asignado, fusionado, cerrado
detalle             JSONB DEFAULT '{}'

operador_id         UUID FK → usuarios (nullable)
ip_address          VARCHAR(45)

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: soporte_sla_metrics

```sql
id                  UUID PK
ticket_id           UUID FK → soporte_tickets NOT NULL

sla_estado          VARCHAR(20) DEFAULT 'dentro_sla'  -- dentro_sla, warning, critico, incumplido
porcentaje_tiempo_utilizado  INTEGER

tiempo_restante_primera_respuesta    INTERVAL
tiempo_restante_resolucion           INTERVAL

calculated_at       TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: intento_contacto

```sql
id                  UUID PK
moroso_id           UUID FK → morosos NOT NULL

tipo_contacto       VARCHAR(30) NOT NULL  -- llamada, visita, email, whatsapp
resultado           VARCHAR(50)  -- contesto, no_contesto, numero_errado, otro
notas               TEXT

operador_id         UUID FK → usuarios

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: feedback_transacciones

```sql
id                  UUID PK
tenant_id           UUID FK → tenants NOT NULL
transaccion_id      UUID FK → transacciones NOT NULL
cliente_id          UUID FK → clientes NOT NULL
sede_id             UUID FK → sedes NOT NULL

calificacion        INTEGER NOT NULL  -- 1-5 estrellas
comentario          TEXT

plataforma          VARCHAR(20) NOT NULL  -- push_notification, email, in_app
estado              VARCHAR(20) DEFAULT 'pendiente'  -- completado, pendiente, no_respondido

fecha_envio_solicitud   TIMESTAMPTZ
fecha_respuesta         TIMESTAMPTZ (nullable)

created_at          TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: cliente_nps

```sql
id                  UUID PK
cliente_id          UUID FK → clientes NOT NULL
tenant_id           UUID FK → tenants NOT NULL

NPS_actual          INTEGER  -- Score -100 a +100
total_respuestas    INTEGER DEFAULT 0
promotores          INTEGER DEFAULT 0
pasivos             INTEGER DEFAULT 0
detractores         INTEGER DEFAULT 0

ultima_actualizacion    TIMESTAMPTZ DEFAULT NOW()
```

### Tabla: sede_calificaciones

```sql
id                  UUID PK
sede_id             UUID FK → sedes NOT NULL

calificacion_promedio   DECIMAL(3,2)
total_respuestas       INTEGER
distribucion_estrellas  JSONB  -- { "1": 5, "2": 10, "3": 20, "4": 100, "5": 200 }

ultima_actualizacion    TIMESTAMPTZ DEFAULT NOW()
```

---

## Endpoints REST

### Tickets

```
POST   /api/v1/soporte/tickets                    Crear ticket
GET    /api/v1/soporte/tickets                    Listar tickets (filtros: sede, estado, prioridad)
GET    /api/v1/soporte/tickets/{ticket_id}        Detalle ticket
PATCH  /api/v1/soporte/tickets/{ticket_id}        Actualizar ticket
DELETE /api/v1/soporte/tickets/{ticket_id}        Eliminar ticket (solo admin)

POST   /api/v1/soporte/tickets/{ticket_id}/responder    Enviar respuesta
PATCH  /api/v1/soporte/tickets/{ticket_id}/estado       Cambiar estado
PATCH  /api/v1/soporte/tickets/{ticket_id}/asignar       Reasignar
POST   /api/v1/soporte/tickets/{ticket_id}/nota-interna  Agregar nota interna
POST   /api/v1/soporte/tickets/{ticket_id}/fusionar      Fusionar con otro

POST   /api/v1/soporte/tickets/{ticket_id}/archivos      Subir archivos adjuntos
GET    /api/v1/soporte/tickets/{ticket_id}/archivos      Listar adjuntos

GET    /api/v1/soporte/tickets/{ticket_id}/sla           Estado SLA del ticket
GET    /api/v1/soporte/tickets/{ticket_id}/chat/mensajes Historial chat
```

### Chat WebSocket

```
WebSocket /ws/soporte/tickets/{ticket_id}/chat    Conexión de chat en tiempo real
```

### SLA

```
GET    /api/v1/soporte/sla/dashboard             Dashboard NPS global y por sede
GET    /api/v1/soporte/sla/sedes/{sede_id}/detalle  Drill-down por sede
GET    /api/v1/soporte/sla/reportes/export       Exportar reporte SLA
```

### Feedback

```
POST   /api/v1/feedback/transacciones            Crear feedback (encuesta)
GET    /api/v1/feedback/transacciones/{transaccion_id}  Ver feedback de transacción
GET    /api/v1/feedback/transacciones/pendientes        Listar encuestas pendientes
POST   /api/v1/feedback/transacciones/{id}/reenviar      Reenviar solicitud
```

### Analytics NPS

```
GET    /api/v1/analytics/nps/dashboard           Dashboard NPS
GET    /api/v1/analytics/nps/sedes/{sede_id}/detalle  Detalle por sede
GET    /api/v1/analytics/feedbacks/negativos      Lista feedbacks negativos recientes
GET    /api/v1/analytics/nps/export               Exportar reporte NPS
```

---

## WebSocket Events (Chat)

### Cliente → Servidor

```json
{ "event": "message", "data": { "tipo": "texto|imagen", "contenido": "...", "imagen_url": "..." } }
{ "event": "typing_start" }
{ "event": "typing_stop" }
{ "event": "mark_read", "mensaje_id": "uuid" }
```

### Servidor → Cliente

```json
{ "event": "message", "data": { "mensaje_id": "...", "contenido": "...", "emisor": {...}, "timestamp": "..." } }
{ "event": "typing", "data": { "emisor_tipo": "operador", "nombre": "..." } }
{ "event": "ticket_updated", "data": { "estado": "respondido" } }
{ "event": "operator_joined", "data": { "operador_id": "...", "nombre": "..." } }
```

---

## SLA Configuration (Default)

| Prioridad | Primera Respuesta | Resolución |
|-----------|-------------------|------------|
| Alta     | 4 horas           | 24 horas   |
| Media    | 24 horas          | 72 horas   |
| Baja     | 72 horas          | 168 horas  |

---

## Eventos Kafka

### Topic: `parkcore.soporte`

```json
{
  "event_type": "ticket.created",
  "ticket_id": "uuid",
  "sede_id": "uuid",
  "cliente_id": "uuid",
  "timestamp": "2026-05-08T10:00:00Z",
  "data": { "numero_ticket": "TK-20260508-0001", "prioridad": "alta" }
}
```

Eventos:
- `ticket.created`, `ticket.respondido`, `ticket.resuelto`, `ticket.cerrado`
- `ticket.estado_changed`, `ticket.asignado`
- `sla_warning`, `sla_critical`, `sla_incumplido`
- `chat.message_sent`, `chat.message_delivered`
- `feedback.solicitado`, `feedback.recibido`
- `nps_actualizado`

---

## Rate Limiting

- Crear ticket: 10 por minuto por cliente
- Enviar mensajes chat: 30 por minuto
- Consultar dashboard SLA: 30 rpm
- Submit feedback: 5 por hora por cliente

---

## Dependencias

- **DB**: PostgreSQL `soporte` schema
- **Redis**: Cache de tickets, presencia WebSocket
- **Kafka**: Eventos de soporte
- **Notification-service**: Push/email de tickets
- **Feedback-service**: Datos de encuestas
- **Analytics-service**: Métricas NPS
- **Sedes-service**: Datos de sede para tickets

---

## Métricas

- `tickets_created_total{sede_id, categoria, prioridad}`
- `tickets_by_state{sede_id, estado}`
- `sla_compliance_rate{tenant_id, prioridad}`
- `chat_messages_total{ticket_id}`
- `chat_latency_ms`
- `feedback_response_rate`
- `nps_score{tenant_id, sede_id}`
- `avg_response_time_minutes{sede_id}`

---

## Health Check

```
GET /health → { "status": "ok", "db": "connected", "redis": "connected", "websocket": "active" }
GET /health/ready → verifica DB, Redis, WebSocket manager
GET /health/live → solo proceso activo
```

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|-----------------|
| Ticket sin transacción relacionada | categoria no puede ser "problema_pago" |
| Operador responde ticket ya cerrado | Error "Ticket cerrado, reabra para responder" |
| Cliente intenta crear ticket sin cuenta | 401 Unauthorized |
| Más de 3 imágenes en ticket | Rechazar 4ta+ con error |
| Chat > 100 mensajes | Paginación, últimos 50 + "Ver más" |
| SLA incumplido | Generar alerta, marcar en auditoría |
| Feedback duplicado misma transacción | Retornar feedback existente |
| Operador transfiere ticket | Notificar a cliente, nuevo operador hereda chat |

---

## Notas

- Número ticket: TK-YYYYMMDD-XXXX, secuencial por día empezando en 0001
- Chat sincronizado con fallback polling REST si WebSocket falla
- Tiempo real: < 1s de latencia de entrega
- Feedback solo se pide 1 vez por semana máximo por cliente
- SLA se calcula con timezone de la sede
- NPS = %Promotores (9-10) - %Detractores (0-6)
- Las alertas de SLA incumplido crean incidencia separada para auditoría