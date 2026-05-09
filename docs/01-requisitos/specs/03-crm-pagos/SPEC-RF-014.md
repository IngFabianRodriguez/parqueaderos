# SPEC-03-014 — Enviar notificaciones push/SMS/email al cliente

## Metadata
- **RF origen**: RF-014
- **Módulo**: 03-crm-pagos
- **Prioridad**: Media
- **Servicios**: notification-service, crm-service

---

## User Story
Como Sistema **quiero** notificar al cliente en eventos clave de su sesión de parqueo (entrada, salida, recordatorio, pago) **para** mejorar su experiencia, reducir consultas al operador y mantenerlo informado de su actividad.

## Objetivo
Enviar notificaciones al cliente a través de múltiples canales (push notification, SMS, email) activadas por eventos del sistema. Las notificaciones son configurables por el tenant_admin: se puede activar/desactivar cada tipo, definir templates personalizados, y elegir el canal preferido por cliente.

## Comportamiento Específico
### Happy Path (Notificación por entrada)
1. Sistema detecta vehículo entra (RF-005)
2. Notification-service recibe evento `vehiculo.ingresado`
3. Sistema obtiene cliente asociado a la placa
4. Sistema consulta preferencias del cliente (canales activos)
5. Sistema renderiza template de notificación de entrada con datos dinámicos (sede, hora, plaza)
6. Sistema envía por el canal preferido (push → SMS → email en fallback)
7. Registro de envío guardado

### Happy Path (Notificación por salida/pago)
1. Sistema detecta sesión pagada (RF-011)
2. Notification-service recibe evento `sesion.pagada`
3. Genera notificación con: sede, monto pagado, tiempo de estadía
4. Incluye link a factura (RF-012) y opción de dejar opinión

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Cliente sin email ni teléfono | Notificación no enviada. Sesión continúa normal. Se loguea como "no contactable" |
| Push no enviado (Firebase down) | Sistema detecta vía callback de entrega. Reintenta por SMS si disponible |
| SMS gateway returns error | Retry 3 veces con backoff 30s, luego fallback email |
| Template con variable faltante | Renderiza el campo vacío, no falla. Loguea warning |
| Cliente con Opt-out explícito | Sistema no envía por ese canal. No se cuenta como falla |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| cliente_id | UUID | Destinatario | Sí |
| tipo_notificacion | VARCHAR | entrada, salida, recordatorio, alerta, bienvenida, encuesta | Sí |
| canal | VARCHAR | push, sms, email (null = todos activos) | No |
| template_id | UUID | Template a usar (null = default) | No |
| datos_contexto | JSON | placa, sede, monto, etc. para renderizar template | Sí |
| enviada_por | UUID | Operador si es manual | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| notificacion_id | UUID | — |
| cliente_id | UUID | — |
| canal | VARCHAR | — |
| estado | VARCHAR | enviada, fallida, recibida, abierta |
| timestamp_envio | TIMESTAMP | — |
| timestamp_recibida | TIMESTAMP | — |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todas las notificaciones se registran en tabla `notificacion` con estado
2. Push notifications deliveradas < 5s después del evento en condiciones normales
3. Un solo envío por canal activo por notificación (no duplicar si cliente tiene múltiples dispositivos)
4. Cliente puede desuscribirse de cualquier canal sin afectar otros

## Endpoints
- `POST /api/v1/notificaciones` — Enviar notificación (manual o desde evento)
- `GET /api/v1/notificaciones/cliente/{cliente_id}` — Historial de notificaciones del cliente
- `PUT /api/v1/notificaciones/preferencias` — Actualizar preferencias de un cliente
- `POST /api/v1/notificaciones/unsubscribe/{token}` — Desuscribirse via link en email

## Health Check
- `GET /health` → `{ "status": "ok", "service": "notification-service" }`

## Notas
- Push: Firebase Cloud Messaging (FCM) para Android, APNs para iOS.
- SMS gateway: configurable (Twilio, Nexmo, o proveedores locales).
- Notificaciones transaccionales (entrada, salida, pago) no requieren opt-out.
- Recordatorios de prepago: se envían 15 min y 5 min antes de expirar el tiempo comprado.