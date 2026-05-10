# SPEC-07-062 — Asistente de Configuración de Primera Sede con Templates Predefinidos

## Metadata
- **RF origen**: RF-062
- **Módulo**: 07-saas-multitenant
- **Prioridad**: Media
- **Servicios**: onboarding-service, tenant-service, sede-service

---

## User Story
**Como** nuevo usuario de ParkCore **quiero** elegir un template predefinido para configurar mi primera sede **para** tener mi parqueadero listo en minutos sin necesidad de definir cada espacio manualmente.

## Objetivo
El sistema debe ofrecer un conjunto de templates predefinidos de configuración de sede (con zonas, tipos de espacio y cantidades recomendadas) para que el usuario pueda seleccionar uno durante el onboarding y aplicarlo con un solo clic.

## Templates Predefinidos

| Template | Zonas | Espacios Total |
|----------|-------|----------------|
| Básico | 1 (General/Descubierto) | 20 |
| Profesional | 2 (Cubierta, Exterior) | 40 |
| Corporativo | 3 (VIP, Cubierta, Exterior) | 80 |
| Aeropuerto / Centro Comercial | 4 (Principal, Cubierta, VIP, Moto) | 200 |
| Empezar desde cero | Definición manual | — |

## Comportamiento Específico

### Aplicación de Template
1. En el paso 3 del wizard (Zonas y Espacios), el sistema muestra los templates disponibles
2. El usuario ve una representación visual de cada template con preview de la distribución
3. El usuario selecciona un template y hace clic en "Aplicar"
4. El sistema aplica el template:
   - Crea las zonas definidas en el template
   - Para cada zona, crea los espacios con el tipo y cantidad especificados
   - Genera espacios con numeración automática (Zona A: A-01, A-02...; Zona B: B-01...)
5. El usuario ve la sede configurada y puede editar, añadir o eliminar zonas/espacios preconfigurados

### Visualización de Templates
Cada template se muestra como:
- Nombre y descripción
- Preview visual de la distribución de zonas y espacios
- Indicadores: número de zonas, número total de espacios

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Template produce más espacios que el límite del plan | Mostrar warning: "Este template excede el límite de tu plan" |
| El usuario modifica el template después de aplicar | Los cambios se guardan normalmente; ya no está vinculado al template |
| Template no disponible para el plan | No se muestra; solo los templates apropiados según el plan |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El sistema ofrece al menos 4 templates predefinidos más la opción de empezar desde cero
2. Cada template tiene una representación visual clara de la distribución de zonas
3. Al aplicar un template, las zonas y espacios se crean correctamente en la base de datos
4. El usuario puede modificar cualquier zona o espacio después de aplicar el template
5. Los templates disponibles se filtran según el plan del tenant

## Endpoints
- `GET /api/v1/templates/sede` — Listar templates de sede disponibles
- `POST /api/v1/sedes/{sede_id}/apply-template` — Aplicar un template a la sede

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| template_id | string | Identificador del template a aplicar (ej: `profesional`, `corporativo`) | Sí |
| sede_id | UUID | Identificador de la sede donde aplicar el template | Sí |
| tenant_id | UUID | Identificador del tenant (para validar límites del plan) | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| template_id | string | ID del template aplicado |
| template_name | string | Nombre del template (ej: "Profesional") |
| zones_created | array[object] | Lista de zonas creadas |
| zones_created[].id | UUID | ID de la zona creada |
| zones_created[].name | string | Nombre de la zona |
| zones_created[].spaces_count | integer | Cantidad de espacios en esta zona |
| total_spaces_created | integer | Total de espacios creados |
| spaces | array[object] | Lista de espacios creados con numeración |
| spaces[].id | UUID | ID del espacio |
| spaces[].zone_id | UUID | Zona a la que pertenece |
| spaces[].code | string | Código del espacio (ej: "A-01", "B-03") |
| spaces[].type | string | Tipo de espacio (ej: `cubierta`, `descubierto`, `vip`) |
| event | string | `template_applied` |
| warning | string | Warning si el template excede límites del plan (null si no hay) |

## Health Check
- `GET /health` → { "status": "ok" }
