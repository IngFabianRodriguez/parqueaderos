# SPEC-08-095 — Políticas de Bloqueo de Vehículos

## Metadata
- **RF origen**: RF-095
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: vehicle-service, billing-service, access-control-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar políticas de bloqueo de vehículos basadas en días de mora o monto mínimo pendiente **para** garantizar el pago de estacionamiento y proteger los ingresos del negocio.

## Objetivo
El sistema debe permitir al `tenant_admin` definir y gestionar políticas de bloqueo. Un vehículo se bloquea cuando incumple las condiciones definidas (días en mora o monto mínimo pendiente). Las políticas definen umbrales de bloqueo y pueden incluir condiciones de desbloqueo automático (pago, tiempo).

## Comportamiento Específico

### Estructura de política de bloqueo
- `block_trigger`: `days_overdue`, `amount_overdue`, `combined`.
- `days_overdue_threshold`: días de mora para bloquear.
- `amount_overdue_threshold`: monto mínimo pendiente para bloquear.
- `applies_to`: `all_vehicles`, `registered_only`, `unregistered_only`.
- `grace_period_hours`: horas de gracia antes del bloqueo.
- `auto_unlock_on_payment`: si se desbloquea al pagar.
- `partial_payment_unlocks`: si un pago parcial desbloquea.
- `auto_unlock_after_days`: días para desbloqueo automático (0 = nunca).
- `notification_before_block`, `notification_hours_before`.
- `active`, `priority`.

### Estados de un vehículo
- `active`: sin restricciones; acceso normal.
- `pending_payment`: saldo pendiente dentro del período de gracia.
- `blocked`: no puede entrar/salir hasta regularizar.
- `temporarily_unblocked`: desbloqueado temporalmente (pago parcial).

### Evaluación y ejecución de bloqueos (job periódico)
1. El job `block-policy-evaluator` se ejecuta cada hora.
2. Para cada vehículo registrado:
   - Obtiene saldo pendiente y días en mora.
   - Evalúa cada política por prioridad.
   - Si cumple criterios y no está bloqueado:
     - Envía notificación previa (si está configurada).
     - Espera el período de gracia.
     - Si sigue en condiciones: cambia estado a `blocked`.
     - Genera evento `vehicle_blocked`.
3. Para vehículos bloqueados:
   - Verifica si cumple condiciones de desbloqueo automático.
   - Si se desbloquea: genera evento `vehicle_unblocked`.

## Criterios de Aceptación
1. El admin puede crear, editar y eliminar políticas de bloqueo.
2. El sistema bloquea vehículos automáticamente cuando se cumplen los criterios.
3. Los bloqueos se aplican según la prioridad de políticas cuando hay múltiples.
4. El período de gracia se respeta antes de ejecutar el bloqueo.
5. Las notificaciones previas al bloqueo se envían con la anticipación configurada.
6. El desbloqueo automático por pago funciona según la configuración.
7. Un vehículo bloqueado no puede registrar entradas ni salidas.

## Datos de Entrada
- `tenant_id` (UUID): Identificador del tenant.
- `block_trigger` (string): Tipo de trigger — `days_overdue`, `amount_overdue`, `combined`.
- `days_overdue_threshold` (int): Días de mora para bloquear.
- `amount_overdue_threshold` (decimal): Monto mínimo pendiente para bloquear.
- `applies_to` (string): `all_vehicles`, `registered_only`, `unregistered_only`.
- `grace_period_hours` (int): Horas de gracia antes del bloqueo.
- `auto_unlock_on_payment` (boolean): Si se desbloquea al pagar.
- `partial_payment_unlocks` (boolean): Si un pago parcial desbloquea.
- `auto_unlock_after_days` (int): Días para desbloqueo automático (0 = nunca).
- `notification_before_block` (boolean): Si se envía notificación previa.
- `notification_hours_before` (int): Horas de anticipación para la notificación.
- `active` (boolean): Si la política está activa.
- `priority` (int): Prioridad de la política.

## Datos de Salida
- `block_policies.id` (UUID): ID de la política creada.
- `block_policies.tenant_id`, `block_trigger`, `days_overdue_threshold`, `amount_overdue_threshold` (mixed): Criterios de bloqueo.
- `block_policies.applies_to`, `grace_period_hours`, `auto_unlock_on_payment`, `partial_payment_unlocks` (mixed): Configuración.
- `block_policies.auto_unlock_after_days`, `notification_before_block`, `notification_hours_before` (mixed): Desbloqueo y notificación.
- `block_policies.active`, `priority` (mixed): Estado y prioridad.
- `vehicles.status` (string): Estado actualizado del vehículo — `active`, `pending_payment`, `blocked`, `temporarily_unblocked`.
- Evento: `vehicle_blocked` o `vehicle_unblocked` publicado.