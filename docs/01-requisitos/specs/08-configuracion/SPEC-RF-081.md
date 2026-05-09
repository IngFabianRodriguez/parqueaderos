# SPEC-08-081 — Configuración de Tema (Modo Claro/Oscuro)

## Metadata
- **RF origen**: RF-081
- **Módulo**: 08-config-svc
- **Prioridad**: Baja
- **Servicios**: config-service, tenant-service, admin-panel

---

## User Story
**Como** administrador de un tenant **quiero** elegir entre modo claro y modo oscuro para la interfaz del panel de administración **para** reducir la fatiga visual yadaptar la experiencia a las preferencias del equipo.

## Objetivo
El sistema debe permitir al `tenant_admin` seleccionar el tema visual del admin panel: modo claro (light) o modo oscuro (dark). La preferencia se almacena por usuario en `users.preferences` y por tenant en `tenants.settings`.

## Comportamiento Específico

### Configuración del tema
1. El admin accede a `Settings → Appearance → Theme`.
2. Selecciona: `System` (sigue la preferencia del OS), `Light`, o `Dark`.
3. Al guardar, el sistema actualiza `users.preferences.theme = 'light'|'dark'|'system'`.
4. El admin panel aplica el tema inmediatamente sin recargar la página.

### Aplicación del tema
1. Al cargar el admin panel, el frontend consulta `users.preferences.theme`.
2. Si es `system`: consulta `prefers-color-scheme` del navegador.
3. Aplica la hoja de estilos correspondiente (CSS variables para colores).
4. El tema se mantiene en localStorage para sesiones sin auth.

### Roles con acceso
- Todo usuario puede elegir su tema personal.
- El `tenant_admin` puede establecer el tema por defecto del tenant.

## Criterios de Aceptación
1. El usuario puede elegir entre Light, Dark o System.
2. El tema se aplica inmediatamente sin recargar la página.
3. La preferencia se guarda en la cuenta del usuario y persiste entre dispositivos.
4. El `tenant_admin` puede establecer un tema por defecto para todo el tenant.
5. Si el tema es `system`, se respetan las preferencias del OS del usuario.