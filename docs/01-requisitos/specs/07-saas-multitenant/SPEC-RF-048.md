# SPEC-07-048 — Aplicación de Branding del Tenant en Emails Transaccionales

## Metadata
- **RF origen**: RF-048
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: notification-service, branding-service, tenant-service, email-service

---

## User Story
**Como** operador/administrador de un tenant **quiero** que los emails enviados por ParkCore (notificaciones de entrada/salida, facturas, alertas) muestren mi logo y colores **para** que los destinatarios perciban la comunicación como oficial de mi empresa.

## Objetivo
El sistema debe inyectar automáticamente el branding del tenant (logo, colores, email_remitente) en todos los emails transaccionales que se originen desde el tenant, incluyendo el email Remitente (from address), el logo en el header, los colores en los botones y el pie de página.

## Comportamiento Específico

### Happy Path
1. Un evento del sistema dispara el envío de un email transaccional (ej: `invoice.created`, `vehicle.entered`, `payment.confirmed`)
2. El `notification-service` recibe el evento con `tenant_id`, `template_name`, `recipient_email`, `template_data`
3. El servicio consulta branding y notification-channels del tenant
4. El sistema procesa la plantilla del email: reemplaza variables, inyecta logo, aplica colores, genera footer
5. El `from_address` se configura como: `{tenant_display_name} <{tenant_email_slug}@parkcore.co>` o custom domain si está configurado (RF-049)
6. El email se envía via email provider con tracking de apertura y clicks
7. Se genera evento `email_sent`

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tenant no tiene branding | Usar default ParkCore; email se envía normalmente |
| Logo no carga en el email | Mostrar texto con nombre del tenant como fallback; no bloquear envío |
| Custom domain configurado | Usar `notificaciones@{custom_domain}` como from address |
| Email provider falla | Guardar email en cola para reintento; generar evento `email_failed` |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| template_name | string | Nombre de la plantilla (invoice, entry_notification, etc.) | Sí |
| recipient_email | string | Email del destinatario | Sí |
| template_data | object | Datos para interpolar en la plantilla | Sí |
| from_address_override | string | Sobrescribir from address (solo para emails críticos) | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| email_id | string | ID del email enviado (del provider) |
| from_address | string | Address de remitente usado |
| logo_url | string | URL del logo inyectado |
| delivered_at | datetime | Timestamp de envío |
| open_tracked | boolean | Si el email tiene tracking de apertura |
| click_tracked | boolean | Si el email tiene tracking de clicks |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todos los emails transaccionales llevan el logo del tenant en el header
2. El `from_address` de los emails muestra el nombre del tenant, no "ParkCore" genérico
3. Los botones de los emails usan el `primary_color` del tenant
4. El footer del email muestra el nombre y datos de la empresa del tenant
5. Si el tenant tiene custom domain, el from address usa ese dominio

## Endpoints
- `POST /api/v1/notifications/email` — Enviar email transaccional con branding
- `GET /api/v1/tenants/{tenant_id}/branding` — Obtener branding para inyección
- `GET /api/v1/tenants/{tenant_id}/notification-channels` — Obtener from address

## Health Check
- `GET /health` → { "status": "ok" }
