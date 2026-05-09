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