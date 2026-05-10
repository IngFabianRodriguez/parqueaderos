# SPEC-07-051 — Generación de API Keys por Tenant

## Metadata
- **RF origen**: RF-051
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: api-gateway, auth-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** generar API keys para que mi sistema externo (app de clientes, integración con ERP, dashboard propio) pueda conectarse a ParkCore **para** automatizar operaciones, consultar datos y realizar acciones programáticamente sin usar el dashboard web.

## Objetivo
El sistema debe permitir que cada tenant genere una o múltiples API keys desde su panel de administración, donde cada key tenga un nombre descriptivo, fecha de creación, y los permisos (scopes) que la key puede usar. Las keys se usan para autenticar requests al API de ParkCore con el formato `Bearer <api_key>`.

## Comportamiento Específico

### Creación de API Key
1. Tenant admin accede a Settings > API Keys > "Nueva API Key"
2. Sistema muestra formulario: Nombre, Scopes (checklist), Expira en (opcional), IP whitelist (opcional)
3. Tenant admin completa y hace clic en "Crear"
4. Sistema genera la API key: 32 bytes random codificados en base64url con prefijo `pk_live_`
5. Sistema calcula SHA-256 hash para almacenamiento
6. Sistema muestra la key completa **una sola vez**
7. Sistema genera evento `api_key_created`

### Uso de API Key
1. Sistema externo hace request con header `Authorization: Bearer pk_live_xxx`
2. API Gateway extrae la key, busca por hash, verifica tenant_id, scopes, expiración, IP whitelist
3. Si todo OK: permite el request, inyecta `tenant_id` y `scopes` en el contexto
4. Si falla: retorna 401 Unauthorized

### Listado y Revocación
1. Tenant admin ve lista de keys: nombre, scopes, creación, último uso, expiración
2. Puede revoke key, rotar key (crea nueva con mismos scopes, invalida anterior), ver logs de uso

### Límites por Plan
| Plan | API Keys permitidas |
|------|---------------------|
| Starter | 2 |
| Professional | 5 |
| Enterprise | 20 |
| Custom | Ilimitado |

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Key mostrada al admin por segunda vez | No se puede recuperar; debe crear nueva y rotar |
| Plan no permite más keys | Error 403 con mensaje de límite y opción de upgrade |
| Key vencida | Retorna 401; el admin debe rotar la key |
| Request desde IP no whitelist | Retorna 403 "IP no autorizada para esta key" |
| Key roubada o expuesta | El admin la revoca inmediatamente |

## Scopes Disponibles
| Scope | Descripción |
|-------|-------------|
| `disponibilidad:read` | Consultar espacios disponibles |
| `reservas:read` | Leer reservas |
| `reservas:write` | Crear/cancelar reservas |
| `transacciones:read` | Leer transacciones |
| `transacciones:write` | Registrar ingresos/salidas manualmente |
| `clientes:read` | Leer datos de clientes |
| `clientes:write` | Crear/editar clientes |
| `pagos:read` | Leer información de pagos |
| `pagos:write` | Procesar pagos |
| `reportes:read` | Acceder a reportes |
| `webhooks:write` | Configurar webhooks |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant admin puede crear hasta el número de API keys permitido por su plan
2. La API key se muestra solo una vez al momento de la creación; después solo se ve metadata
3. Cada key tiene scopes granulares que limitan qué endpoints puede usar
4. Las keys pueden tener expiración opcional; keys vencidas se rechazan con 401
5. Las keys pueden tener IP whitelist opcional
6. Un admin puede revoke una key en cualquier momento

## Endpoints
- `POST /api/v1/api-keys` — Crear nueva API key
- `GET /api/v1/api-keys` — Listar keys del tenant
- `DELETE /api/v1/api-keys/{key_id}` — Revocar key
- `POST /api/v1/api-keys/{key_id}/rotate` — Rotar key
- `GET /api/v1/api-keys/{key_id}/usage` — Ver logs de uso

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| name | string | Nombre descriptivo de la API key (ej: "App iOS Production") | Sí |
| scopes | array[string] | Lista de scopes permitidos (ej: `["disponibilidad:read", "reservas:write"]`) | Sí |
| expires_at | datetime | Fecha de expiración opcional (null = nunca expira) | No |
| ip_whitelist | array[string] | Lista de IPs permitidas opcional (null = cualquier IP) | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | UUID | Identificador único de la API key |
| name | string | Nombre descriptivo asignado |
| key_prefix | string | Primeros 8 caracteres de la key (`pk_live_xxx...`) |
| key_full | string | API key completa (solo se muestra una vez al crear) |
| scopes | array[string] | Scopes asignados |
| created_at | datetime | Timestamp de creación |
| expires_at | datetime | Fecha de expiración (null si no expira) |
| last_used_at | datetime | Último uso (null si nunca se usó) |
| status | string | `active`, `revoked`, `expired` |

## Health Check
- `GET /health` → { "status": "ok" }
