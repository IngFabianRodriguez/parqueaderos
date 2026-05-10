# SPEC-07-058 — Activación de Features Mediante Upgrade de Plan

## Metadata
- **RF origen**: RF-058
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, feature-flag-service, tenant-service, notification-service

---

## User Story
**Como** administrador de un tenant **quiero** que al hacer upgrade de mi plan las nuevas features se activen automáticamente **para** no tener que configurar nada adicional después de pagar.

## Objetivo
El sistema debe activar inmediatamente las features del nuevo plan cuando el upgrade se complete (después de confirmar el pago vía Stripe), sin necesidad de intervención manual.

## Comportamiento Específico

### Proceso de Activación
1. El tenant admin inicia upgrade desde Settings > Suscripción > "Hacer upgrade" (RF-040)
2. El sistema procesa el pago vía Stripe
3. Stripe envía webhook `customer.subscription.updated` o `invoice.payment_succeeded`
4. El billing-service recibe el webhook e identifica el nuevo plan
5. El billing-service actualiza `tenants.plan_id` al nuevo plan
6. El billing-service llama a `feature-flag-service.activatePlanFeatures(tenant_id, new_plan_id)`
7. El servicio de features:
   - Lee el mapa de `feature_flags` para el nuevo plan
   - Actualiza `tenant_features` con las nuevas features activas
   - Genera evento `features_activated` con lista de nuevas features
8. El sistema envía email al tenant admin con lista de nuevas features
9. El dashboard del tenant muestra los nuevos módulos sin necesidad de recarga

### Features Activadas por Upgrade
| Upgrade | Features nuevas activadas |
|---------|---------------------------|
| Starter → Professional | Multi-sede (3), BI Reportes, API Access, Overage billing |
| Professional → Enterprise | Multi-sede (ilimitado), SSO/SAML, Custom Domain, Flotas B2B, 50 usuarios, RPM 1,000 |
| Enterprise → Custom | White-label app, ilimitado todo, API RPM 10,000 |
| Starter → Enterprise | Todas las de Professional + Enterprise |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Pago de upgrade falla | No se activa el nuevo plan; el tenant permanece en el plan actual |
| El tenant está suspended | El upgrade no se procesa hasta que el tenant se reactive |
| El webhook llega duplicado | Si el plan ya es el nuevo, no se hace nada; idempotencia |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Al completar un upgrade, las features del nuevo plan están activas en menos de 10 segundos después del webhook
2. Las features nuevas aparecen en el dashboard sin necesidad de recargar la página
3. El email de confirmación incluye la lista de nuevas features desbloqueadas
4. El evento `features_activated` se genera con la lista de features añadidas
5. Las features del plan anterior siguen funcionando; no se pierden acceso a nada

## Endpoints
- `POST /api/v1/webhooks/stripe` — Confirmación de pago de upgrade
- `GET /api/v1/tenants/{tenant_id}/features` — Consulta de features activas post-upgrade

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant que hace upgrade | Sí |
| new_plan_id | string | Identificador del nuevo plan (ej: `professional`, `enterprise`) | Sí |
| stripe_subscription_id | string | ID de la suscripción en Stripe | Sí |
| payment_status | string | Estado del pago (`succeeded`, `failed`, `pending`) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| tenant_id | UUID | Identificador del tenant |
| previous_plan | string | Plan anterior |
| new_plan | string | Plan activado |
| features_activated | array[string] | Lista de features añadidas |
| activated_at | datetime | Timestamp de activación |
| email_sent | boolean | Si el email de confirmación fue enviado |
| event | string | `features_activated` |

## Health Check
- `GET /health` → { "status": "ok" }
