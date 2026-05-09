# SPEC-07-054 — Rotación y Revocación de API Keys

## Metadata
- **RF origen**: RF-054
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: api-gateway, auth-service, tenant-service

---

## User Story
**Como** administrador de un tenant **quiero** poder rotar y revoke mis API keys **para** mantener la seguridad de mis integraciones si una key se expone o si necesito cambiar los permisos.

## Objetivo
El sistema debe permitir que el tenant admin revoque una API key existente (inutilizándola inmediatamente) y rote una key (creando una nueva con los mismos scopes mientras la anterior se invalida). Ambos procesos deben ser inmediatos y generar eventos de auditoría.

## Comportamiento Específico

### Revocación
1. Tenant admin identifica la key a revocar en Settings > API Keys
2. Hace clic en "Revocar" (icono de papelera)
3. Sistema muestra modal de confirmación
4. Tenant admin confirma
5. Sistema marca `api_keys.status = revoked`, `revoked_at = NOW()`
6. Sistema genera evento `api_key_revoked` con `key_id`, `tenant_id`, `revoked_by`, `reason`
7. Sistema invalida cualquier caché de la key
8. El admin ve la key en la lista con estado `Revocada`

### Rotación
1. Tenant admin identifica la key a rotar; hace clic en "Rotar" (icono de flecha circular)
2. Sistema muestra modal con nombre de la key, scopes, checkbox de confirmación
3. Tenant admin confirma
4. Sistema genera nueva API key (mismo proceso que creación en RF-051)
5. Sistema marca la key anterior como `revoked`
6. Sistema muestra la nueva key completa **una sola vez**
7. Sistema genera evento `api_key_rotated` con `old_key_id`, `new_key_id`, `tenant_id`

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Revocar key que ya está en uso | La integración dejará de funcionar inmediatamente |
| Rotar key sin confirmar checkbox | El modal no se envía; se pide confirmación explícita |
| Revocar key que ya fue revocada | Mostrar error "Esta key ya está revocada" |
| La última key activa del tenant | Se permite revocar; el tenant puede crear una nueva |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| key_id | UUID | Identificador de la key a revocar/rotar | Sí |
| reason | string | Motivo de revocación (audit) | No |
| confirmation | boolean | Confirmación explícita del admin | Sí |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. La revocación de una key hace que cualquier request con esa key retorne 401 en menos de 1 segundo
2. La rotación crea una nueva key funcional con los mismos scopes que la anterior
3. La key anterior se invalida en el mismo momento que la nueva se genera
4. Los eventos `api_key_revoked` y `api_key_rotated` se generan con usuario, timestamp y key IDs
5. Las keys revocadas se mantienen en la base de datos para auditoría pero no se pueden usar

## Endpoints
- `DELETE /api/v1/api-keys/{key_id}` — Revocar key
- `POST /api/v1/api-keys/{key_id}/rotate` — Rotar key
- `GET /api/v1/api-keys` — Listar keys (incluye revocadas)

## Health Check
- `GET /health` → { "status": "ok" }
