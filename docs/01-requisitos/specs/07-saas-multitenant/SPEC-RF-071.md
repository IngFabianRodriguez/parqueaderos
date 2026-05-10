# SPEC-07-071 — Asignación de Roles a Usuarios por el Tenant Admin

## Metadata
- **RF origen**: RF-071
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: user-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** asignar y cambiar los roles de los usuarios de mi organización **para** ajustar los permisos de acceso según las necesidades del negocio sin tener que eliminar y recrear usuarios.

## Objetivo
El sistema debe permitir que el `tenant_admin` asigne, modifique y elimine roles de los usuarios dentro de su tenant. Cada usuario puede tener uno o múltiples roles; cada rol tiene un conjunto de permisos definidos. Los cambios de rol son inmediatos.

## Comportamiento Específico

### Asignar un rol a un usuario
1. El `tenant_admin` accede a `Settings → Users → [Usuario] → Roles`.
2. Ve la lista de roles disponibles y los roles actualmente asignados al usuario.
3. Selecciona uno o más roles para asignar.
4. Confirma la acción.
5. El sistema inserta las asignaciones en `user_roles`.
6. Se registra en `audit_log`.

### Eliminar un rol
1. El `tenant_admin` selecciona un rol asignado y hace clic en "Eliminar".
2. El sistema elimina la fila de `user_roles`.
3. Si el usuario queda sin roles, se le asigna `viewer` por defecto.

### Restricción
- Un `tenant_admin` no puede asignarse roles más altos que el suyo.
- El `superadmin` puede asignar cualquier rol.

## Criterios de Aceptación
1. El `tenant_admin` puede agregar y eliminar roles de cualquier usuario de su tenant.
2. Un usuario puede tener múltiples roles simultáneamente.
3. Los cambios de rol se registran en `audit_log` con `performed_by` y `timestamp`.
4. No se permite asignar roles más allá de los que el admin tiene.
5. El `superadmin` puede modificar roles de cualquier usuario en cualquier tenant.

## Datos de Entrada
- **user_id** — ID del usuario al que se le asignan roles (UUID, required)
- **roles** — Array de IDs de roles a asignar al usuario (UUID[], required)
- **performed_by** — ID del admin que realiza la asignación (UUID, required, implicit from session)

## Datos de Salida
- **user_roles** — Tabla de asignaciones actualizada con los nuevos roles
- **audit_log** — Entrada con `action = role_assigned | role_removed`, `user_id`, `roles[]`, `performed_by`, `timestamp`
- **Respuesta** — 200 OK con `{ user_id, assigned_roles: [...] }`