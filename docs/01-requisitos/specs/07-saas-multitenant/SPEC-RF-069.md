# SPEC-07-saas-multitenant-069 — El sistema debe permitir que el tenant_admin configure un mapeo entre los gru...

## Metadata
- **RF origen**: RF-069
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de un tenant Enterprise **quiero** que los grupos/roles que mis usuarios tienen en el IdP (Okta, Azure AD, Google Workspace) se traduzcan a los roles internos de ParkCore **para** que los permisos de acceso sean consistentes con lo que ya está definido en mi directorio corporativo. ---

## Objetivo
El sistema debe permitir que el tenant_admin configure un mapeo entre los grupos/roles recibidos en el SAML assertion (del IdP) y los roles internos del tenant en ParkCore. Cuando un usuario hace login via SSO, sus roles se determinan ejecutando este mapeo. La configuración es por IdP y se gestiona desde el admin panel del tenant. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | mapped_roles | array | Lista de roles de ParkCore asignados al usuario | | default_role_assigned | boolean | true si se usó el rol por defecto (ningún grupo tenía mapeo) | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | mapped_roles | array | Lista de roles de ParkCore asignados al usuario | | default_role_assigned | boolean | true si se usó el rol por defecto (ningún grupo tenía mapeo) | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El tenant_admin puede crear, editar y eliminar reglas de mapeo desde el admin panel. 2. Los grupos recibidos en el SAML assertion pueden incluir nombres con espacios, mayúsculas y caracteres especiales; el matching es case-insensitive y se normaliza. 3. Un usuario puede recibir múltiples roles si pertenece a múltiples grupos con mapeo. 4. Los cambios en el mapeo se aplican en el siguiente login SSO (no requieren logout inmediato). 5. El rol por defecto (`operator`) se asigna cuando ningún grupo tiene mapeo. 6. Si el `parkcore_role` no existe en el sistema, la configuración del mapeo se rechaza con error claro. 7. La configuración del mapeo es específica por IdP: el mismo grupo de Azure AD puede mapear a roles diferentes que el mismo grupo en Okta. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/sso/role-mappings` — Lista de mapeos configurados - `POST /api/v1/tenants/{tenant_id}/sso/role-mappings` — Crear nuevo mapeo - `PUT /api/v1/tenants/{tenant_id}/sso/role-mappings/{mapping_id}` — Actualizar mapeo - `DELETE /api/v1/tenants/{tenant_id}/sso/role-mappings/{mapping_id}` — Eliminar mapeo ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El rol asignado por mapeo SSO puede ser modificado por el tenant_admin manualmente después (RF-071). La próxima vez que el usuario haga login, el mapeo SSO se vuelve a aplicar y podría sobreescribir la asignación manual si el admin no ha configurado protección contra esto. Se recomienda documentar este comportamiento. - La normalización de nombres de grupo incluye: trim de espacios, conversión a lowercase, eliminación de acentos (para comparar "Gerência Financeira" con "gerencia financiera"). - Si el IdP soporta anidación de grupos (grupos dentro de grupos), se flattened y se incluyen todos los grupos ancestros en el assertion. - El campo `priority` permite que si un usuario tiene "Admin" (prioridad 1) y "Operator" (prioridad 2), se le asigne el rol de Admin si el mapeo de Admin tiene prioridad más alta. Sin embargo, el comportamiento recomendado es acumular roles, no reemplazar.
