# SPEC-08-082 — Configuración de Idioma y Zona Horaria

## Metadata
- **RF origen**: RF-082
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: config-service, tenant-service, i18n-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar el idioma y la zona horaria de mi organización **para** que todos los datos, notificaciones y reportes se muestren en el formato correcto según mi ubicación y región.

## Objetivo
El sistema debe permitir al `tenant_admin` configurar el idioma principal del sistema (es, en, pt) y la zona horaria (IANA timezone). Estos valores se aplican a todos los usuarios del tenant salvo que cada usuario tenga su propia preferencia.

## Comportamiento Específico

### Configuración por tenant
1. El admin accede a `Settings → Organization → Language & Timezone`.
2. Selecciona:
   - `language_code`: código ISO 639-1 (es, en, pt, fr, de).
   - `timezone`: zona horaria IANA (ej: America/Bogota, America/Sao_Paulo).
   - `date_format`: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD.
   - `time_format`: 12h, 24h.
   - `currency_format`: código de moneda (COP, USD, BRL).
3. Se guarda en `tenants.settings`.
4. Se publica evento `TENANT_SETTINGS_UPDATED`.

### Aplicación del idioma
1. Cada usuario recibe el idioma del tenant como default.
2. El usuario puede override su idioma personal en `users.preferences.language_code`.
3. Los textos de la interfaz (labels, mensajes, placeholders) se cargan del módulo i18n.
4. Los mensajes de notificación también usan el idioma del destinatario.

### Aplicación de zona horaria
1. Todas las marcas de tiempo se almacenan en UTC en la base de datos.
2. Al mostrar fechas/horas al usuario, se convierten a la zona horaria del tenant (o del usuario si está configurada).
3. Los reportes usan la zona horaria del tenant para agrupar datos por día.
4. Los eventos programados (batch notifications, jobs) se ejecutan en UTC pero se muestran en hora local del tenant.

## Criterios de Aceptación
1. El admin puede configurar idioma, zona horaria, formato de fecha y hora para el tenant.
2. El idioma se aplica a la interfaz, notificaciones y reportes.
3. Todas las marcas de tiempo se almacenan en UTC; se muestran en la zona horaria del tenant.
4. Cada usuario puede override el idioma con su preferencia personal.
5. Los formatos de fecha y moneda respetan la configuración regional.
6. Cambios en estos ajustes se reflejan en el siguiente login del usuario.

## Datos de Entrada
- `language_code` (string): Código ISO 639-1 (es, en, pt, fr, de).
- `timezone` (string): Zona horaria IANA (ej: America/Bogota).
- `date_format` (string): Formato de fecha — DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD.
- `time_format` (string): Formato de hora — 12h o 24h.
- `currency_format` (string): Código de moneda (COP, USD, BRL).
- `tenant_id` (UUID): Identificador del tenant whose settings are being updated.

## Datos de Salida
- `tenants.settings.language_code` (string): Idioma almacenado en la configuración del tenant.
- `tenants.settings.timezone` (string): Zona horaria almacenada.
- `tenants.settings.date_format`, `time_format`, `currency_format` (string): Formatos almacenados.
- `users.preferences.language_code` (string, opcional): Preferencia personal del usuario.
- Evento: `TENANT_SETTINGS_UPDATED` publicado tras el guardado.