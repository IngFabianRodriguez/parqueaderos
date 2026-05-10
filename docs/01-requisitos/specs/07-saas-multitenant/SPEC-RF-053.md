# SPEC-07-053 — Rate Limits por API Key Según el Plan del Tenant

## Metadata
- **RF origen**: RF-053
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: api-gateway, rate-limit-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** conocer los límites de requests por minuto que aplica a cada API key **para** diseñar mis integraciones dentro de esos límites y escalar mi uso si necesito más.

## Objetivo
El sistema debe definir rate limits por API key basados en el plan del tenant, aplicando límites diferentes según el plan (Starter, Professional, Enterprise, Custom). Cada API key tendrá un límite de requests por minuto (RPM) y por mes (RPMonth), y el API Gateway rechazará requests que excedan esos límites con código 429 Too Many Requests.

## Rate Limits por Plan
| Plan | Requests por Minuto (RPM) | Requests por Mes |
|------|---------------------------|------------------|
| Starter | 60 | 10,000 |
| Professional | 300 | 100,000 |
| Enterprise | 1,000 | 1,000,000 |
| Custom | 10,000 | Ilimitado |

## Límites Adicionales por Scope
| Scope | % del rate limit total aplicable |
|-------|----------------------------------|
| `disponibilidad:read` | 30% del total |
| `transacciones:write` | 20% del total |
| `pagos:write` | 10% del total |
| Otros scopes | 40% del total |

## Comportamiento Específico

### Aplicación de Rate Limit
1. API Gateway recibe request con `Authorization: Bearer pk_live_xxx`
2. Se extrae la key; se buscan rate limits asociados al plan del tenant
3. Se verifica si la key tiene un override de rate limit
4. Se determina la ventana de rate limit (`window = 60 segundos`)
5. Se incrementa el contador en Redis: `rate_limit:{key_id}:{window}` con TTL 60s
6. Se compara `count` vs `limit`:
   - Si count <= limit: request pasa; se añaden headers
   - Si count > limit: request rechaza con 429

### Headers de Respuesta
- `X-RateLimit-Limit`: límite de la ventana (ej: 300)
- `X-RateLimit-Remaining`: requests restantes (limit - count)
- `X-RateLimit-Reset`: timestamp Unix de fin de ventana
- `Retry-After`: solo presente en 429, segundos hasta retry

### Response 429 (Excedió rate limit)
```json
{
  "error": "rate_limit_exceeded",
  "message": "Has excedido el límite de requests por minuto. Espera 30 segundos.",
  "limit": 300,
  "retry_after": 30,
  "plan": "Professional",
  "upgrade_url": "https://app.parkcore.co/settings/subscription"
}
```

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Límite de RPM alcanzado | Retorna 429; el cliente debe esperar y reintentar después de `Retry-After` |
| Límite mensual alcanzado | Retorna 429 con mensaje diferente: "Límite mensual alcanzado" |
| Límite por scope excedido | Retorna 429 específico: "Scope transacciones:write excedido" |
| Redis caído (no puede contar) | Fail-open: permitir el request; loguear alerta |
| Plan del tenant cambia (upgrade) | Los rate limits se recalculan con los del nuevo plan |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada request al API Gateway incrementa el contador de rate limit de la key correspondiente
2. Cuando el contador alcanza el límite, el siguiente request retorna 429 sin procesar
3. Los headers de rate limit se incluyen en todas las respuestas
4. Los rate limits se basan en el plan del tenant

## Endpoints
- Todos los endpoints del API de ParkCore pasan por el middleware de rate limiting

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| Authorization header | string | `Bearer pk_live_xxx` con la API key | Sí |
| tenant_plan | string | Plan del tenant (`Starter`, `Professional`, `Enterprise`, `Custom`) | Sí |
| key_id | UUID | Identificador de la API key para tracking de uso | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| X-RateLimit-Limit | integer | Límite de requests en la ventana actual |
| X-RateLimit-Remaining | integer | Requests restantes en la ventana actual |
| X-RateLimit-Reset | integer | Timestamp Unix de fin de la ventana |
| Retry-After | integer | Segundos hasta poder hacer nuevo request (solo en 429) |
| status_code | integer | 200 si OK, 429 si rate limit excedido |
| error | object | Objeto de error con `rate_limit_exceeded`, `message`, `limit`, `retry_after`, `plan`, `upgrade_url` |

## Health Check
- `GET /health` → { "status": "ok" }
