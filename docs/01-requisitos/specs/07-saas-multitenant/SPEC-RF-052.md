# SPEC-07-052 — Scopes Granulares por API Key

## Metadata
- **RF origen**: RF-052
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: api-gateway, auth-service

---

## User Story
**Como** administrador de un tenant **quiero** asignar scopes específicos a cada API key **para** limitar qué operaciones puede realizar cada integración sin afectar otras.

## Objetivo
El sistema debe definir y aplicar scopes granulares sobre cada API key, de modo que una key solo pueda acceder a los endpoints y acciones específicos para los que fue autorizada. Cada endpoint del API declarará qué scope requiere, y el API Gateway validará que la key tenga ese scope antes de procesar el request.

## Comportamiento Específico

### Validación de Scopes
1. API Gateway recibe request con `Authorization: Bearer pk_live_xxx`
2. Se extrae la key y se buscan los `scopes` asociados
3. Se determina el scope requerido para el endpoint solicitado
4. Se verifica si `scope_requerido ∈ scopes_de_la_key`:
   - Si sí: request se procesa; se registra en `api_key_logs`
   - Si no: retorna 403 Forbidden con `{"error": "insufficient_scope", "required": "reservas:write", "message": "Esta API key no tiene permiso para crear reservas."}`

### Mapa de Scopes por Endpoint
| Método | Endpoint | Scope requerido |
|--------|----------|-----------------|
| GET | `/api/v1/disponibilidad` | `disponibilidad:read` |
| GET | `/api/v1/sedes` | `disponibilidad:read` |
| GET | `/api/v1/reservas` | `reservas:read` |
| POST | `/api/v1/reservas` | `reservas:write` |
| PUT | `/api/v1/reservas/{id}` | `reservas:write` |
| DELETE | `/api/v1/reservas/{id}` | `reservas:write` |
| GET | `/api/v1/transacciones` | `transacciones:read` |
| POST | `/api/v1/transacciones/ingreso` | `transacciones:write` |
| POST | `/api/v1/transacciones/salida` | `transacciones:write` |
| GET | `/api/v1/clientes` | `clientes:read` |
| POST | `/api/v1/clientes` | `clientes:write` |
| PUT | `/api/v1/clientes/{id}` | `clientes:write` |
| POST | `/api/v1/pagos` | `pagos:write` |
| GET | `/api/v1/reportes/*` | `reportes:read` |
| POST | `/api/v1/webhooks` | `webhooks:write` |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Key tiene scope `*` (todas) | Se expansiona a todos los scopes disponibles; acceso total |
| Endpoint sin scope definido | Por defecto requiere `admin:read`; se rejecciona hasta que se defina |
| Scope desconocido en la key | Se ignora; no causa error |
| Nuevo endpoint sin scope mapeado | El API Gateway retorna 500 hasta que se defina |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada endpoint del API tiene declarado el scope requerido en la configuración del API Gateway
2. Un request con una key que tiene el scope correcto pasa; la respuesta es normal
3. Un request con una key que falta el scope retorna 403 con el error de `insufficient_scope`
4. Los scopes se asignan a la key al momento de creación (RF-051) y se pueden editar al rotar

## Endpoints
- Todos los endpoints del API de ParkCore declaran su scope en el router del API Gateway

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| Authorization header | string | `Bearer pk_live_xxx` con la API key | Sí |
| scope_requerido | string | Scope necesario para el endpoint (ej: `reservas:write`) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| request_autorizado | boolean | `true` si la key tiene el scope requerido |
| error | object | Objeto de error con `code`, `required_scope`, `message` (solo si falla) |
| status_code | integer | 200 si autorizado, 403 si scope insuficiente |

## Health Check
- `GET /health` → { "status": "ok" }
