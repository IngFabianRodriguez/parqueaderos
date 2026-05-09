# SPEC-07-034 — Aislamiento Completo de Datos Entre Tenants

## Metadata
- **RF origen**: RF-034
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Crítica
- **Servicios**: todos los servicios (database layer, api-gateway, auth-service)

---

## User Story
**Como** administrador de un tenant **quiero** estar seguro de que mis datos son invisibles para todos los demás tenants **para** proteger la confidencialidad de mi información de negocio.

## Objetivo
El sistema debe garantizar que los datos de cada tenant están completamente aislados unos de otros, tanto a nivel de base de datos (RLS), como a nivel de aplicación (middleware de tenant), y a nivel de red.

## Comportamiento Específico

### Happy Path
1. Todo request HTTP pasa por el middleware de autenticación
2. El middleware extrae el tenant_id del JWT
3. El middleware inyecta el tenant_id en el contexto de la request
4. Cada handler de API recibe el contexto con el tenant_id y lo usa en todas las queries
5. PostgreSQL RLS filtra rows WHERE tenant_id = current_setting('app.tenant_id')

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| JWT sin tenant_id claim | Retornar 401 Unauthorized |
| Token JWT válido pero tenant_id no existe en DB | Retornar 401; invalidar token |
| Request intenta modificar recurso de otro tenant | Retornar 403; registrar en auditoría de seguridad |
| Query intenta acceder a tabla sin tenant_id | RLS retorna 0 rows; se alerta al equipo de desarrollo |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| JWT token | string | Token JWT con claim tenant_id | Sí |
| Recurso solicitado | string | Tipo de recurso (transaction, client, sede) | Sí |
| ID del recurso | UUID | Identificador del recurso específico | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| Datos solicitados | any | Datos del recurso solo si pertenece al tenant del solicitante |
| Error 403 | JSON | Mensaje de acceso denegado |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada tabla en el schema tiene columna tenant_id not null con índice B-tree
2. PostgreSQL RLS está habilitado y configurado en todas las tablas del schema de negocio
3. Un query hecho con tenant_id = A retorna 0 rows si el recurso pertenece a tenant_id = B
4. El middleware de tenant retorna 403 si el JWT no contiene tenant_id
5. Los eventos de Kafka usan tenant_id como key de partición
6. Un intento de acceso cruzado genera un evento de seguridad con datos de diagnóstico

## Endpoints
- Todos los endpoints de la API requieren tenant_id en el contexto

## Health Check
- `GET /health` → { "status": "ok" }