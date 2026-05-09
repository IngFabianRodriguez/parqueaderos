# SPEC-07-074 — Restricción de Acceso de Usuarios a Sedes Específicas

## Metadata
- **RF origen**: RF-074
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: user-service, site-service, tenant-service

---

## User Story
**Como** administrador de un tenant con múltiples sedes **quiero** restringir qué usuarios pueden acceder a qué sedes **para** que cada operador solo vea y gestione la información de las sedes que le corresponden.

## Objetivo
El sistema debe permitir que el `tenant_admin` configure qué sedes puede acceder cada usuario. Un usuario con rol `operator` o `viewer` puede tener acceso a todas las sedes o solo a un subconjunto específico. El sistema filtra automáticamente los datos para mostrar solo las sedes autorizadas.

## Comportamiento Específico

### Asignar sedes a un usuario
1. El `tenant_admin` accede a `Settings → Users → [Usuario] → Site Access`.
2. Ve la lista de todas las sedes con checkboxes.
3. Selecciona las sedes a las que el usuario debe tener acceso.
4. Guarda la configuración.
5. El sistema elimina las asignaciones existentes y reinserta las nuevas.
6. Se registra en `audit_log`.

### Asignación "Todas las sedes"
- Si el admin marca "Acceso a todas las sedes", `user_site_access` queda vacío (NULL) = acceso total.
- La consulta de "todas las sedes" es: `WHERE tenant_id = user.tenant_id`.

### Validación de acceso en tiempo de query
- Cuando un usuario hace `GET /api/v1/sites`, el sistema añade condición `site_id IN (SELECT site_id FROM user_site_access WHERE user_id = ?)`. Si `user_site_access` está vacío, no aplica filtro.

### Validación en operaciones
- Cuando un operador registra ingreso/salida, el sistema verifica que la `site_id` esté en las sedes autorizadas. Si no, retorna 403 Forbidden.

## Criterios de Aceptación
1. El `tenant_admin` puede asignar 0, 1 o múltiples sedes a cualquier usuario con rol `operator` o `viewer`.
2. Los usuarios con rol `tenant_admin` tienen acceso implícito a todas las sedes.
3. Un usuario sin asignación (NULL) tiene acceso a todas las sedes de su tenant.
4. Un usuario con lista vacía de sitios asignados ve 0 sitios.
5. Toda operación filtra automáticamente por las sedes asignadas.
6. El intento de acceso a una sede no autorizada retorna 403 Forbidden.
7. Los cambios de asignación se registran en `audit_log`.