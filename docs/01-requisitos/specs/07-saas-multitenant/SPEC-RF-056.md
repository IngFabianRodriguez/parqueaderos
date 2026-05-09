# SPEC-07-056 — Feature Flags por Plan del Tenant

## Metadata
- **RF origen**: RF-056
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: tenant-service, feature-flag-service, auth-service

---

## User Story
**Como** administrador de un tenant **quiero** que las features exclusivas de mi plan estén disponibles y las de planes superiores estén ocultas o bloquedas **para** que mi equipo use solo lo que está incluido en mi suscripción.

## Objetivo
El sistema debe definir un mapa de feature flags asociadas a cada plan (Starter, Professional, Enterprise, Custom), activando automáticamente las features incluidas en el plan del tenant y desactivando las que no corresponden. El acceso a una feature no autorizada debe retornar error 403.

## Mapa de Feature Flags por Plan
| Feature | Starter | Professional | Enterprise | Custom |
|---------|---------|--------------|------------|--------|
| Multi-sede | ❌ | ✅ (3 max) | ✅ (ilimitado) | ✅ |
| BI y Reportes avanzados | ❌ | ✅ | ✅ | ✅ |
| API Access | ❌ | ✅ | ✅ | ✅ |
| SSO / SAML | ❌ | ❌ | ✅ | ✅ |
| White-label app | ❌ | ❌ | ❌ | ✅ |
| Custom domain | ❌ | ❌ | ✅ | ✅ |
| Overage billing | ❌ | ✅ | ✅ | ✅ |
| Flotas B2B | ❌ | ❌ | ✅ | ✅ |
| API rate limit (RPM) | 60 | 300 | 1,000 | 10,000 |
| Usuarios max | 3 | 10 | 50 | Ilimitado |
| Sedes max | 1 | 3 | Ilimitado | Ilimitado |
| Transacciones/mes | 1,000 | 10,000 | 100,000 | Ilimitado |

## Comportamiento Específico

### Carga de Features
1. Al cargar el dashboard o hacer login, el sistema consulta `GET /api/v1/tenants/{tenant_id}/features`
2. El servicio retorna la lista de features activas para el plan del tenant
3. El frontend muestra/oculta módulos según la lista
4. Al intentar acceder a una feature no incluida:
   - El frontend puede deshabilitar el botón desde el inicio
   - Si se hace request directo al endpoint, el API Gateway verifica el feature flag y retorna 403

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Feature flag no existe para un plan | Asumir `false`; loguear warning |
| Plan del tenant es null | Asumir Starter; no permitir acceso a ninguna feature premium |
| Tenant hace downgrade | Las features del plan anterior se desactivan inmediatamente |
| Feature de trial vs paid | Los tenants en trial tienen acceso a todas las features de su plan |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada plan tiene definidas todas sus features en `feature_flags`; no hay features indefinidas
2. Las features del plan se cargan al iniciar sesión y se cachean por 5 minutos
3. Los endpoints de features no incluidas retornan 403 con mensaje claro y link a upgrade
4. El downgrade de plan desactiva las features que ya no corresponden inmediatamente

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/features` — Obtener features activas del tenant
- `GET /api/v1/plans` — Listar todos los planes y sus features (público)

## Health Check
- `GET /health` → { "status": "ok" }
