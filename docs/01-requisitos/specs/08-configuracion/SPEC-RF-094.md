# SPEC-08-094 — Descuentos y Promociones Configurables

## Metadata
- **RF origen**: RF-094
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: billing-service, promotion-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar descuentos y promociones con reglas de validez y límites de uso **para** atraer clientes, fidelizar usuarios frecuentes y ofrecer ofertas especiales en fechas o condiciones específicas.

## Objetivo
El sistema debe permitir al `tenant_admin` crear, modificar y desactivar descuentos y promociones. Cada promoción define: tipo de descuento (porcentaje, monto fijo, tiempo gratis), condiciones de aplicación (monto mínimo, tipo de vehículo, días), período de validez, y límites de uso (global y por usuario).

## Comportamiento Específico

### Tipos de descuento
- `percentage`: porcentaje de descuento sobre el total.
- `fixed_amount`: monto fijo descontado.
- `free_time`: tiempo de estacionamiento gratis (ej: 30 min gratis).
- `free_exit`: exoneración de pago completa.

### Estructura de una promoción
- `name`, `description`.
- `code`: código de redención (null = automática).
- `discount_type`, `discount_value`.
- `min_purchase_amount`: monto mínimo de compra.
- `max_discount_amount`: tope de descuento (para percentage).
- `applicable_vehicle_types`, `applicable_zones`.
- `valid_from`, `valid_until`.
- `max_total_uses`, `max_uses_per_user`.
- `days_of_week`, `time_restriction` (start_time, end_time).
- `stackable`: si se puede combinar con otras promociones.
- `priority`: prioridad de aplicación (mayor = primero).

### Aplicación en facturación
1. El billing-service consulta las `promotions` aplicables al vehículo que sale.
2. Filtra por: zona, vehículo, monto mínimo, fechas, días de semana, horario.
3. Si hay código: busca coincidencia exacta.
4. Selecciona la promoción de mayor prioridad (si stackable=false, solo una).
5. Aplica el descuento al subtotal.
6. Registra el uso en `promotion_redemptions`.

## Criterios de Aceptación
1. El admin puede crear promociones con: porcentaje, monto fijo, tiempo gratis o salida gratis.
2. Las promociones pueden tener código manual o ser automáticas.
3. Se pueden definir condiciones: monto mínimo, tipo de vehículo, zona, días, horario.
4. Los límites de uso (global y por usuario) se aplican correctamente.
5. Las fechas de validez se respetan; promociones expiradas no se aplican.
6. El orden de aplicación cuando hay múltiples promociones (prioridad) es correcto.
7. Los usos se registran para auditoría y reporting.
8. Las promociones pueden ser combinables o excluyentes.

## Datos de Entrada
- `tenant_id` (UUID): Identificador del tenant.
- `name`, `description` (string): Nombre y descripción de la promoción.
- `code` (string, nullable): Código de redención (null = automática).
- `discount_type` (string): `percentage`, `fixed_amount`, `free_time`, `free_exit`.
- `discount_value` (decimal): Valor del descuento.
- `min_purchase_amount` (decimal, nullable): Monto mínimo de compra.
- `max_discount_amount` (decimal, nullable): Tope de descuento (para percentage).
- `applicable_vehicle_types`, `applicable_zones` (array[string], nullable): Condiciones de aplicación.
- `valid_from`, `valid_until` (datetime): Período de validez.
- `max_total_uses`, `max_uses_per_user` (int, nullable): Límites de uso.
- `days_of_week` (array[int], opcional): Días de aplicación [0-6].
- `time_restriction` (JSON, opcional): `{start_time, end_time}` para limitar horario.
- `stackable` (boolean): Si se puede combinar con otras promociones.
- `priority` (int): Prioridad de aplicación (mayor = primero).
- `is_active` (boolean): Estado de la promoción.

## Datos de Salida
- `promotions.id` (UUID): ID de la promoción creada.
- `promotions.tenant_id`, `name`, `code`, `discount_type`, `discount_value` (mixed): Datos almacenados.
- `promotions.min_purchase_amount`, `max_discount_amount`, `valid_from`, `valid_until` (mixed): Condiciones y vigencia.
- `promotions.max_total_uses`, `max_uses_per_user`, `stackable`, `priority`, `is_active` (mixed): Límites y configuración.
- `promotion_redemptions.id` (UUID): ID de cada redención registrada.
- `promotion_redemptions.promotion_id`, `user_id`, `vehicle_id`, `invoice_id`, `redeemed_at` (mixed): Registro de uso.
- Evento: `PROMOTION_CREATED`, `PROMOTION_UPDATED` o `PROMOTION_REDEEMED` publicado.