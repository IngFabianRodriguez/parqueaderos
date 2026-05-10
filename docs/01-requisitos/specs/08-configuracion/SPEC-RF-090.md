# SPEC-08-090 — Configuración de Roles y Permisos de Usuario

## Metadata
- **RF origen**: RF-090
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: auth-service, user-service, config-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** definir los roles y permisos que controlan qué acciones puede realizar cada usuario **para** garantizar la seguridad y limitar el acceso a funcionalidades según la responsabilidad de cada persona.

## Objetivo
El sistema implementa RBAC (Role-Based Access Control). El `tenant_admin` puede crear roles personalizados y asignar permisos específicos a cada rol. Los roles son globales al tenant; un usuario puede tener múltiples roles. El sistema verifica permisos en todos los endpoints protected.

## Comportamiento Específico

### Roles predefinidos del sistema
- `tenant_admin`: acceso total.
- `operator`: operación diaria (acceso a talanquera).
- `cashier`: cobro y cuadre de caja.
- `supervisor`: supervisión y overrides.
- `company_admin`: admin de empresa B2B con flota.

Los roles predefinidos no pueden eliminarse, solo editarse.

### Permisos disponibles (agrupados por módulo)
- **Acceso**: `gate_open`, `gate_close`, `emergency_open`, `override_barrier`.
- **Caja**: `process_payment`, `issue_refund`, `close_shift`, `view_cashier_reports`.
- **Configuración**: `edit_rates`, `edit_schedule`, `edit_payment_methods`, `edit_taxes`.
- **Usuarios**: `create_user`, `edit_user`, `deactivate_user`, `assign_role`.
- **Reportes**: `view_reports`, `export_reports`, `view_financial_reports`.
- **B2B**: `manage_companies`, `manage_fleet_vehicles`, `view_fleet_reports`.
- **Admin**: `manage_roles`, `api_keys`, `billing`.

### Creación de rol
1. El admin accede a `Settings → Security → Roles and Permissions`.
2. Crea un nuevo rol: `role_name`, `role_code` (único), `description`.
3. Asigna permisos marcando los checkboxes.
4. Guarda; se persiste en `roles`, `role_permissions`.
5. Se publica `ROLES_UPDATED`.

### Asignación de roles
- El `tenant_admin` asigna roles a usuarios en `Settings → Users → [Usuario] → Roles`.
- Un usuario puede tener múltiples roles; los permisos se acumulan (OR).

### Validaciones
- `role_code` único dentro del tenant.
- Al menos un permiso por rol.
- No se puede eliminar un rol con usuarios asignados (error 409).

## Criterios de Aceptación
1. El admin puede crear roles personalizados además de los predefinidos.
2. Cada rol tiene un `role_code` único dentro del tenant.
3. Los permisos se asignan a roles; los usuarios heredan permisos a través de sus roles.
4. Un usuario puede tener múltiples roles; los permisos se acumulan.
5. Los roles predefinidos no pueden eliminarse.
6. El sistema verifica permisos en cada endpoint protected.
7. El evento `ROLES_UPDATED` se publica cuando se modifican roles o permisos.

## Datos de Entrada
- `tenant_id` (UUID): Identificador del tenant.
- `role_name` (string): Nombre visible del rol.
- `role_code` (string): Código único del rol dentro del tenant.
- `description` (string): Descripción del rol.
- `permissions` (array[string]): Lista de permisos asignados al rol.

## Datos de Salida
- `roles.id` (UUID): ID del rol creado.
- `roles.tenant_id`, `role_name`, `role_code`, `description` (string): Datos almacenados.
- `role_permissions.role_id`, `permission_code` (mixed): Permisos asignados.
- `role_assignment_count` (int): Número de usuarios con este rol (para validación al eliminar).
- Evento: `ROLES_UPDATED` publicado cuando se crean/modifican roles o permisos.