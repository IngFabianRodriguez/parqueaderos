# SPEC-07-060 — Email de Bienvenida al Crear la Cuenta

## Metadata
- **RF origen**: RF-060
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: notification-service, tenant-service, auth-service

---

## User Story
**Como** nuevo usuario de ParkCore **quiero** recibir un email de bienvenida al crear mi cuenta **para** saber qué hacer a continuación y tener una buena primera impresión de la plataforma.

## Objetivo
El sistema debe enviar un email transaccional de bienvenida al usuario founder inmediatamente después de que su cuenta tenant se cree exitosamente (RF-029). El email debe incluir instrucciones claras de próximo paso (verificar email, comenzar onboarding) y un link directo al wizard de onboarding.

## Comportamiento Específico

### Envío del Email
1. El tenant se crea exitosamente (RF-029)
2. El `auth-service` detecta el evento `tenant_created`
3. El servicio consulta el `tenant_branding` para usar el logo del tenant
4. Se prepara el email de bienvenida con template `welcome`:
   - Asunto: "¡Bienvenido a ParkCore, {nombre}! Completa tu configuración en 5 minutos."
   - Saludo con nombre del usuario
   - Instrucciones de próximo paso
   - Botón primario: "Verificar mi email" (link de verificación, RF-061)
   - Sección "Qué viene después": resumen del onboarding
5. El email se envía con tracking de apertura y clicks
6. Se genera evento `welcome_email_sent`

### Contenido del Email
- Asunto: "¡Bienvenido a ParkCore, {nombre}! Configura tu cuenta en 5 minutos"
- Botón "Verificar mi email" apuntando al link de verificación
- Pasos: 1. Verifica tu email (2 min), 2. Configura tu empresa y primera sede (5 min), 3. Invita a tu equipo y empieza a operar

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| El email es hard bounce | Marcar `users.email_bounced = true`; no enviar más emails a esta dirección |
| Soft bounce temporal | Reintentar con backoff exponencial (1h, 4h, 12h) |
| El usuario ya verificó su email | El botón de verificar no aparece; el email incluye link al dashboard |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El email de bienvenida se envía dentro de los 60 segundos posteriores a la creación del tenant
2. El email incluye el nombre del usuario y el nombre de su empresa
3. El botón "Verificar mi email" apunta al link de verificación (RF-061)
4. El email es responsive (legible en móvil)
5. El tracking de apertura y clicks está habilitado

## Endpoints
- Proceso batch triggered por `tenant_created`; no hay endpoint directo para el usuario

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant creado | Sí |
| user_id | UUID | Identificador del usuario founder | Sí |
| user_email | string | Email del usuario founder | Sí |
| user_name | string | Nombre del usuario founder | Sí |
| company_name | string | Nombre de la empresa del tenant | Sí |
| verification_token | string | Token único para verificar email | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| email_id | string | ID del email enviado (para tracking) |
| recipient | string | Email del destinatario |
| subject | string | Asunto del email |
| sent_at | datetime | Timestamp de envío |
| status | string | `sent`, `bounced`, `failed` |
| tracking_enabled | boolean | Si el tracking de apertura/clicks está activo |
| event | string | `welcome_email_sent` |

## Health Check
- `GET /health` → { "status": "ok" }
