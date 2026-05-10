# SPEC-08-085 — Planes de Tarifa (Tarifas por Fracción, Minutos, Horas)

## Metadata
- **RF origen**: RF-085
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: rate-service, billing-service, config-service, site-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar los planes de tarifa de cada sede **para** definir cómo se cobra el estacionamiento: fracciones de tiempo, tarifas por hora, tarifas planas, y topes máximos.

## Objetivo
El sistema debe permitir al `tenant_admin` crear y gestionar planes de tarifa por sede y zona. Cada plan define: la estructura de cobro (fracción, hourly, flat), los montos, los horarios de aplicación, y los topes máximos. Un sitio puede tener múltiples planes activos.

## Comportamiento Específico

### Estructura de un plan de tarifa
1. El admin accede a `Settings → Sites → [Sede] → Rate Plans`.
2. Crea un plan:
   - `plan_name`: nombre (ej: "Tarifa Normal", " Nocturna 50%").
   - `applies_to`: `zone_id` específico o `null` (todas).
   - `applies_to_vehicle_types`: array de tipos de vehículo o `all`.
   - `schedule_id`: horario durante el cual aplica (RF-084).
   - `rate_type`: `fraction` | `hourly` | `flat` | `daily`.
   - `fraction_minutes`: minutos de cada fracción (ej: 15).
   - `fraction_rate`: monto por fracción.
   - `hourly_rate`: monto por hora completa (si type=hourly).
   - `flat_rate`: monto fijo (si type=flat).
   - `daily_cap_amount`: monto máximo por día (null = sin tope).
   - `minimum_charge`: tarifa mínima por estadía.
   - `is_active`: booleano.
   - `effective_from`, `effective_until`: período de validez.

### Aplicación de tarifas
1. Cuando un vehículo ingresa, el sistema determina el `rate_plan` aplicable según: sede, zona, tipo de vehículo, y horario actual.
2. Al salir, el billing-service calcula el total según: duración, fracción, y topes.
3. El resultado se almacena en `invoices.base_rate` y `invoices.total`.

### Planes múltiples
- Un sitio puede tener varios planes (ej: uno normal, uno con descuento del 50% para noche).
- Se selecciona el plan según la franja horaria del ingreso.
- Si hay conflicto de horarios, se usa el plan con `priority` mayor.

## Criterios de Aceptación
1. El admin puede crear múltiples planes de tarifa por sede y zona.
2. Cada plan puede ser: por fracción, hourly, flat, o daily.
3. Los planes tienen horarios de aplicación definidos (schedule).
4. Los planes aplican a tipos de vehículo específicos o a todos.
5. Los topes máximos (daily cap) se aplican al calcular el total.
6. La tarifa mínima define el cobro mínimo por cualquier estadía.
7. Los planes tienen período de validez (effective_from/until).
8. Un vehículo siempre se cobra con el plan vigente al momento del ingreso.

## Datos de Entrada
- `site_id` (UUID): Identificador de la sede.
- `plan_name` (string): Nombre del plan de tarifa.
- `zone_id` (UUID, nullable): Zona a la que aplica (null = todas).
- `applies_to_vehicle_types` (array[string]): Tipos de vehículo o `all`.
- `schedule_id` (UUID): Horario de aplicación (RF-084).
- `rate_type` (string): `fraction`, `hourly`, `flat` o `daily`.
- `fraction_minutes`, `fraction_rate` (int): Configuración de fracción.
- `hourly_rate` (decimal): Tarifa por hora.
- `flat_rate` (decimal): Tarifa plana.
- `daily_cap_amount` (decimal, nullable): Tope máximo diario.
- `minimum_charge` (decimal): Tarifa mínima por estadía.
- `effective_from`, `effective_until` (datetime): Período de validez.

## Datos de Salida
- `rate_plans.id` (UUID): ID del plan creado.
- `rate_plans.site_id`, `plan_name`, `rate_type`, `fraction_minutes`, `fraction_rate` (mixed): Datos almacenados.
- `rate_plans.hourly_rate`, `flat_rate`, `daily_cap_amount`, `minimum_charge` (decimal): Tarifas almacenadas.
- `rate_plans.effective_from`, `effective_until` (datetime): Período de validez.
- Evento: `RATE_PLAN_CREATED` o `RATE_PLAN_UPDATED` publicado.