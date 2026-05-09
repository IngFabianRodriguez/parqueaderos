# SPEC-07-033 — Múltiples Usuarios por Tenant

## Metadata
- **RF origen**: RF-033
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: auth-service, tenant-service, user-service

---

## User Story
**Como** administrador de un tenant **quiero** invitar a mis colaboradores (managers, operadores) a mi cuenta **para** que puedan gestionar el parqueadero conmigo con sus propios accesos individuales.

## Objetivo
El sistema debe permitir que cada tenant tenga múltiples usuarios, cada uno con rol específico dentro de la organización del tenant, credenciales independientes y acceso exclusivamente a los recursos que su rol permita.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Usuarios > "Invitar usuario"
2. Ingresa: nombre completo, email, rol (manager, operador, auditor)
3. Sistema valida que el email no esté registrado en otro tenant
4. Sistema valida que el plan permite la cantidad de usuarios (Starter 3, Professional 10, Enterprise 50)
5. Sistema crea usuario con status = pending_invitation
6. Sistema envía email de invitación con enlace: /invite/{token}
7. Usuario hace clic en enlace y crea contraseña
8. Sistema genera sesión JWT y redirige al dashboard

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Email ya existe en otro tenant | Retorna error 409 |
| Plan no permite más usuarios | Retorna error 403 |
| Invitación no aceptada en 7 días | Se marca como expired; admin puede reenviar |
| Admin intenta invitarse a sí mismo | Error "Ya tienes acceso completo como admin" |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| nombre_completo | string(100) | Nombre del usuario a invitar | Sí |
| email | string(255) | Email del usuario | Sí |
| rol | enum | Rol: tenant_admin, manager, operador, auditor | Sí |
| sedes_asignadas | array[UUID] | Lista de sedes a las que tiene acceso | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| user_id | UUID | Identificador del usuario creado |
| email | string | Email del usuario |
| rol | string | Rol asignado |
| status | enum | pending_invitation, active, disabled |
| invitation_sent_at | datetime | Fecha en que se envió la invitación |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant_admin puede crear hasta el número de usuarios permitido por su plan
2. Cada usuario tiene credenciales independientes (email + contraseña)
3. Un mismo email no puede pertenecer a dos tenants distintos
4. Los usuarios ven exclusivamente las sedes y módulos que su rol permite
5. La invitación expira a los 7 días si no es aceptada

## Endpoints
- `POST /api/v1/tenants/{tenant_id}/users` — Crear usuario invitado
- `GET /api/v1/tenants/{tenant_id}/users` — Listar usuarios del tenant
- `PUT /api/v1/tenants/{tenant_id}/users/{user_id}` — Editar rol o estado
- `DELETE /api/v1/tenants/{tenant_id}/users/{user_id}` — Eliminar usuario
- `POST /api/v1/invitations/{token}/accept` — Aceptar invitación

## Health Check
- `GET /health` → { "status": "ok" }