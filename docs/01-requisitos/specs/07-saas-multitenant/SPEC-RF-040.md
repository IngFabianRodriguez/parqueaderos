# SPEC-07-040 — Upgrade de Plan con Prorrateo Inmediato

## Metadata
- **RF origen**: RF-040
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, stripe-integration, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** hacer upgrade de mi plan y que el cobro sea inmediato y prorrateado **para** acceder a las nuevas features sin esperar al siguiente ciclo de facturación.

## Objetivo
El sistema debe procesar el upgrade de plan de un tenant de forma inmediata, calculando el prorrateo de los días no consumidos del plan actual y cobrando la diferencia para el resto del ciclo.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Suscripción > "Hacer upgrade"
2. Sistema muestra el plan actual y los planes disponibles con la diferencia de precio
3. Tenant admin selecciona el plan destino y confirma
4. Sistema calcula prorrateo: (precio_nuevo - precio_actual) * (dias_restantes / dias_total_ciclo)
5. Sistema crea Stripe Checkout Session para el cargo prorrateado
6. Al confirmar el pago, Stripe envía webhook invoice.payment_succeeded
7. Sistema actualiza subscriptions.plan_id al nuevo plan
8. Sistema activa los feature flags del nuevo plan

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Pago de upgrade falla | Tenant permanece en plan actual |
| Upgrade a Custom | Sistema muestra formulario de contacto con ventas |
| El plan destino tiene límite de sedes menor | Permitir upgrade; límite nuevo aplica |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| new_plan | enum | Plan destino (debe ser más caro que el actual) | Sí |
| billing_cycle | string | Ciclo del plan (monthly/annual) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| previous_plan | string | Plan que tenía antes |
| new_plan | string | Plan activado |
| amount_charged | decimal | Monto cobrado por el prorrateo |
| prorated_days | integer | Días prorrateados |
| effective_date | datetime | Fecha de inicio del nuevo plan |
| next_billing_date | datetime | Fecha del próximo cobro |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un upgrade de plan se procesa en menos de 10 segundos después de confirmar el pago
2. El monto cobrado corresponde exactamente al prorrateo
3. El nuevo plan y sus feature flags están activos inmediatamente después de confirmar el pago
4. La invoice muestra una línea de "Upgrade prorrateado"
5. El current_period_end no cambia; la próxima renovación sigue en la fecha original

## Endpoints
- `POST /api/v1/subscriptions/upgrade` — Iniciar upgrade
- `POST /api/v1/webhooks/stripe` — Confirmar pago de upgrade
- `GET /api/v1/tenants/{tenant_id}/subscription` — Consultar suscripción actual

## Health Check
- `GET /health` → { "status": "ok" }