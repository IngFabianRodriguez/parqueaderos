# SPEC-06-028 — RBAC: Control de Acceso Basado en Roles

## Metadata
- **RF origen**: RF-028
- **Módulo**: 06-seguridad
- **Prioridad**: Alta
- **Servicios**: auth-service, user-service, gateway-service, todos los servicios

---

## User Story
**Como** superadmin **quiero** definir qué acciones puede realizar cada rol sobre cada recurso del sistema **para** garantizar el principio de menor privilegio y evitar que usuarios accedan a funciones fuera de su responsabilidad.

## Objetivo
El sistema debe implementar un sistema RBAC donde cada rol (superadmin, admin_sede, operador, cliente) tiene un conjunto de permisos específicos sobre recursos definidos. Los permisos se verifican en cada request y se incluyen como claims en el JWT.

## Comportamiento Específico

### Happy Path
1. El API Gateway recibe una request con header Authorization: Bearer <jwt>
2. El Gateway decodifica el JWT y extrae los claims: user_id, rol, permisos, sede_ids
3. El Gateway consulta la ruta del endpoint y el método HTTP para mapearlos a recurso y acción
4. El Gateway verifica si el rol del usuario tiene el permiso requerido
5. Si el permiso existe: la request se reenvía al servicio de backend
6. Si el permiso no existe: retorna 403 Forbidden

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Rol con nombre duplicado | Sistema rechaza con 409 Conflict |
| Permiso inválido (no existe recurso:accion) | Sistema rechaza con 400 y lista de permisos válidos |
| Admin intenta asignar rol superior al suyo | Sistema rechaza con 403 |
| Acceso a sede no asignada | Sistema retorna 403 |
| JWT manipulado (firma inválida) | Gateway retorna 401 y registra alerta de seguridad |
| Acceso sin autenticación (sin JWT) | Retorna 401 Unauthorized |

## Datos de Entrada
### Creación de Rol
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| nombre | string | Nombre único del rol | Sí |
| descripcion | string | Descripción del propósito del rol | No |
| permisos | array | Lista de permisos en formato "recurso:accion" | Sí |

### Asignación de Rol a Usuario
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| usuario_id | UUID | ID del usuario a modificar | Sí |
| rol_id | UUID | ID del rol a asignar | Sí |
| sede_ids | array | IDs de sedes a las que tiene acceso | Condicional |
| motivo | string | Razón del cambio (para auditoría) | Sí |

## Datos de Salida
### Respuesta de Permiso Denegado
```json
{
  "error": "access_denied",
  "code": 403,
  "message": "No tienes permiso para realizar esta acción",
  "details": {
    "required_permission": "sedes:write",
    "your_permissions": ["sedes:read", "reports:read"],
    "resource": "sede",
    "action": "write"
  }
}
```

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un usuario con rol "operador" NO puede ejecutar comandos sobre talanqueras de sedes diferentes a las asignadas
2. Un admin_sede NO puede crear usuarios con permisos superiores a los suyos
3. El sistema retorna 403 Forbidden con mensaje claro cuando un usuario intenta acceder sin permisos
4. Los permisos se verifican en el API Gateway antes de reenviar la request
5. Un superadmin puede crear nuevos roles, asignar permisos arbitrarios, y asignar roles a usuarios
6. Un intento de acceso sin autenticación retorna 401 Unauthorized
7. Los endpoints públicos (login, salud) no requieren autenticación

## Endpoints
- `GET /api/v1/roles` — Lista todos los roles disponibles (solo superadmin)
- `POST /api/v1/roles` — Crea un nuevo rol (solo superadmin)
- `GET /api/v1/roles/{id}` — Detalle de un rol con sus permisos
- `PUT /api/v1/roles/{id}` — Actualiza un rol (solo superadmin)
- `DELETE /api/v1/roles/{id}` — Elimina un rol
- `GET /api/v1/permissions` — Lista todos los permisos disponibles
- `PUT /api/v1/users/{id}/role` — Asigna un rol a un usuario

## Health Check
- `GET /health` → { "status": "ok" }