# SPEC-07-044 — Integración con Stripe como Motor de Suscripciones y Billing

## Metadata
- **RF origen**: RF-044
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, stripe-integration, tenant-service

---

## User Story
**Como** administrador de ParkCore **quiero** usar Stripe como el motor de cobros y suscripciones **para** no tener que construir y mantener un sistema de pagos complejo y garantizar seguridad en el manejo de datos financieros.

## Objetivo
El sistema debe integrar Stripe como el único motor de procesamiento de pagos, suscripciones recurrentes, creación de customers, y manejo de métodos de pago. Toda la información sensible de tarjetas se almacena en Stripe (PCI compliance), nunca en la base de datos de ParkCore.

## Comportamiento Específico

### Creación del Customer y Suscripción
1. Cuando un tenant inicia el flujo de suscripción (RF-037), el sistema crea un Stripe Customer
2. Datos del customer: `email`, `name` (empresa), `metadata: { tenant_id }`
3. Se guarda el `stripe_customer_id` en la tabla `tenants`
4. El sistema crea una Stripe Subscription con: `customer`, `items`, `billing_cycle_anchor`, `trial_end`
5. Se guarda el `stripe_subscription_id` en la tabla `subscriptions`

### Checkout para Nuevos Tenants
1. El sistema crea un Stripe Checkout Session: `mode: 'subscription'`, `customer`, `line_items`
2. El tenant es redirigido a la página de checkout de Stripe
3. Al confirmar el pago, Stripe redirige al tenant a la URL de éxito de ParkCore
4. Stripe envía webhook `checkout.session.completed` al sistema
5. El sistema procesa el webhook; el tenant pasa a estado `active`

### Customer Portal para Tenants Existentes
1. El tenant accede a Settings > Suscripción > "Gestionar pago"
2. El sistema crea un Stripe Customer Portal Session para el `stripe_customer_id`
3. El tenant es redirigido al Stripe Customer Portal; desde ahí puede actualizar método de pago, ver invoices, cancelar suscripción

### Manejo de Métodos de Pago
1. Los métodos de pago se almacenan en Stripe como PaymentMethods
2. El sistema nunca almacena números de tarjeta en la base de datos
3. Para cobrar, el sistema usa `stripe.invoices.create()` y `stripe.invoices.pay()`

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Stripe no responde (API timeout) | Retry con exponential backoff (3 intentos); si falla, mostrar error al usuario |
| Tarjeta rechazada en checkout | Stripe muestra mensaje de error en su propia UI; el usuario puede reintentar |
| El customer ya existe en Stripe | Verificar por `stripe_customer_id` en tabla `tenants`; si existe, reutilizarlo |
| El precio del plan cambió en Stripe | El precio se toma del `price_id` en la tabla `plans`; el nuevo se usa en el siguiente ciclo |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| email | string | Email del tenant (para Stripe Customer) | Sí |
| empresa_nombre | string | Nombre de la empresa | Sí |
| plan_price_id | string | ID del precio del plan en Stripe | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| stripe_customer_id | string | ID del customer en Stripe |
| stripe_subscription_id | string | ID de la suscripción en Stripe |
| stripe_payment_method_id | string | ID del método de pago por defecto |
| billing_portal_url | string | URL del Stripe Customer Portal |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Todo tenant con suscripción activa tiene un `stripe_customer_id` en la tabla `tenants`
2. La creación de customer y suscripción en Stripe ocurre sin errores en > 99.5% de los casos
3. Los pagos se procesan sin que los datos de tarjeta pasen por los servidores de ParkCore
4. Las facturas generadas por Stripe son las mismas que se muestran en el invoice interno (mapeo 1:1)
5. El Stripe Customer Portal permite al tenant gestionar su suscripción sin asistencia
6. Si Stripe no responde, el sistema hace retry con backoff y no deja al usuario en estado inconsistente

## Endpoints
- `POST /api/v1/subscriptions/create-checkout` — Crear Stripe Checkout Session
- `POST /api/v1/subscriptions/portal` — Crear Stripe Customer Portal Session
- `POST /api/v1/webhooks/stripe` — Endpoint único para todos los webhooks de Stripe

## Health Check
- `GET /health` → { "status": "ok" }