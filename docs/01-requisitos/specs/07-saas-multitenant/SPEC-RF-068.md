# SPEC-07-saas-multitenant-068 — Cuando un usuario se autentica vía SAML 2

## Metadata
- **RF origen**: RF-068
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de un tenant Enterprise **quiero** que cuando un usuario se autentique por primera vez via SSO, el sistema lo cree automáticamente en mi organización con los roles correspondientes **para** no tener que crear manualmente cada usuario antes de que pueda acceder. ---

## Objetivo
Cuando un usuario se autentica vía SAML 2.0 (RF-067) y su cuenta no existe aún en ParkCore, el sistema debe crearla automáticamente en el tenant correspondiente usando los atributos del SAML assertion. El usuario queda provisioning sin intervención del admin del tenant. Los roles se asignan según el mapeo configurado (RF-069). ---

## Comportamiento Específico

### Happy Path
1. El usuario completa el flujo SSO y el auth-service obtiene el SAML assertion válido (RF-067, pasos 1-8). 2. El auth-service extrae: `NameID`, `email`, `first_name`, `last_name`, `groups` (si existen). 3. El auth-service busca el usuario por `email` o `saml_name_id` en la tabla `users`: - Si existe: actualizar `last_login` y continuar con la sesión (no es JIT, es login normal). - Si no existe: continuar con el flujo de provisioning. 4. Validar que `email` esté presente y tenga formato válido. 5. Validar que el dominio del email pertenezca al tenant (protección anti-squatting): - Obtener los dominios autorizados del tenant desde `tenant_domains`. - Si el dominio del email no está en la lista, rechazar el login. 6. Crear el usuario: - `id`: UUID generado. - `tenant_id`: del tenant que hizo el request SSO. - `email`: del assertion. - `name`: `first_name` + `last_name` del assertion. - `saml_name_id`: valor del `NameID` del assertion (para futura búsqueda). - `auth_method`: `saml`. - `idp_provider`: nombre del IdP (Okta, Azure AD, etc.). - `is_active`: `true`. - `created_at`: timestamp actual. - `created_via`: `jit_provisioning`. 7. Determinar los roles iniciales: - Consultar el mapeo de grupos del IdP a roles del tenant (RF-069). - Si el usuario tiene grupos que mapean a roles, asignar esos roles en `user_roles`. - Si no hay mapeo o ningún grupo coincide: asignar el rol `operator` por defecto (configurable por el tenant). 8. Registrar el evento de provisioning en `audit_log`: usuario creado, tenant, IdP, timestamp. 9. Crear la sesión JWT y completar el flujo de login. ### Asignación de roles por defecto Si el IdP no provee grupos/roles, el usuario recibe: - `role`: `operator` - `level`: `site_based` - Acceso仅限于: operaciones normales dentro del tenant. El admin del tenant puede cambiar el rol después desde el admin panel. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | uuid | ID del usuario recién creado | | email | string | Email del usuario | | roles | array | Roles asignados | | created_via | string | Indica que fue creado via JIT | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | uuid | ID del usuario recién creado | | email | string | Email del usuario | | roles | array | Roles asignados | | created_via | string | Indica que fue creado via JIT | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. La primera vez que un usuario de un IdP hace login via SSO, su cuenta se crea automáticamente en el tenant de ParkCore. 2. Los datos del usuario (`email`, `name`) se completan con los atributos del SAML assertion. 3. El `saml_name_id` se guarda para identificar al usuario en futuras sesiones SSO. 4. Los roles se asignan según el mapeo del IdP (RF-069); si no hay mapeo, se usa el rol por defecto. 5. El JIT provisioning solo ocurre si está habilitado en la configuración del IdP del tenant. 6. El dominio del email del usuario debe estar en la lista de dominios autorizados del tenant. 7. El evento de creación via JIT queda registrado en el audit log. 8. El usuario puede hacer login inmediatamente después de ser creado, sin intervención del admin. ---

## Endpoints
- No hay endpoints REST nuevos específicos para JIT; el flujo está embebido en el proceso de autenticación SSO (RF-067). - `GET /api/v1/admin/users` — El admin del tenant puede ver los usuarios creados via JIT y modificar sus roles. - `DELETE /api/v1/admin/users/{id}` — El admin puede eliminar usuarios creados via JIT. ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El JIT provisioning solo aplica para SSO; los usuarios creados por email/password no usan este flujo. - El campo `created_via = 'jit_provisioning'` permite al admin identificar fácilmente los usuarios creados automáticamente. - Se recomienda que el admin del tenant revise periódicamente los usuarios creados via JIT para confirmar que los roles asignados son correctos. - Si el tenant deshabilita el SSO después de que usuarios fueron creados via JIT, esos usuarios retain sus cuentas y roles; pueden hacer login con email/password si el tenant tiene ese método habilitado. - El campo `saml_name_id` debe ser único por IdP; el mismo NameID de un IdP diferente puede existir para otro IdP (son de diferentes dominios).
