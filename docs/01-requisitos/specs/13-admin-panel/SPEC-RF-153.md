# SPEC-13-admin-panel-153 — El panel de administración permite gestionar completamente las cuentas tenant...

## Metadata
- **RF origen**: RF-153
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** superadmin **quiero** crear, configurar y desactivar cuentas tenant **para** gestionar el ciclo de vida completo de los clientes del SaaS. ---

## Objetivo
El panel de administración permite gestionar completamente las cuentas tenant: crear nuevas cuentas con sus datos básicos, configurar plan y facturación, establecer límites de uso, y desactivar cuentas cuando sea necesario. Cada tenant opera de forma aislada con su propio slug, sedes, usuarios y datos. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El superadmin puede crear un tenant y este queda operativo en < 30 segundos. 2. El slug es único y se genera automáticamente en minúsculas sin espacios. 3. El trial expira automáticamente a los 14 días y se envía recordatorio 3 días antes. 4. Un tenant suspendido no puede recibir login de ningún usuario. 5. Cada cambio de plan queda registrado en auditoría con el valor anterior y nuevo. 6. Los límites configurados se aplican en tiempo real (no permite crear sede 6 si límite es 5). 7. El sistema envía email al admin principal en cada cambio de estado. ---

## Endpoints
- `POST /api/v1/admin/tenants` — Crear tenant - `GET /api/v1/admin/tenants` — Listar tenants (con filtros: estado, plan) - `GET /api/v1/admin/tenants/{id}` — Detalle de tenant - `PUT /api/v1/admin/tenants/{id}` — Actualizar tenant - `PUT /api/v1/admin/tenants/{id}/suspend` — Suspender - `PUT /api/v1/admin/tenants/{id}/reactivate` — Reactivar - `PUT /api/v1/admin/tenants/{id}/plan` — Cambiar plan ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El slug debe ser alphanumeric con guiones, sin espacios ni caracteres especiales. - Al crear un tenant en TRIAL, se debe crear automáticamente el admin con rol ADMIN_TENANT. - Los límites deben poder excederse temporalmente (grace period de 5%) para evitar bloquear por picos. - La facturación se maneja en el módulo de conciliación (RF-170+).
