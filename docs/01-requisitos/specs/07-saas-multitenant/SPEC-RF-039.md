# SPEC-07-039 — Tracking de Uso Excedente y Facturación al Cierre del Ciclo

## Metadata
- **RF origen**: RF-039
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: billing-service, usage-tracking-service, tenant-service

---

## User Story
**Como** administrador de ParkCore **quiero** que cuando un tenant exceda los límites de su plan se trackee el uso excedente y se incluya en la factura del mes **para** cobrar justamente por lo que se usa.

## Objetivo
El sistema debe trackear el uso de recursos de cada tenant en tiempo real, comparar con los límites de su plan, y al cierre del ciclo de facturación calcular los excedentes para agregarlos a la invoice mensual como cargos adicionales (overage).

## Comportamiento Específico

### Happy Path
1. Cada vez que ocurre un evento de uso, el servicio correspondiente incrementa el contador
2. El contador se almacena en tabla usage_metrics con: tenant_id, YYYY_MM, resource_type, count
3. Al acercarse al límite (80%), se envía notificación al tenant
4. Al cierre del ciclo: se calculan excedentes y se agregan a la invoice

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Límite de usuarios alcanzado | Permite crear el usuario y lo marca como overage |
| Plan sin límites (Custom) | No se aplica tracking de overage |
| Uso exactamente igual al límite | No hay overage; uso_percentage = 100% |
| Usage tracking falla | Contador se reconstruye batch desde los logs |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| resource_type | enum | Tipo: transactions, sedes, users, api_calls | Sí |
| increment | integer | Cantidad a incrementar | Sí |
| timestamp | datetime | Momento del evento | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| usage_current | integer | Uso actual del recurso |
| usage_limit | integer | Límite del plan |
| usage_percentage | decimal | Porcentaje de uso |
| overage_units | integer | Unidades excedentes (0 si no hay) |
| overage_charge | decimal | Cargo adicional por excedentes |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada evento de uso incrementa el contador en menos de 1 segundo
2. El contador de uso se muestra en el dashboard del tenant_admin
3. Se envía email de advertencia cuando el uso alcanza el 80% del límite
4. Al cierre del ciclo, los excedentes se calculan correctamente y se agregan a la invoice
5. La línea de invoice muestra: recurso excedido, unidades, precio unitario, total

## Endpoints
- `POST /api/v1/usage/track` — Incrementar contador de uso (interno)
- `GET /api/v1/tenants/{tenant_id}/usage` — Ver uso actual vs límites
- `GET /api/v1/usage/current` — Dashboard de uso en tiempo real

## Health Check
- `GET /health` → { "status": "ok" }