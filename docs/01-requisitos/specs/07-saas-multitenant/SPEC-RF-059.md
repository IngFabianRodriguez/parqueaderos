# SPEC-07-059 — Wizard de Onboarding para Nuevo Tenant

## Metadata
- **RF origen**: RF-059
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: onboarding-service, tenant-service, notification-service

---

## User Story
**Como** nuevo usuario de ParkCore **quiero** que el sistema me guíe paso a paso en la configuración inicial de mi cuenta **para** tener mi parqueadero funcionando rápidamente sin necesidad de leer documentación.

## Objetivo
El sistema debe presentar un wizard de onboarding que guíe al nuevo tenant a través de los pasos esenciales para configurar su cuenta: datos de la empresa, creación de la primera sede, definición de zonas y espacios, configuración de la primera talanquera, e invitación del equipo.

## Comportamiento Específico

### Flujo del Wizard (6 Pasos)

**Paso 1: Datos de la Empresa**
- Nombre de la empresa, NIT, Dirección, Ciudad, Teléfono, Sector
- Se guarda en `tenants`; avanza al paso 2

**Paso 2: Tu Primera Sede**
- Nombre de la sede, Dirección, Ciudad, Horario de operación, Modo de operación (`iot` o `manual`)
- Si modo `iot`: sección adicional para talanqueras (opcional, se puede hacer después)
- Se crea la sede en `sedes`

**Paso 3: Zonas y Espacios**
- Templates predefinidos (RF-062): Básico (1 zona, 20 espacios), Profesional (2 zonas, 40), Corporativo (3 zonas, 80), Aeropuerto/Centro Comercial (4 zonas, 200), Empezar desde cero
- El usuario selecciona un template o crea manualmente
- Se crean zonas y espacios en `zonas` y `espacios`

**Paso 4: Configuración de Talanqueras (solo modo IoT)**
- Si se eligió modo `iot`: añadir talanqueras con nombre, tipo (entrada/salida), IP del dispositivo
- Puede saltar este paso y hacerlo después desde el admin

**Paso 5: Tarifa Inicial**
- Sugerencia según sector: Por hora, Tarifa nocturna, Tarifa mensual, Fracción mínima (15 min)
- Se crea la tarifa en `tarifas`

**Paso 6: Invitar al Equipo**
- Invitar hasta 3 usuarios (email, rol: manager/operador) o omitir
- Si invita: se envía email de invitación (RF-033)
- Sistema marca `onboarding_completed_at = NOW()`; `onboarding_status = completed`
- Redirige al dashboard del tenant

### Progreso Automático
- El progreso se guarda automáticamente en cada paso
- Si el usuario cierra la sesión y vuelve, el wizard se reanuda desde donde quedó
- Email de recordatorio a las 48h si el onboarding no se completa

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Usuario cierra el navegador durante el wizard | El progreso se guarda automáticamente; al volver, se reanuda |
| Error de validación en un paso | Se muestra mensaje inline en el campo; no se avanza |
| El usuario abandona el wizard | Se envía email recordatorio en 48h; estado `onboarding_pending` |
| NIT duplicado en el sistema | Rechazar con mensaje "Este NIT ya está registrado" |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El wizard guía al usuario a través de los 6 pasos en orden, sin poder saltar pasos (excepto talanqueras si modo manual)
2. El progreso se guarda automáticamente al completar cada paso
3. Si el usuario regresa a la plataforma, el wizard se reanuda desde el último paso completado
4. Al completar el wizard, el tenant tiene: 1 sede, 1 zona, 1 espacio, 1 tarifa
5. Si el onboarding no se completa en 48 horas, se envía email recordatorio

## Endpoints
- `POST /api/v1/onboarding/step/{step}` — Guardar progreso de un paso
- `GET /api/v1/onboarding/status` — Consultar estado del onboarding
- `POST /api/v1/tenants/{tenant_id}/sedes` — Crear primera sede
- `POST /api/v1/tenants/{tenant_id}/zonas` — Crear zonas

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| step | integer | Número del paso (1-6) | Sí |
| tenant_id | UUID | Identificador del tenant | Sí |
| company_name | string | Nombre de la empresa | Sí (paso 1) |
| nit | string | NIT de la empresa | Sí (paso 1) |
| address | string | Dirección de la empresa | Sí (paso 1) |
| city | string | Ciudad de la empresa | Sí (paso 1) |
| sector | string | Sector/industria | No (paso 1) |
| sede_name | string | Nombre de la primera sede | Sí (paso 2) |
| sede_address | string | Dirección de la sede | Sí (paso 2) |
| operation_mode | string | `iot` o `manual` | Sí (paso 2) |
| template_id | string | ID del template seleccionado | Sí (paso 3) |
| tariff_name | string | Nombre de la tarifa inicial | Sí (paso 5) |
| tariff_type | string | `por_hora`, `nocturna`, `mensual`, `fraccion` | Sí (paso 5) |
| tariff_price | decimal | Precio de la tarifa | Sí (paso 5) |
| invited_emails | array[string] | Emails de usuarios a invitar (máx 3) | No (paso 6) |
| invited_roles | array[string] | Roles de los invitados (`manager`, `operador`) | No (paso 6) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| step | integer | Paso completado |
| progress | object | Resumen del progreso: `completed_steps`, `current_step`, `percent_complete` |
| tenant_id | UUID | Identificador del tenant |
| sede_id | UUID | ID de la sede creada (disponible después paso 2) |
| onboarding_status | string | `in_progress`, `completed`, `pending` |
| completed_at | datetime | Timestamp de finalización (null si no completado) |

## Health Check
- `GET /health` → { "status": "ok" }
