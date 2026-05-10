# SPEC-08-092 — Configuración de Horarios de Notificaciones Batch

## Metadata
- **RF origen**: RF-092
- **Módulo**: 08-config-svc
- **Prioridad**: Media
- **Servicios**: notification-service, scheduler-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar los horarios de envío de notificaciones batch (resúmenes diarios, recordatorios) **para** que los recordatorios y alertas se envíen en horarios convenientes para los operadores y propietarios.

## Objetivo
El sistema debe permitir al `tenant_admin` configurar horarios programados para el envío de notificaciones batch. Estos horarios son configurables por tipo de notificación y soportan zonas horarias específicas del tenant.

## Comportamiento Específico

### Tipos de notificación batch soportados
- `daily_summary`: resumen diario de ingresos y ocupación (diaria).
- `payment_reminder`: recordatorio de pagos pendientes (diaria).
- `overdue_alert`: alerta de vehículos en mora (cada 6 horas).
- `occupancy_report`: reporte de ocupación (diaria).
- `custom`: plantilla personalizada (definida en RF-091).

### Configuración de horario
1. El admin accede a `Settings → Notifications → Batch Schedules`.
2. Selecciona el tipo de notificación batch.
3. Define la hora local de envío (formato HH:MM).
4. Selecciona los días de la semana (array [0-6], 0=Domingo).
5. Opcionalmente define la zona horaria (por defecto: zona del tenant).
6. Guarda la configuración.
7. El sistema valida que no haya conflicto con otro horario del mismo tipo.
8. Se persiste en `notification_schedules` y se activa el job en el scheduler.

### Ejecución del job
1. El scheduler consulta `notification_schedules` para obtener tareas activas.
2. Para cada schedule, calcula el próximo UTC execution time usando la zona horaria.
3. Cuando llega el momento UTC, dispara el job `batch-notification-sender`.
4. El job obtiene los datos (resumen diario, alertas pendientes, etc.).
5. Envía las notificaciones a los destinatarios correspondientes.
6. Registra en `notification_logs` con `batch_id`.

## Criterios de Aceptación
1. El admin puede crear, editar y eliminar horarios de notificación batch.
2. Los horarios se ejecutan en la zona horaria correcta del tenant.
3. Si un schedule tiene `enabled=false`, el scheduler lo ignora.
4. El sistema soporta al menos 5 tipos de notificación batch configurables.
5. Se puede definir múltiples schedules para el mismo tipo.
6. Los cambios en la configuración se reflejan en el scheduler en < 60 segundos.
7. Cada ejecución batch genera un registro en `notification_logs` con `batch_id` único.

## Datos de Entrada
- `tenant_id` (UUID): Identificador del tenant.
- `notification_type` (string): Tipo — `daily_summary`, `payment_reminder`, `overdue_alert`, `occupancy_report`, `custom`.
- `scheduled_time` (string): Hora local de envío (formato HH:MM).
- `days_of_week` (array[int]): Días de la semana [0-6], 0=Domingo.
- `timezone` (string, opcional): Zona horaria (por defecto: zona del tenant).
- `enabled` (boolean): Si el schedule está activo.

## Datos de Salida
- `notification_schedules.id` (UUID): ID del schedule creado.
- `notification_schedules.tenant_id`, `notification_type`, `scheduled_time`, `days_of_week` (mixed): Datos almacenados.
- `notification_schedules.timezone`, `enabled` (mixed): Configuración de zona horaria y estado.
- `next_execution_utc` (datetime): Próxima ejecución calculada en UTC.
- `notification_logs.batch_id` (UUID): ID único de cada ejecución batch.