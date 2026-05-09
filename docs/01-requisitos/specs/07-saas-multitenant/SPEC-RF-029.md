# SPEC-07-saas-multitenant-029 — El sistema debe permitir la creación de una nueva cuenta tenant con datos bás...

## Metadata
- **RF origen**: RF-029
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** fundador o administrador de un parqueadero **quiero** registrar una nueva cuenta en la plataforma **para** comenzar a gestionar mi negocio con una пробная period. ---

## Objetivo
El sistema debe permitir la creación de una nueva cuenta tenant con datos básicos de la empresa, generando automáticamente un ambiente aislado y comenzando el periodo de prueba de 14 días sin cobro. ---

## Comportamiento Específico

### Happy Path
1. El usuario accede a la página de registro (`/register`) e ingresa: nombre de la empresa, nombre del fundador, email, contraseña, NIT de la empresa. 2. El sistema valida que el email no esté en uso por otro tenant. 3. El sistema valida que el NIT no esté en uso por otro tenant. 4. El sistema genera un slug a partir del nombre de la empresa (primera palabra + random de 4 caracteres alfanuméricos). Si el slug ya existe, se genera uno alternativo con sufijos numéricos (`-2`, `-3`). 5. El sistema crea el registro del tenant con: `tenant_id` (UUID), `name`, `slug`, `founder_email`, `nit`, `status = 'trial'`, `trial_start_date = NOW()`, `trial_end_date = NOW() + 14 días`. 6. El sistema crea el usuario fundador con email verificado = false, rol `tenant_admin`, `tenant_id` asignado. 7. El sistema encripta la contraseña con bcrypt (cost 12) y la almacena. 8. El sistema envía email de bienvenida con enlace de verificación de email. 9. El sistema genera la sesión JWT y redirige al onboarding wizard. 10. El sistema registra el evento `tenant_created` con `tenant_id`, timestamp y plan inicial estimado (`trial`). ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | tenant_id | UUID | Identificador único del tenant | | slug | string | Slug único para acceso (`/app/{slug}`) | | status | enum | Estado inicial del tenant (`trial`) | | trial_end_date | datetime | Fecha de fin del periodo de prueba | | usuario_fundador_id | UUID | ID del usuario creado con rol tenant_admin | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | tenant_id | UUID | Identificador único del tenant | | slug | string | Slug único para acceso (`/app/{slug}`) | | status | enum | Estado inicial del tenant (`trial`) | | trial_end_date | datetime | Fecha de fin del periodo de prueba | | usuario_fundador_id | UUID | ID del usuario creado con rol tenant_admin | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Un nuevo tenant se crea en la base de datos en menos de 3 segundos. 2. El slug generado es único y accesible desde `/app/{slug}`. 3. El tenant inicia con estado `trial` y `trial_end_date` exactamente 14 días en el futuro. 4. El usuario fundador recibe rol `tenant_admin` sin necesidad de confirmación adicional. 5. El email de bienvenida se envía dentro de los 30 segundos posteriores a la creación. 6. No es posible crear un tenant con un email ya existente en el sistema. 7. La contraseña se almacena encriptada con bcrypt (cost 12); nunca se almacena en texto plano. 8. El evento `tenant_created` se registra en la tabla de eventos SaaS al finalizar la creación. ---

## Endpoints
- `POST /api/v1/tenants` — Crear nuevo tenant - `POST /api/v1/auth/register` — Registrar usuario fundador (interno, parte del flujo) ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El slug se genera automáticamente pero se permite al usuario sobrescribirlo antes de confirmar el registro. - Los primeros 5 slugs alternativos se generan automáticamente; si todos existen, se muestra un input para que el usuario elija manualmente. - El periodo trial de 14 días comienza desde `NOW()` (fecha del registro), no desde la verificación del email. - La tabla `tenants` incluye campos de dirección, ciudad y país que pueden ser completados durante el onboarding.
