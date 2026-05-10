# SPEC-08-087 — Configuración de Métodos de Pago

## Metadata
- **RF origen**: RF-087
- **Módulo**: 08-config-svc
- **Prioridad**: Alta
- **Servicios**: config-service, payment-service, billing-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar qué métodos de pago acepta mi estacionamiento **para** que mis clientes puedan pagar de la forma que prefieran (efectivo, tarjeta, transferencia, etc.) y el sistema procese correctamente cada transacción.

## Objetivo
El sistema debe permitir al `tenant_admin` habilitar y configurar los métodos de pago disponibles en cada sede. Los métodos incluyen: efectivo, tarjeta de crédito/débito (POS), transferencia bancaria, monedero digital, y pagos QR. Cada método tiene configuraciones específicas.

## Comportamiento Específico

### Métodos de pago disponibles
1. `cash`: Pago en efectivo — requiere configuración de caja (RF-092).
2. `card`: Tarjeta crédito/débito via terminal POS — requiere `pos_provider` y `terminal_id`.
3. `bank_transfer`: Transferencia bancaria — requiere `bank_account` y referencia.
4. `digital_wallet`: Monedero digital — requiere `wallet_provider` (Yappy, MercadoPago, etc.).
5. `qr_pay`: Pago con código QR — genera QR estático/dinámico.

### Configuración por sede
1. El admin accede a `Settings → Sites → [Sede] → Payment Methods`.
2. Ve la lista de métodos disponibles con checkbox de habilitación.
3. Para cada método habilitado, configura:
   - `enabled`: booleano.
   - `position`: orden de prioridad en la UI del operador.
   - `config`: JSON con settings específicos del método.
   - `minimum_amount`: monto mínimo para usar este método (null = sin mínimo).
   - `maximum_amount`: monto máximo (null = sin máximo).
   - `is_default`: si es el método sugerido por defecto.
4. Guarda en `site_payment_methods`.

### Configuración de POS (card)
- `pos_provider`: nombre del proveedor (ej: "Stripe", "Verifone").
- `terminal_id`: ID del terminal POS.
- `merchant_id`: ID del comercio.
- `acquirer_id`: ID del adquirente.
- `connection_type`: `ethernet`, `wifi`, `gprs`.

### Procesamiento de pagos
1. El billing-service recibe el `payment_method` seleccionado por el cliente.
2. Valida que el método esté habilitado para la sede.
3. Delega al `PaymentProvider` correspondiente.
4. Recibe la respuesta (success/failure + reference).
5. Actualiza el status de la invoice.

## Criterios de Aceptación
1. El admin puede habilitar/deshabilitar métodos de pago por sede.
2. Cada método tiene configuraciones específicas (POS provider, wallet, etc.).
3. Se pueden establecer montos mínimos y máximos por método.
4. El método por defecto se muestra primero en la UI del operador.
5. Solo los métodos habilitados están disponibles para procesar pagos.
6. El sistema delega al PaymentProvider correcto según el método seleccionado.

## Datos de Entrada
- `site_id` (UUID): Identificador de la sede.
- `payment_method` (string): Método — `cash`, `card`, `bank_transfer`, `digital_wallet`, `qr_pay`.
- `enabled` (boolean): Si el método está habilitado.
- `position` (int): Orden de prioridad en la UI del operador.
- `config` (JSON): Configuración específica del método.
- `minimum_amount`, `maximum_amount` (decimal, nullable): Límites de monto.
- `is_default` (boolean): Si es el método sugerido por defecto.

## Datos de Salida
- `site_payment_methods.id` (UUID): ID del método configurado.
- `site_payment_methods.site_id`, `payment_method`, `enabled`, `position` (mixed): Datos almacenados.
- `site_payment_methods.config` (JSON): Configuración específica.
- `site_payment_methods.minimum_amount`, `maximum_amount`, `is_default` (mixed): Límites y prioridad.
- Evento: `PAYMENT_METHOD_UPDATED` publicado tras el guardado.