# SPEC-07-076 — Auditoría de Accesos y Operaciones en Tiempo Real

## Metadata
- **RF origen**: RF-076
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: audit-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** ver en tiempo real quién accede al sistema y qué operaciones realiza **para** detectar actividades sospechosas y mantener un registro de auditoría completo.

## Objetivo
El sistema debe mantener un log de auditoría de todas las operaciones relevantes: login/logout, creación/modificación/eliminación de recursos, cambios de configuración, y accesos a datos sensibles. El log debe ser inmutable y consultable en tiempo real.

## Comportamiento Específico

### Registro de eventos de auditoría
1. Cada microservicio emite eventos a Kafka topic `audit.events`.
2. El audit-service consume estos eventos y los persiste en `audit_log` (append-only).
3. Cada evento incluye: `event_id`, `timestamp`, `user_id`, `tenant_id`, `action`, `resource_type`, `resource_id`, `ip_address`, `user_agent`, `request_id`, `details` (JSON).

### Consulta del log de auditoría
1. El `tenant_admin` accede a `Settings → Audit Log`.
2. El sistema muestra los eventos del tenant ordenados por timestamp descendente.
3. Filtros disponibles: usuario, acción, tipo de recurso, rango de fechas.
4. Los eventos se muestran paginados (50 por página).

### Eventos registrados
- Autenticación: `login`, `logout`, `login_failed`, `mfa_enabled`, `password_changed`.
- Usuarios: `user_created`, `user_updated`, `user_deactivated`, `role_assigned`, `role_removed`.
- Sitios: `site_created`, `site_updated`, `site_deleted`.
- Configuración: `settings_changed`, `rate_plan_created`, `rate_plan_updated`.
- Transacciones: `transaction_completed`, `invoice_generated`, `payment_received`.
- API: `api_key_created`, `api_key_revoked`.

## Criterios de Aceptación
1. Todos los eventos de auditoría se registran en < 2 segundos del evento original.
2. El log de auditoría es inmutable: no se puede modificar ni eliminar.
3. Cada registro tiene timestamp, usuario, acción, recurso afectado e IP.
4. El `tenant_admin` puede consultar su log con filtros por usuario, acción, recurso y fecha.
5. Los eventos se retienen por 2 años (configurable).
6. Los datos de auditoría son específicos por tenant: un admin solo ve los de su tenant.
7. El `superadmin` puede ver logs de cualquier tenant.