# SPEC-08-configuracion-098 — El sistema debe permitir a los administradores de tenant personalizar el orde...

## Metadata
- **RF origen**: RF-098
- **Módulo**: 08-configuracion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de tenant **quiero** poder cambiar el orden de las secciones en la app móvil del operador **para** priorizar las funciones más usadas y adaptar la interfaz a los flujos de trabajo específicos de cada estacionamiento. ---

## Objetivo
El sistema debe permitir a los administradores de tenant personalizar el orden de las secciones principales de la app móvil del operador. Las secciones configurables incluyen: Dashboard/Resumen, Registro de Entrada, Registro de Salida, Búsqueda de Vehículos, Historial, y Configuración. Cada operador puede ver el orden configurado por su administrador de tenant al iniciar sesión. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | layout_id | uuid | Identificador | | profile_name | string | Nombre del perfil | | sections | array | Lista ordenada de secciones | | default_section | string | Sección por defecto | | show_icons | boolean | Iconos visibles | | compact_mode | boolean | Modo compacto | | active | boolean | Si es el perfil activo | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | layout_id | uuid | Identificador | | profile_name | string | Nombre del perfil | | sections | array | Lista ordenada de secciones | | default_section | string | Sección por defecto | | show_icons | boolean | Iconos visibles | | compact_mode | boolean | Modo compacto | | active | boolean | Si es el perfil activo | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Un administrador puede reordenar las secciones de la app del operador. 2. Las secciones disponibles son: Dashboard, Entrada, Salida, Búsqueda, Historial, Bloqueados, Reportes, Configuración, Ayuda. 3. Se pueden crear múltiples perfiles de layout (ej: "Rápido", "Supervisor"). 4. Se puede asignar un perfil como activo para el tenant. 5. Los operadores ven el nuevo orden al reabrir la app o tras notificación de actualización. 6. Se puede ocultar secciones completas para operadores que no las necesitan. 7. La sección por defecto se puede cambiar. 8. El layout se aplica por tenant, pero puede overridarse por rol de operador. 9. Se soportan cambios de layout en tiempo real sin necesidad de actualizar la app. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/app-layouts` — Listar layouts - `POST /api/v1/tenants/{tenant_id}/app-layouts` — Crear layout - `PUT /api/v1/tenants/{tenant_id}/app-layouts/{id}` — Actualizar layout - `DELETE /api/v1/tenants/{tenant_id}/app-layouts/{id}` — Eliminar layout - `POST /api/v1/tenants/{tenant_id}/app-layouts/{id}/activate` — Activar layout - `GET /api/v1/operators/me/app-layout` — Obtener layout para el operador actual ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- Los perfiles de layout permiten tener diferentes configuraciones para diferentes roles de operador. - El "Modo compacto" reduce el espacio visual de cada sección para mostrar más información. - Los badges/contadores en las secciones (ej: "3 vehículos bloqueados") requieren sync en background. - Se recomienda que la sección de Entrada sea la primera para operadores de alta rotación. - Los cambios de layout son atómicos: o se aplica todo el nuevo orden o se mantiene el anterior.
