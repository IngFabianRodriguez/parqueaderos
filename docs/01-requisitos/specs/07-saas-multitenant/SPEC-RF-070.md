# SPEC-07-saas-multitenant-070 — El sistema debe permitir que el `tenant_admin` cree usuarios dentro de su ten...

## Metadata
- **RF origen**: RF-070
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de un tenant **quiero** crear usuarios dentro de mi organización con roles específicos **para** permitir que mis empleados accedan al sistema según sus responsabilidades. ---

## Objetivo
El sistema debe permitir que el `tenant_admin` cree usuarios dentro de su tenant, asignándoles un rol específico (`tenant_admin`, `operator`, `viewer`). Cada usuario creado pertenece exclusivamente al tenant donde se crea y sus permisos están limitados por el rol asignado. ---

## Comportamiento Específico

### Happy Path
1. El `tenant_admin` accede a `Settings → Users → Add User`. 2. Completa el formulario: - `email`: dirección de correo del nuevo usuario. - `name`: nombre completo del usuario. - `role`: selección del rol (`tenant_admin`, `operator`, `viewer`). - `sites`: lista de sedes a las que tendrá acceso (solo para `operator` y `viewer`, opcional según configuración del tenant). 3. El sistema valida: - El email no esté en uso por un usuario activo en otro tenant. - El rol seleccionado exista. - Las sedes seleccionadas pertenezcan al tenant del admin. 4. Se crea el usuario en la tabla `users`: - `id`: UUID generado. - `tenant_id`: del admin que crea. - `email`, `name`: del formulario. - `auth_method`: `email_password`. - `status`: `pending_invitation`. - `created_at`: timestamp actual. - `created_by`: `user_id` del admin que crea. 5. Se inserta el rol en `user_roles`: `user_id`, `role`, `tenant_id`. 6. Si se seleccionaron sedes, se insertan en `user_site_access`: `user_id`, `site_id`. 7. Se genera un `invitation_token` (JWT de corta duración, 7 días) y se envía por email al usuario. 8. El usuario hace clic en el link del email, lo lleva a `GET /auth/invitation/{token}`. 9. El sistema valida el token y presenta un formulario para crear contraseña. 10. El usuario ingresa y confirma la contraseña. 11. El sistema actualiza: `password_hash`, `status = active`, `invitation_token = null`. 12. El usuario puede hacer login. ### Casos de creación por Superadmin - El superadmin puede crear usuarios en cualquier tenant via `POST /api/v1/admin/tenants/{tenant_id}/users`. - El flujo es el mismo, pero no se requiere ser `tenant_admin` del tenant destino. - El superadmin también puede especificar el `tenant_id` destino. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | uuid | ID del usuario creado | | email | string | Email del usuario | | name | string | Nombre del usuario | | role | string | Rol asignado | | status | string | Estado inicial: `pending_invitation` | | invitation_sent_at | timestamp | Timestamp del envío del email | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | uuid | ID del usuario creado | | email | string | Email del usuario | | name | string | Nombre del usuario | | role | string | Rol asignado | | status | string | Estado inicial: `pending_invitation` | | invitation_sent_at | timestamp | Timestamp del envío del email | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El `tenant_admin` puede crear usuarios con roles `operator` y `viewer` sin límite (sujeto al límite del plan). 2. El `tenant_admin` puede crear otros `tenant_admin` (mismo nivel), pero el sistema puede restringuirse por configuración del plan. 3. El usuario creado recibe un email de invitación antes de poder hacer login. 4. El usuario queda con estado `pending_invitation` hasta que complete el registro de contraseña. 5. La asignación de sites es opcional y solo aplica para roles `operator` y `viewer`. 6. El `tenant_admin` solo ve y puede crear usuarios de su propio tenant. 7. El superadmin puede crear usuarios en cualquier tenant. 8. El email de cada usuario es único en todo el sistema. ---

## Endpoints
- `POST /api/v1/tenants/{tenant_id}/users` — Crear usuario - `GET /api/v1/tenants/{tenant_id}/users` — Listar usuarios del tenant - `GET /api/v1/tenants/{tenant_id}/users/{user_id}` — Detalle de usuario - `PUT /api/v1/tenants/{tenant_id}/users/{user_id}` — Actualizar usuario - `DELETE /api/v1/tenants/{tenant_id}/users/{user_id}` — Eliminar usuario - `POST /api/v1/users/{user_id}/resend-invitation` — Reenviar invitación - `GET /auth/invitation/{token}` — Página de aceptación de invitación ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Un usuario pertenece a un solo tenant. No existe un usuario "global" excepto el superadmin. - La invitación expira en 7 días; después de eso, el admin puede reenviar una nueva invitación. - El password del usuario debe cumplir con la política de passwords del sistema (min 8 caracteres, al menos una mayúscula, un número). - Si el tenant tiene SSO habilitado, los usuarios pueden ser creados también via JIT (RF-068); los usuarios creados manualmente tienen `auth_method = email_password`.
