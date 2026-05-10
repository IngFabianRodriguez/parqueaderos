# SPEC-08-088 — Configuración de Notificaciones y Plantillas de Comunicación

## Metadata
- **RF origen**: RF-088
- **Módulo**: 08-config-svc
- **Prioridad**: Media
- **Servicios**: notification-service, config-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** personalizar las plantillas de notificación que el sistema envía a mis clientes **para** mantener mi marca y comunicar información relevante de mi organización.

## Objetivo
El sistema debe permitir al `tenant_admin` personalizar las plantillas de email, SMS y push notifications. Las plantillas usan variables (placeholders) que se reemplazan en tiempo de ejecución. El admin puede activar/desactivar cada notificación y modificar el contenido manteniendo las variables requeridas.

## Comportamiento Específico

### Categorías de notificaciones
- **Transaccionales**: ingreso, egreso, pago, factura.
- **Administrativas**: alertas de caja, reportes programados.
- **Marketing**: promociones, encuestas (si aplica).

### Estructura de una plantilla
- `template_name`: identificador interno (ej: `entry_confirmation`).
- `channel`: `email`, `sms`, `push`, `in_app`.
- `subject` (solo email): asunto del mensaje.
- `body`: cuerpo del mensaje con placeholders `{{variable}}`.
- `is_active`: booleano.
- `footer`: pie de página (configurable por el admin).
- `language_code`: código ISO 639-1 (plantilla por idioma).

### Variables disponibles
- `{{customer_name}}`, `{{vehicle_plate}}`, `{{venue_name}}`, `{{entry_time}}`, `{{exit_time}}`, `{{amount}}`, `{{currency}}`, `{{ticket_number}}`, `{{company_name}}`.

### Validación al guardar
1. Todas las variables usadas en el body existen en el catálogo.
2. El body no está vacío.
3. El subject (si aplica) tiene entre 3 y 100 caracteres.
4. El body no excede: 10,000 caracteres (email), 1,600 caracteres (SMS).

### Eventos
- Se publica `NOTIFICATION_TEMPLATES_UPDATED` tras cada guardado.
- Las notificaciones futuras usan las nuevas plantillas.

## Criterios de Aceptación
1. El admin puede ver y editar todas las plantillas de notificación de su tenant.
2. Cada plantilla tiene variables que se reemplazan en tiempo de ejecución.
3. Las plantillas pueden estar activas o inactivas; las inactivas no se envían.
4. Las variables no reconocidas se detectan en la validación y se rechazan.
5. Existe una plantilla por defecto en español (`es`) como fallback.
6. Los cambios se reflejan en las siguientes notificaciones; las ya enviadas no se modifican.

## Datos de Entrada
- `tenant_id` (UUID): Identificador del tenant.
- `template_name` (string): Identificador interno (ej: entry_confirmation).
- `channel` (string): Canal — `email`, `sms`, `push`, `in_app`.
- `subject` (string, solo email): Asunto del mensaje (3-100 caracteres).
- `body` (string): Cuerpo del mensaje con placeholders `{{variable}}` (máx 10,000 email, 1,600 SMS).
- `is_active` (boolean): Si la plantilla está activa.
- `footer` (string): Pie de página configurable.
- `language_code` (string): Código ISO 639-1 para la plantilla.

## Datos de Salida
- `notification_templates.id` (UUID): ID de la plantilla.
- `notification_templates.tenant_id`, `template_name`, `channel`, `subject`, `body` (mixed): Datos almacenados.
- `notification_templates.is_active`, `footer`, `language_code` (mixed): Estado y configuración.
- `template_validation` (object): Resultado de la validación — variables reconocidas, errores.
- Evento: `NOTIFICATION_TEMPLATES_UPDATED` publicado tras el guardado.