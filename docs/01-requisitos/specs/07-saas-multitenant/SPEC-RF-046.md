# SPEC-07-046 — Configuración de Branding por Tenant (Logo, Colores)

## Metadata
- **RF origen**: RF-046
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Alta
- **Servicios**: branding-service, tenant-service, asset-service

---

## User Story
**Como** administrador de un tenant **quiero** configurar mi logo, color primario y color secundario **para** que la plataforma refleje la identidad visual de mi empresa en todos los puntos de contacto.

## Objetivo
El sistema debe permitir que cada tenant personalice su identidad visual (logo, color primario, color secundario) desde su panel de administración, almacenando estos assets de forma segura y sirviéndolos dinámicamente en todas las interfaces donde aparezca el branding del tenant.

## Comportamiento Específico

### Happy Path
1. Tenant admin accede a Settings > Branding
2. Sistema muestra formulario con: campo de logo (upload), selector de color primario (hex), selector de color secundario (hex), preview en tiempo real
3. Tenant admin sube imagen de logo → validación formato (PNG, JPG, SVG), tamaño (máx 2MB), dimensiones (mín 128x128px, máx 512x512px)
4. Si pasa validación: se sube a storage con path `branding/{tenant_id}/logo.{ext}`; se genera URL pública
5. Tenant admin selecciona colores usando picker
6. Sistema guarda en `tenant_branding`: `tenant_id`, `logo_url`, `primary_color`, `secondary_color`, `updated_at`
7. Sistema genera preview en tiempo real
8. Tenant admin hace clic en "Guardar cambios"
9. Sistema actualiza y genera evento `branding_updated`
10. El branding se aplica instantáneamente en todas las interfaces del tenant

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Logo no es PNG/JPG/SVG | Rechazar con error "Formato no soportado. Usa PNG, JPG o SVG." |
| Logo excede 2MB | Rechazar con error "El archivo excede el límite de 2MB." |
| Logo muy pequeño (<128px) | Rechazar con error "La imagen debe ser mínimo 128x128 píxeles." |
| Color hex inválido | Rechazar con error "Color inválido. Usa formato hex (#RRGGBB)." |
| Tenant no configura branding | Se usan valores por defecto (logo ParkCore, #2563EB y #1E40AF) |
| Storage no disponible | Retornar 503; el usuario puede reintentar |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| logo_file | file | Imagen PNG/JPG/SVG (máx 2MB, 128x128 a 512x512px) | No (default: logo ParkCore) |
| primary_color | string | Color primario en hex (#RRGGBB) | Sí (default: #2563EB) |
| secondary_color | string | Color secundario en hex (#RRGGBB) | Sí (default: #1E40AF) |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| logo_url | string | URL pública del logo almacenado |
| primary_color | string | Color primario configurado |
| secondary_color | string | Color secundario configurado |
| preview_url | string | URL de preview renderizado del branding |
| updated_at | datetime | Timestamp de última modificación |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El tenant admin puede subir un logo y seleccionar colores desde Settings > Branding
2. El logo se almacena en storage con URL pública accesible
3. Los colores y logo se guardan en la tabla `tenant_branding` y se sirven en todas las pantallas del tenant
4. El preview en tiempo real muestra cómo se verá el dashboard antes de guardar
5. Los cambios se aplican inmediatamente después de guardar (< 2 segundos)
6. Si el tenant no tiene branding configurado, se usan los valores por defecto de ParkCore

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/branding` — Obtener branding actual
- `PUT /api/v1/tenants/{tenant_id}/branding` — Actualizar branding (logo + colores)
- `POST /api/v1/assets/upload` — Subir logo al storage

## Health Check
- `GET /health` → { "status": "ok" }
