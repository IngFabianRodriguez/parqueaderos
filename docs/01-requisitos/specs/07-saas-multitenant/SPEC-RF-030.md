# SPEC-07-saas-multitenant-030 — El sistema debe generar, asignar y validar un slug único para cada tenant, as...

## Metadata
- **RF origen**: RF-030
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de un parqueadero **quiero** que mi cuenta tenga un slug único en la URL **para** que mis operadores y clientes accedan a través de `/app/{mi-parqueadero}`. ---

## Objetivo
El sistema debe generar, asignar y validar un slug único para cada tenant, asegurando que sea accesible en la ruta `/app/{slug}`, navegable desde cualquier navegador y utilizado como identificador público del tenant en la plataforma. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | slug | string | Slug único asignado (ej: `mi-parqueadero-a7b2`) | | tenant_id | UUID | Tenant asociado | | url_acceso | string | URL completa de acceso (`https://parkcore.app/app/mi-parqueadero-a7b2`) | | disponible | boolean | Indica si el slug estaba disponible antes de asignar | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | slug | string | Slug único asignado (ej: `mi-parqueadero-a7b2`) | | tenant_id | UUID | Tenant asociado | | url_acceso | string | URL completa de acceso (`https://parkcore.app/app/mi-parqueadero-a7b2`) | | disponible | boolean | Indica si el slug estaba disponible antes de asignar | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Todo tenant nuevo tiene exactamente un slug asignado en el momento de su creación. 2. El slug es único a nivel global en el sistema; no existen dos tenants con el mismo slug. 3. La ruta `/app/{slug}` responde con el dashboard del tenant correspondiente en menos de 500ms. 4. Un tenant en estado `trial` puede cambiar su slug una vez durante los 14 días. 5. Un tenant con estado `active` (suscrito) no puede cambiar su slug. 6. Los slugs no pueden contener espacios, caracteres especiales ni mayúsculas. 7. Los slugs deben tener entre 3 y 50 caracteres. 8. El sistema bloquea slugs que coincidan con palabras reservadas listadas. 9. Cada cambio de slug genera un evento `slug_changed` en la tabla de eventos. ---

## Endpoints
- `POST /api/v1/tenants` — Crear tenant con slug automático - `POST /api/v1/tenants/{tenant_id}/slug` — Actualizar slug (solo trial) - `GET /api/v1/slugs/check?slug={slug}` — Verificar disponibilidad de slug ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El slug funciona como identificador público del tenant. No debe confundirse con el `tenant_id` (UUID interno). - La normalización del nombre sigue rules: `Parqueadero Los Pinos` → `parqueadero-los-pinos-a7b2`. - Para tenants Enterprise con custom domain, el slug sigue existiendo pero el acceso primario es vía el dominio propio (ej: `miempresa.com` → slug `miempresa` reservado pero acceso por dominio). - El endpoint de verificación de disponibilidad debe ser público (no requiere auth) para permitir que el frontend valide en tiempo real mientras el usuario escribe.
