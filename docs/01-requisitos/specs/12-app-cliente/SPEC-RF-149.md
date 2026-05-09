# SPEC-12-app-cliente-149 — El sistema debe permitir al cliente configurar sus preferencias de notificaci...

## Metadata
- **RF origen**: RF-149
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** configurar qué notificaciones quiero recibir y por qué canal (push, SMS o email) **para** controlar la comunicación y recibir solo la información que me interesa. ---

## Objetivo
El sistema debe permitir al cliente configurar sus preferencias de notificación desde la app. El cliente puede habilitar o deshabilitar tipos específicos de notificaciones y elegir el canal preferido para cada una. ---

## Comportamiento Específico

### Happy Path
1. El cliente accede a "Mi Cuenta" → "Configuración de Notificaciones". 2. El sistema muestra las categorías de notificaciones disponibles y el estado actual de cada una. 3. El cliente puede togglear cada notificación entre habilitada/deshabilitada. 4. Para cada notificación habilitada, el cliente puede seleccionar el canal preferido: - Push (requiere tener la app instalada y notificaciones habilitadas en el SO) - SMS (requiere número de teléfono verificado) - Email (requiere email verificado) 5. El cliente puede seleccionar múltiples canales para una misma notificación. 6. El cliente también ve las opciones de "idioma de notificaciones" y "horario静音" (no molestar). 7. Al guardar, el sistema actualiza las preferencias y muestra confirmación. 8. Si el cliente deshabilita todos los canales de una notificación, esa notificación deja de envíosarse. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | preferencias_id | UUID | Identificador del registro de preferencias | | cliente_id | UUID | ID del cliente | | notificaciones | array | Lista de preferencias por tipo | | habilitada | boolean | Estado general de notificaciones push | | canales_configurados | array | Canales disponibles y verificados para el cliente | | fecha_actualizacion | timestamp | Última modificación | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | preferencias_id | UUID | Identificador del registro de preferencias | | cliente_id | UUID | ID del cliente | | notificaciones | array | Lista de preferencias por tipo | | habilitada | boolean | Estado general de notificaciones push | | canales_configurados | array | Canales disponibles y verificados para el cliente | | fecha_actualizacion | timestamp | Última modificación | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede habilitar/deshabilitar cada tipo de notificación individualmente. 2. El cliente puede elegir uno o más canales (push/SMS/email) para cada notificación. 3. Los canales no verificados se muestran bloqueados con opción de verificar. 4. El cliente puede configurar un horario de no molestar. 5. Los cambios en preferencias se aplican inmediatamente (no requieren re-login). 6. El cliente recibe solo las notificaciones que ha habilitado. 7. Se muestra el estado actual de cada canal (verificado/no verificado). ---

## Endpoints
- `GET /api/v1/cliente/config/notificaciones` — Obtiene las preferencias del cliente - `PUT /api/v1/cliente/config/notificaciones` — Actualiza las preferencias - `POST /api/v1/cliente/verificar/email` — Envía email de verificación - `POST /api/v1/cliente/verificar/telefono` — Envía SMS de verificación ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Las notificaciones críticas de seguridad (ej: vehículo bloqueado) se envían por todos los canales disponibles independientemente de las preferencias. - El horario de silencio (no molestar) se evalúa en el momento del envío; si la notificación es crítica, se envía de todas formas. - La preferencia de idioma de notificaciones puede diferir del idioma de la app.
