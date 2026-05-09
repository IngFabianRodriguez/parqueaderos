# SPEC-11-app-operador-132 — Cuando un operador tiene asignadas varias sedes (multisede), la app debe most...

## Metadata
- **RF origen**: RF-132
- **Módulo**: 11-app-operador
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** operador con acceso a múltiples sedes **quiero** cambiar rápidamente entre sedes desde la app **para** gestionar diferentes parqueaderos sin cerrar sesión ni cambiar de usuario. ---

## Objetivo
Cuando un operador tiene asignadas varias sedes (multisede), la app debe mostrar un selector de sede accesible desde cualquier pantalla principal. Este selector permite cambiar la sede activa con un solo toque, actualizando instantáneamente todos los datos visibles (dashboard, talánqueras, alertas). El operador permanece autenticado; solo cambia el contexto de sede. ---

## Comportamiento Específico

### Happy Path
1. El operador toca el nombre de la sede actual en la barra superior de la app. 2. Se despliega el selector de sede (bottom sheet o modal). 3. El selector muestra: nombre de sede, dirección resumida, y un indicador de estado (activa/inactiva). 4. El operador toca la sede destino. 5. El sistema valida que el operador aún tiene acceso a esa sede. 6. La app cambia el contexto a la nueva sede y carga el dashboard correspondiente. 7. Se cierra el selector y se muestra confirmación visual del cambio. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | UUID | ID de la sede activa | | nombre | String | Nombre de la sede | | direccion | String | Dirección resumida | | estado | Enum | ACTIVA, INACTIVA, SUSPENDIDA | | espacios_total | Integer | Total de espacios de la sede | | es_default | Boolean | Si es la sede principal del operador | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | sede_id | UUID | ID de la sede activa | | nombre | String | Nombre de la sede | | direccion | String | Dirección resumida | | estado | Enum | ACTIVA, INACTIVA, SUSPENDIDA | | espacios_total | Integer | Total de espacios de la sede | | es_default | Boolean | Si es la sede principal del operador | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El selector de sede es visible en la barra superior de la app. 2. Al tocar el selector, se despliega la lista de sedes asignadas al operador. 3. El cambio de sede se ejecuta en menos de 1 segundo. 4. Al cambiar de sede, el dashboard refleja los datos de la nueva sede. 5. Las talánqueras mostradas corresponden a la sede activa. 6. Las alertas corresponden a la sede activa. 7. Un operador con una sola sede no ve el selector. 8. Las sedes inactivas se muestran deshabilitadas y no son seleccionables. 9. El estado del selector se preserva entre sesiones (última sede seleccionada). ---

## Endpoints
- `GET /api/v1/operator/sedes` — Lista de sedes asignadas al operador - `POST /api/v1/operator/sede/active` — Registra el cambio de sede activa - `GET /api/v1/operator/sede/{id}/summary` — Resumen rápido de la sede ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El selector nunca debe desaparecer; si el operador tiene más de una sede, siempre debe ser accesible. - En la bottom sheet se debe mostrar también el avatar/nombre del operador para contexto visual. - El cambio de sede NO cierra sesión ni reinicia la app; es un cambio de contexto únicamente. - Se debe evitar que el operador pueda "perderse" al cambiar de sede; el flujo siempre lleva al dashboard de la nueva sede.
