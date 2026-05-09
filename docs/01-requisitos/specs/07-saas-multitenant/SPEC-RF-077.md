# SPEC-07-077 — Auditoría de Cambios en Registros Maestros

## Metadata
- **RF origen**: RF-077
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: audit-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** que el sistema guarde un historial de cada cambio realizado en los registros maestros (tarifas, categorías, usuarios, sitios) **para** poder rastrear quién cambió qué y cuándo, facilitando la resolución de problemas y la auditoría de cumplimiento.

## Objetivo
El sistema debe mantener un historial de cambios (audit trail) para todos los registros maestros. Cada modificación genera un registro con: usuario que hizo el cambio, timestamp, tipo de operación, valores anteriores y nuevos. Los registros maestros incluyen: sites, rate_plans, vehicle_categories, users, roles, payment_methods.

## Comportamiento Específico

### Registro de cambios
1. Antes de cualquier UPDATE o DELETE en un registro maestro, el servicio captura el estado actual (before image).
2. Después de la operación, captura el nuevo estado (after image).
3. Inserta un registro en `master_record_history`: `record_type`, `record_id`, `operation` (CREATE/UPDATE/DELETE), `before_values` (JSON), `after_values` (JSON), `user_id`, `timestamp`, `tenant_id`.
4. El registro es append-only; no se elimina jamás.

### Consulta del historial
1. El admin accede a `Settings → Audit → Record History`.
2. Selecciona el tipo de registro y el ID específico.
3. El sistema muestra la línea de tiempo de cambios: Created → modificaciones → estado actual.
4. Cada entrada muestra: timestamp, usuario, tipo de operación, y diff de valores.

### Retención
- Historial de registros maestros: retención infinita (no se elimina).
- Disponible para consulta desde el admin panel y via API.

## Criterios de Aceptación
1. Cada CREATE, UPDATE y DELETE en un registro maestro genera un registro en `master_record_history`.
2. Los registros incluyen: usuario, timestamp, tipo de operación, valores antes y después.
3. El historial es consultable por tipo de registro e ID específico.
4. El historial es inmutable; no se puede modificar ni eliminar.
5. Un admin solo ve el historial de los registros de su tenant.
6. Los valores se almacenan como JSON para flexibilidad.
7. El `superadmin` puede ver el historial de cualquier tenant.