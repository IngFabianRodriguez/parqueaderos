# SPEC-07-036 — Churn (Cancelación) y Retención de Datos por 90 Días

## Metadata
- **RF origen**: RF-036
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: billing-service, tenant-service, notification-service, data-retention-service

---

## User Story
**Como** administrador de ParkCore **quiero** que cuando un tenant cancele su suscripción sus datos se retengan durante 90 días **para** dar oportunidad de recuperación y cumplir con obligaciones legales de conservación de datos.

## Objetivo
El sistema debe manejar la cancelación (churn) de un tenant de forma que los datos se retengan por 90 días en modo solo lectura, pasado ese periodo los datos se eliminen de forma permanente.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Suscripción > "Cancelar suscripción"
2. Sistema muestra pantalla de confirmación con razón de cancelación
3. Tenant admin confirma; sistema actualiza status = canceled, canceled_at = NOW()
4. Sistema configura job programado para eliminación en NOW() + 90 días
5. Sistema genera evento tenant_churned
6. Durante 90 días: tenant_admin puede ver datos en solo lectura y exportar
7. Pasados 90 días: datos se eliminan permanentemente

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Tenant cancela con suscripción annual activa | Suscripción se cancela de inmediato |
| Durante los 90 días el admin intenta crear transacción | Retornar 403 "Tu cuenta está cancelada" |
| El tenant se reagota después de 90 días | No es posible; debe registrarse de nuevo |
| Job de eliminación falla | Reintentar la siguiente noche; alertar al equipo |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| cancellation_reason | string | Razón de cancelación | Sí |
| confirm_cancel | boolean | Confirmación explícita del admin | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| status | enum | canceled |
| canceled_at | datetime | Fecha y hora de cancelación |
| cancellation_reason | string | Razón seleccionada |
| data_deletion_date | datetime | Fecha de eliminación (canceled_at + 90 días) |
| days_until_deletion | integer | Días restantes antes de eliminación |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant puede iniciar cancelación desde el dashboard de Settings
2. La cancelación es inmediata; la suscripción de Stripe se cancela el mismo día
3. Los datos del tenant se retienen durante 90 días en modo solo lectura
4. Durante los 90 días, el tenant_admin puede exportar sus datos
5. La reactivación durante los 90 días restaura el acceso completo sin pérdida de datos
6. Después de 90 días, los datos se eliminan permanentemente

## Endpoints
- `POST /api/v1/tenants/{tenant_id}/cancel` — Cancelar suscripción
- `POST /api/v1/tenants/{tenant_id}/reactivate` — Reactivar durante periodo de retención
- `GET /api/v1/tenants/{tenant_id}/export` — Exportar datos antes de eliminación

## Health Check
- `GET /health` → { "status": "ok" }