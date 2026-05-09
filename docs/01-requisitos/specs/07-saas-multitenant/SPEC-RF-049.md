# SPEC-07-049 — Custom Domain para Tenants Enterprise+

## Metadata
- **RF origen**: RF-049
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: dns-service, tenant-service, cdn-service, ssl-service

---

## User Story
**Como** administrador de un tenant Enterprise **quiero** que mi equipo acceda al dashboard desde `parking.empresa.com` en lugar de `empresa.parkcore.co` **para** dar una experiencia más profesional y reforzar mi marca.

## Objetivo
El sistema debe permitir que los tenants de plan Enterprise o superior configuren un dominio personalizado (custom domain) para acceder a su dashboard. El sistema se encargará del provisionamiento automático de certificados SSL, la configuración DNS y el routing correcto al tenant.

## Comportamiento Específico

### Configuración del Custom Domain
1. Tenant admin accede a Settings > Branding > "Dominio personalizado"
2. Sistema muestra input para ingresar el subdomain (ej: `parking.empresa.com`)
3. Sistema valida que el plan permite custom domain
4. Sistema verifica que el dominio no está en uso por otro tenant
5. Sistema genera los registros DNS necesarios (CNAME + TXT para ACME)
6. Sistema muestra al tenant los registros que debe agregar
7. Tenant admin agrega los registros DNS en su proveedor
8. Sistema poll-ea el DNS cada 5 minutos para verificar propagación
9. Una vez propagado, sistema genera el certificado SSL via ACME (Let's Encrypt)
10. Sistema configura el CDN/proxy para routing
11. Sistema actualiza `tenant_domains` con `domain`, `ssl_status = active`, `verified_at`
12. Sistema genera evento `custom_domain_configured`
13. El tenant recibe email de confirmación

### Routing de Requests
1. Request llega a `https://parking.empresa.com/dashboard`
2. CDN/Proxy recibe el request; extrae el Host header
3. CDN resuelve el CNAME y enruta al servicio de ParkCore
4. El servicio identifica el tenant desde el dominio
5. Se aplica el branding del tenant y se sirve el dashboard

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Plan del tenant no permite custom domain | Mostrar error "Esta feature requiere plan Enterprise o superior" |
| Dominio ya en uso por otro tenant | Mostrar error 409; contactar a soporte |
| Registro DNS no propagado después de 24h | Enviar recordatorio al tenant; permitir revalidación manual |
| SSL renewal falla | Alertar al tenant; equipo de ParkCore resuelve manualmente |
| Tenant hace downgrade a plan inferior | Custom domain sigue activo hasta fin del ciclo; luego se desactiva |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| custom_domain | string | Dominio personalizado (subdomain.empresa.com) | Sí |
| ssl_enabled | boolean | Habilitar SSL automático (default: true) | Sí |
| tenant_id | UUID | Identificador del tenant | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| domain_id | UUID | Identificador del dominio configurado |
| custom_domain | string | Dominio configurado |
| cname_target | string | Destino CNAME que el cliente debe configurar |
| dns_records | array | Lista de registros DNS a configurar |
| ssl_status | enum | `pending`, `provisioning`, `active`, `failed` |
| verified_at | datetime | Fecha de verificación DNS |
| expires_at | datetime | Fecha de expiración del certificado SSL |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant Enterprise+ puede configurar hasta 3 custom domains
2. El SSL se genera automáticamente en menos de 10 minutos después de que los DNS están propagados
3. El dashboard del tenant es accesible desde `https://{custom_domain}` sin warnings de certificado
4. El custom domain usa el branding del tenant automáticamente
5. Si el SSL expira, el sistema renueva automáticamente sin intervención del tenant

## Endpoints
- `POST /api/v1/tenants/{tenant_id}/domains` — Configurar custom domain
- `GET /api/v1/tenants/{tenant_id}/domains` — Listar dominios configurados
- `DELETE /api/v1/tenants/{tenant_id}/domains/{domain_id}` — Eliminar custom domain
- `POST /api/v1/domains/validate` — Validar configuración DNS

## Health Check
- `GET /health` → { "status": "ok" }
