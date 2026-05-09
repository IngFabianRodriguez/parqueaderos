# SPEC-13-admin-panel-151 — El panel de administración permite gestionar completamente el ciclo de vida d...

## Metadata
- **RF origen**: RF-151
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador del sistema **quiero** crear, editar y desactivar usuarios (operadores, supervisores, admins de sede) **para** mantener el control de acceso y la seguridad del sistema. ---

## Objetivo
El panel de administración permite gestionar completamente el ciclo de vida de los usuarios: crear cuentas con roles asignados, modificar sus datos y permisos, resetear contraseñas, y desactivar usuarios cuando dejan la organización. Todo con registro de auditoría de cada cambio. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | UUID | Identificador único | | nombre | String | Nombre completo | | email | String | Correo electrónico | | telefono | String | Teléfono | | rol | Enum | Rol asignado | | sede_ids | Array[UUID] | Sedes asignadas | | activo | Boolean | Si está activo | | fecha_creacion | DateTime | Cuándo fue creado | | ultimo_acceso | DateTime | Último login | | creado_por | UUID | Admin que lo creó | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | user_id | UUID | Identificador único | | nombre | String | Nombre completo | | email | String | Correo electrónico | | telefono | String | Teléfono | | rol | Enum | Rol asignado | | sede_ids | Array[UUID] | Sedes asignadas | | activo | Boolean | Si está activo | | fecha_creacion | DateTime | Cuándo fue creado | | ultimo_acceso | DateTime | Último login | | creado_por | UUID | Admin que lo creó | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El admin puede crear un usuario con rol OPERADOR y asignarlo a 1 o más sedes. 2. El admin puede cambiar el rol de un usuario existente. 3. Un usuario desactivado no puede iniciar sesión ni recibir tokens activos. 4. Cada acción de gestión de usuarios queda registrada en auditoría. 5. El sistema envía email de bienvenida al crear un nuevo usuario. 6. La búsqueda de usuarios devuelve resultados en < 500ms. 7. El admin no puede asignarse roles superiores al suyo. 8. Los campos de auditoría incluyen: quién, qué, cuándo (user_id, acción, timestamp). ---

## Endpoints
- `POST /api/v1/admin/users` — Crear usuario - `GET /api/v1/admin/users` — Listar usuarios (con filtros) - `GET /api/v1/admin/users/{id}` — Detalle de usuario - `PUT /api/v1/admin/users/{id}` — Actualizar usuario - `DELETE /api/v1/admin/users/{id}` — Desactivar usuario - `POST /api/v1/admin/users/{id}/reset-password` — Resetear contraseña ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los roles disponibles dependen del nivel del admin: Superadmin ve todos los roles, Admin tenant solo ve ADMIN_TENANT, SUPERVISOR, OPERADOR. - Los OPERADORES siempre deben tener al menos una sede asignada. - La contraseña temporal expira en 24 horas; el usuario debe cambiarla al primer login.
