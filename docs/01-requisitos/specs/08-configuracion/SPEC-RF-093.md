# SPEC-08-093 — Reglas de Tarifación Configurables

## Metadata
- **RF origen**: RF-093
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: billing-service, pricing-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** definir y modificar reglas de tarifación desde el panel **para** controlar cómo se calcula el costo del estacionamiento: fracciones de tiempo, topes máximos y tarifas especiales.

## Objetivo
El sistema debe permitir al `tenant_admin` configurar reglas de tarifación completas y flexibles. Las reglas definen el cálculo del monto a cobrar según la duración, con soporte para: fracciones de tiempo (ej: cada 15 minutos), topes máximos (diarios/mensuales), tarifas especiales (navidad, hora pico, fines de semana), y tarifas diferenciadas por zona.

## Comportamiento Específico

### Estructura de regla de tarifación
1. `zone_id`: zona a la que aplica (null = todas).
2. `vehicle_type`: `car`, `motorcycle`, `truck`, `all`.
3. `base_rate`: tarifa base.
4. `time_fraction_minutes`: fracción de tiempo en minutos (ej: 15).
5. `fraction_rate`: tarifa por fracción.
6. `minimum_charge`: costo mínimo por estadía.
7. `has_daily_cap`, `daily_cap_amount`: tope diario opcional.
8. `has_monthly_cap`, `monthly_cap_amount`: tope mensual opcional.
9. `special_rates`: array de tarifas especiales.
10. `effective_from`, `effective_until`: período de vigencia.

### Tarifas especiales
- `special_type`: `holiday`, `peak_hour`, `weekend`, `seasonal`.
- `multiplier`: factor multiplicador (ej: 1.5 = 50% más caro).
- `fixed_amount`: monto fijo alternativo.
- `date_pattern`: patrón de fechas (ej: "12-24 to 12-31").
- `time_pattern`: patrón de horas (ej: "08:00-18:00").
- `day_of_week`: días de la semana [0-6].

### Aplicación al calcular tarifa
1. El billing-service consulta `pricing_rules` activas para la zona y tipo de vehículo.
2. Aplica la tarifa base según la duración.
3. Verifica y aplica topes máximos.
4. Verifica tarifas especiales (fecha/hora actual).
5. Calcula el monto final.

### Validaciones
- Dos reglas activas para el mismo período y zona generan conflicto.
- Si la duración excede un tope, se aplica el monto máximo.
- Cambio de tarifa durante estadía activa: se cobra según la tarifa vigente al momento del ingreso (locking).

## Criterios de Aceptación
1. El admin puede crear, editar, duplicar y eliminar reglas de tarifación.
2. Las reglas soportan fracciones de tiempo configurables (1, 5, 10, 15, 30, 60 min).
3. Los topes máximos (diarios/mensuales) se aplican correctamente.
4. Las tarifas especiales (navidad, hora pico, fines de semana) se aplican cuando corresponde.
5. Las reglas tienen período de vigencia y se auto-desactivan al expirar.
6. El sistema soporta múltiples zonas con diferentes tarifas en el mismo tenant.
7. Los cambios en reglas no afectan facturas ya emitidas.