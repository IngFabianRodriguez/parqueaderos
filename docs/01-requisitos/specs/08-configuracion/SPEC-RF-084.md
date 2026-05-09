# SPEC-08-084 — Horarios de Operación por Sede

## Metadata
- **RF origen**: RF-084
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: config-service, site-service, billing-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar los horarios de operación de cada sede **para** que el sistema sepa en qué horas puede haber ingresos/egresos y cómo calcular las tarifas según el momento del día.

## Objetivo
El sistema debe permitir al `tenant_admin` definir horarios de operación para cada sede: horas de apertura y cierre, días de la semana activos, y si hay franjas horarias con tarifas diferentes (horario normal vs nocturno). Cada schedule puede tener múltiples franjas.

## Comportamiento Específico

### Configuración de horario
1. El admin accede a `Settings → Sites → [Sede] → Schedules`.
2. Crea un schedule con:
   - `schedule_name`: nombre descriptivo (ej: "Horario Regular", " Nocturno").
   - `days_of_week`: array [0-6] donde 0=Domingo.
   - `time_slots`: array de franjas horarias `[{start: "06:00", end: "22:00"}]`.
   - `is_active`: booleano.
   - `applies_to`: `all` o fechas específicas (date range).
3. Puede crear múltiples schedules (ej: uno para invierno, otro para verano).
4. Se guarda en `site_schedules`.

### Franjas horarias con tarifas
- Si una franja horaria tiene una tarifa diferenciada, el `rate_plan` referenciado en la franja se usa para calcular el costo durante esas horas.
- El billing-service consulta `site_schedules` para saber si la sede está abierta al momento del ingreso/egreso.

### Validación
- Si un vehículo intenta ingresar fuera del horario: se registra como `after_hours` y se puede aplicar tarifa especial o denegar el acceso según configuración.
- Si un vehículo está dentro del estacionamiento cuando cierra la sede: se permite la salida; el ingreso se deniega.

### Horas especiales (feriados)
- El admin puede agregar fechas especiales (feriados) con horario diferenciado.
- Se guardan en `site_special_days`: `date`, `schedule_id` (scheduleoverride), `description`.

## Criterios de Aceptación
1. El admin puede crear múltiples schedules por sede (ej: regular, nocturno, temporada).
2. Cada schedule define días de la semana y franjas horarias.
3. Los horarios diferenciados aplican tarifas específicas según la franja.
4. Los vehículos no pueden ingresar fuera del horario activo; la salida siempre está permitida.
5. Las fechas especiales (feriados) pueden tener horarios override.
6. El sistema notifica si un vehículo está dentro del estacionamiento al momento del cierre.