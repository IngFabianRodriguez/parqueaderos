# SPEC-07-047 — Aplicación de Branding del Tenant en el Dashboard del Operador

## Metadata
- **RF origen**: RF-047
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: branding-service, frontend-service, tenant-service

---

## User Story
**Como** operador de un tenant **quiero** ver el dashboard con los colores y logo de mi empresa **para** que la experiencia se sienta propia y no como una herramienta genérica.

## Objetivo
El sistema debe aplicar dinámicamente el branding configurado (logo, color primario, color secundario) del tenant en todas las pantallas del dashboard que ven los operadores y usuarios del tenant, incluyendo la barra superior, botones primarios, acentos visuales y favicon.

## Comportamiento Específico

### Happy Path
1. El operador accede a `https://{slug}.parkcore.co/dashboard`
2. El frontend consulta `GET /api/v1/tenants/{tenant_id}/branding` para obtener logo y colores
3. El frontend inyecta el branding dinámicamente:
   - Barra superior muestra el logo del tenant (izquierda)
   - CSS variables (`--primary-color`, `--secondary-color`) se establecen con los valores del tenant
   - `<link rel="icon">` se actualiza con el logo del tenant
4. Todos los componentes del dashboard leen las CSS variables para sus estilos
5. El branding se cachea en el navegador por 1 hora
6. Si el operador cambia de sede dentro del mismo tenant, el branding persiste

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Branding no configurado | Usar valores por defecto: logo ParkCore, #2563EB, #1E40AF |
| logo_url retorna 404 | Mostrar logo default de ParkCore; loguear warning |
| Logo carga lento (> 2s) | Mostrar placeholder con iniciales del tenant hasta que cargue |
| Colores no tienen contraste WCAG AA | Permitir guardar pero mostrar warning de accesibilidad |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tenant_id | UUID | Identificador del tenant | Sí |
| session_token | string | Token JWT de la sesión del operador | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| logo_url | string | URL del logo del tenant |
| primary_color | string | Color primario (#RRGGBB) |
| secondary_color | string | Color secundario (#RRGGBB) |
| favicon_url | string | URL del favicon (mismo logo en 32x32) |
| tenant_name | string | Nombre de la empresa del tenant |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El logo del tenant aparece en la barra superior del dashboard en menos de 1 segundo después de cargar
2. Los botones primarios del dashboard usan el `primary_color` del tenant
3. Los acentos y bordes usan el `secondary_color` del tenant
4. El favicon del navegador se actualiza con el logo del tenant
5. Los cambios de branding se reflejan inmediatamente sin necesidad de recargar la página
6. El branding es consistente en todas las páginas del dashboard del tenant

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/branding` — Obtener branding del tenant
- `GET /api/v1/assets/{asset_id}` — Servir logo con Cache-Control

## Health Check
- `GET /health` → { "status": "ok" }
