# SPEC-07-050 — White-Label de la App Móvil para Tenants Custom

## Metadata
- **RF origen**: RF-050
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: branding-service, mobile-app-service, tenant-service, app-store-service

---

## User Story
**Como** administrador de un tenant Custom **quiero** que la app móvil de ParkCore se distribuya en las tiendas de apps con mi nombre, mi logo y mis colores **para** que mis clientes piensen que es una app propia de mi empresa.

## Objetivo
El sistema debe permitir que tenants de plan Custom personalicen la app móvil de ParkCore (la app del cliente final, no la del operador) con su marca: nombre de la app, ícono, colores, splash screen, y la publiquen en Apple App Store y Google Play Store bajo la cuenta del tenant.

## Comportamiento Específico

### Configuración de White-Label
1. Tenant admin accede a Settings > Branding > "App Móvil White-Label"
2. Sistema verifica que el plan es Custom; si no lo es, muestra error y sugiere upgrade
3. Sistema muestra el toolkit de white-label: guía de assets, templates, checklist
4. Tenant admin ingresa: App name, Bundle ID / Package name, Ícono (1024x1024px PNG), Splash screen (2732x2732px), Colores, Deep linking scheme
5. Sistema valida los assets (formato, tamaño)
6. Sistema genera el proyecto de app personalizado: descarga código base, inyecta assets, compila builds para iOS (.ipa) y Android (.aab)
7. Sistema entrega al tenant los archivos binarios listos para subir a las tiendas
8. Tenant sube los binarios a Apple App Store Connect y Google Play Console

### Actualizaciones de la App
1. Cuando ParkCore libera una nueva versión de la app base, el sistema notifica al tenant admin
2. El tenant admin puede descargar el nuevo código base y repetir el proceso de personalización

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Plan del tenant no es Custom | Mostrar error "White-label requiere plan Custom" |
| App name ya existe en App Store | El tenant debe elegir otro nombre |
| Ícono no cumple requisitos (tiene alpha) | Rechazar con mensaje específico |
| Credenciales de Apple no son válidas | Mostrar error 401; el tenant debe corregir |
| El tenant no tiene cuenta de desarrollador | Se le provee documentación de cómo crear una |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| app_name | string | Nombre de la app en las tiendas (máx 30 caracteres) | Sí |
| bundle_id | string | Bundle ID de iOS (ej: `co.parkingplus.app`) | Sí |
| package_name | string | Package name de Android | Sí |
| icon_file | file | Ícono 1024x1024px PNG sin alpha | Sí |
| splash_file | file | Splash screen 2732x2732px | Sí |
| deep_link_scheme | string | Esquema de deep linking (ej: `parkingplus`) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| build_ready | boolean | Si los binarios están listos para subir |
| ios_build_path | string | Ruta al archivo `.ipa` compilado |
| android_build_path | string | Ruta al archivo `.aab` compilado |
| bundle_id | string | Bundle ID configurado |
| package_name | string | Package name configurado |
| build_version | string | Versión del build (v1.0.0) |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Un tenant Custom puede descargar los binarios de la app base con sus assets personalizados
2. Los binarios resultantes muestran el nombre, ícono y colores del tenant desde el primer uso
3. La app white-label pasa el proceso de revisión de Apple App Store y Google Play
4. El tenant puede actualizar la app cuando ParkCore libera nuevas versiones del código base
5. Los deep links de la app usan el esquema custom en lugar de `parkcore://`

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/white-label/download` — Descargar código base y toolkit
- `POST /api/v1/white-label/validate-assets` — Validar assets antes de compilar
- `GET /api/v1/white-label/build-status` — Consultar estado del build

## Health Check
- `GET /health` → { "status": "ok" }
