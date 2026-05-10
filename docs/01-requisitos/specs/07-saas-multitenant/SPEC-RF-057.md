# SPEC-07-057 — Error 403 al Acceder Feature No Incluida en el Plan

## Metadata
- **RF origen**: RF-057
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: api-gateway, feature-flag-service, tenant-service

---

## User Story
**Como** operador de un tenant con plan Starter **quiero** ver un mensaje claro cuando intento acceder a una feature no incluida en mi plan **para** entender qué necesito hacer para desbloquearla y no pensar que es un error del sistema.

## Objetivo
El sistema debe retornar un error HTTP 403 (Forbidden) con cuerpo JSON estructurado cuando un tenant intente acceder a una feature, módulo o endpoint que no esté incluido en su plan. El mensaje debe ser claro, orientador y proporcionar un camino de upgrade.

## Comportamiento Específico

### Respuesta de Error 403
```json
{
  "error": "feature_not_included",
  "code": "PLAN_FEATURE_REQUIRED",
  "message": "Esta funcionalidad requiere un plan superior.",
  "feature": "bi_reportes",
  "feature_name": "Reportes Avanzados de BI",
  "current_plan": "Starter",
  "required_plan": "Professional",
  "upgrade_url": "/settings/subscription/upgrade",
  "can_trial": false,
  "contact_sales_url": "/contact-sales"
}
```

### Frontend Modal
1. El frontend recibe el 403 y muestra un modal:
   - Título: "Feature no disponible en tu plan"
   - Descripción: "Los Reportes Avanzados de BI están disponibles en el plan Professional o superior"
   - Botón principal: "Hacer upgrade a Professional"
   - Botón secundario: "Ver todos los planes"
2. Se genera evento `feature_access_denied` en `events_saas` para tracking de demanda

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Request directo al API (sin UI) | Retorna el JSON de error 403; el cliente debe manejarlo |
| Feature no existe en la base de datos | Retorna 404, no 403 |
| Feature de Enterprise+ sin plan Enterprise | El `upgrade_url` apunta al checkout del plan Enterprise; `contact_sales_url` también presente |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada endpoint o feature no incluida en el plan retorna HTTP 403 con cuerpo JSON estructurado
2. El mensaje de error incluye: nombre de la feature, plan requerido, y URL de upgrade
3. El frontend muestra un modal informativo y no solo un error genérico
4. El evento `feature_access_denied` se genera para métricas de demanda de features
5. Si la feature requiere plan Custom, se incluye `contact_sales_url` además del `upgrade_url`

## Endpoints
- Todos los endpoints que correspondan a features con feature flags
- `GET /api/v1/tenants/{tenant_id}/features` — Consulta de features activas

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| feature_id | string | Identificador de la feature que se intenta acceder | Sí |
| tenant_plan | string | Plan actual del tenant | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| error | string | `feature_not_included` |
| code | string | `PLAN_FEATURE_REQUIRED` |
| message | string | Mensaje legible: "Esta funcionalidad requiere un plan superior." |
| feature | string | Identificador de la feature bloqueada |
| feature_name | string | Nombre visible de la feature (ej: "Reportes Avanzados de BI") |
| current_plan | string | Plan actual del tenant |
| required_plan | string | Plan mínimo necesario (ej: `Professional`) |
| upgrade_url | string | URL para hacer upgrade (ej: `/settings/subscription/upgrade`) |
| can_trial | boolean | Si hay trial disponible para esta feature |
| contact_sales_url | string | URL de contacto con ventas (solo para planes Custom) |
| status_code | integer | Siempre 403 Forbidden |

## Health Check
- `GET /health` → { "status": "ok" }
