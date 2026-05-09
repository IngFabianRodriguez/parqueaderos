# SPEC-08-089 — Configuración de Impuestos y Descuentos por Sede

## Metadata
- **RF origen**: RF-089
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: billing-service, rate-service, config-service, transaction-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar los impuestos aplicables y los descuentos promocionales por sede **para** que el sistema calcule el monto final correcto a cobrar al cliente.

## Objetivo
El sistema debe permitir al `tenant_admin` configurar: (1) impuestos que se aplican sobre el subtotal de cada transacción (IVA, ISR, etc.), y (2) descuentos o promociones con fechas de vigencia. Los impuestos y descuentos son acumulables y se configuran por sede.

## Comportamiento Específico

### Configuración de Impuestos
1. El admin accede a `Settings → Sites → [Sede] → Taxes`.
2. Puede agregar un impuesto:
   - `tax_name`: nombre (ej: "IVA 19%", "ISR 2%").
   - `tax_type`: `percentage` o `fixed` (monto fijo).
   - `tax_rate`: porcentaje (0-100) o monto fijo.
   - `applies_to`: `all`, `cash_only`, `card_only`.
   - `is_default`: si aplica automáticamente a toda transacción.
   - `is_active`: booleano.
3. Se pueden agregar varios impuestos; el orden de aplicación es el orden de creación.

### Configuración de Descuentos
1. El admin accede a `Settings → Sites → [Sede] → Discounts`.
2. Puede crear un descuento:
   - `discount_name`: nombre (ej: "15% OFF primeros 30 min").
   - `discount_type`: `percentage`, `fixed_amount`, `flat_rate`.
   - `discount_value`: valor del descuento.
   - `target`: `all_vehicles`, `specific_category`, `subscribed_only`, `corporate_only`.
   - `discount_trigger`: `none`, `time_based`, `duration_based`, `coupon_code`.
   - `coupon_code`: código de cupón (si trigger=coupon_code).
   - `max_uses`: número máximo de usos (null = ilimitado).
   - `valid_from`, `valid_until`: rango de fechas de vigencia.
   - `is_active`: booleano.

### Orden de cálculo
1. Subtotal (base_rate + fractions + extras).
2. Descuentos aplicados (en orden de prioridad).
3. Impuestos aplicados (en el orden configurado).
4. = Total a Cobrar.

## Criterios de Aceptación
1. El admin puede configurar múltiples impuestos por sede con tipo y porcentaje/monto fijo.
2. Los impuestos pueden aplicar a todas las transacciones o solo a ciertos métodos de pago.
3. Los descuentos pueden ser porcentaje, monto fijo, o tarifa plana.
4. Los cupones tienen códigos únicos y controles de uso.
5. Los impuestos se calculan sobre el subtotal después de aplicar descuentos.
6. El evento `TAX_DISCOUNT_CONFIG_UPDATED` se publica tras cada cambio.