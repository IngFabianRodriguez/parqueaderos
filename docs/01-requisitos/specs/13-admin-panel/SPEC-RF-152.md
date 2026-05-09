# SPEC-13-admin-panel-152 — El sistema implementa Role-Based Access Control (RBAC) donde los roles define...

## Metadata
- **RF origen**: RF-152
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** superadmin **quiero** definir roles con permisos específicos y asignarlos a usuarios **para** garantizar que cada persona tenga acceso solo a lo que necesita. ---

## Objetivo
El sistema implementa Role-Based Access Control (RBAC) donde los roles definen qué acciones puede realizar cada usuario. El superadmin puede crear roles personalizados, asignar permisos granulares, y los admin de tenant pueden asignar roles predefinidos a sus usuarios. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | rol_id | UUID | Identificador único | | nombre | String | Nombre del rol | | descripcion | String | Descripción | | permisos | Array[String] | Lista de permisos | | es_sistema | Boolean | Si es rol predefinido (no editable) | | fecha_creacion | DateTime | Cuándo se creó | | usuarios_count | Integer | Cuántos usuarios tienen este rol | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | rol_id | UUID | Identificador único | | nombre | String | Nombre del rol | | descripcion | String | Descripción | | permisos | Array[String] | Lista de permisos | | es_sistema | Boolean | Si es rol predefinido (no editable) | | fecha_creacion | DateTime | Cuándo se creó | | usuarios_count | Integer | Cuántos usuarios tienen este rol | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El superadmin puede crear roles con cualquier combinación de permisos. 2. Los roles predefinidos del sistema no pueden eliminarse ni modificar sus permisos. 3. Un usuario con rol OPERADOR no puede crear otros usuarios. 4. Los permisos se evalúan en cada request API (no solo en la UI). 5. El cambio de permisos de un rol fuerza re-autenticación de todos los usuarios con ese rol. 6. El log de auditoría registra creación, modificación y eliminación de roles. 7. Los admin de tenant solo ven roles que tienen permisos permitidos para su nivel. ---

## Endpoints
- `GET /api/v1/admin/roles` — Listar roles - `POST /api/v1/admin/roles` — Crear rol - `GET /api/v1/admin/roles/{id}` — Detalle de rol - `PUT /api/v1/admin/roles/{id}` — Actualizar rol - `DELETE /api/v1/admin/roles/{id}` — Eliminar rol - `GET /api/v1/admin/permissions` — Listar permisos disponibles ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los permisos deben ser evaluados tanto en frontend como en backend (defensa en profundidad). - Se recomienda implementar middleware de autorización que valide permisos en cada endpoint. - Los logs de auditoría de permisos deben incluir: quién hizo el cambio, rol afectado, permisos antes y después.
