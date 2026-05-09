# SPEC-13-admin-panel-156 — El panel permite crear y gestionar descuentos y cupones que aplican a tickets...

## Metadata
- **RF origen**: RF-156
- **Módulo**: 13-admin-panel
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** admin de tenant **quiero** crear descuentos y cupones **para** ejecutar campañas comerciales y fidelizar clientes. ---

## Objetivo
El panel permite crear y gestionar descuentos y cupones que aplican a tickets de parqueadero. Se pueden definir por porcentaje o monto fijo, con límites de uso, vigencia, y condiciones específicas. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| (ninguno) | — | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Los cupones son únicos y case-insensitive. 2. Un cupón puede usarse una o múltiples veces según configuración. 3. Los cupones expirados no son aplicables. 4. El sistema registra cada uso con timestamp, cliente y ticket. 5. Un mismo cliente puede usar el mismo cupón según el límite por cliente. 6. El admin puede desactivar un cupón en cualquier momento. ---

## Endpoints
- (ninguno especificado)

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Se recomienda que los códigos sean fácil de recordar pero no predecibles. - Los descuentos deben verse reflejados en la factura del cliente.
