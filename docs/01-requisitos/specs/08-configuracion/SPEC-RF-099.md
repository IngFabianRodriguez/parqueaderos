# SPEC-08-configuracion-099 — El sistema debe permitir a los administradores de tenant configurar, para el ...

## Metadata
- **RF origen**: RF-099
- **Módulo**: 08-configuracion
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** administrador de tenant **quiero** configurar qué campos son obligatorios u opcionales al registrar una entrada manual de vehículo **para** adaptar el flujo de registro a las necesidades operativas del estacionamiento y cumplir con regulaciones locales. ---

## Objetivo
El sistema debe permitir a los administradores de tenant configurar, para el registro manual de entrada de vehículos (cuando el operador captura la placa o datos manualmente en la app), cuáles campos son obligatorios y cuáles opcionales. Los campos configurables incluyen: placa, tipo de vehículo, color, marca, foto del vehículo, identificación del conductor, y observación. Esta configuración permite flexibilidad entre estacionamientos que requieren más datos (para auditoría) vs. los que priorizan velocidad (mínimo dato posible). ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | config_id | uuid | Identificador | | profile_name | string | Nombre del perfil | | applies_to | enum | Alcance | | fields | array | Lista de campos con configuración | | required_fields_count | integer | Número de campos obligatorios | | enabled_fields_count | integer | Número de campos habilitados | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | config_id | uuid | Identificador | | profile_name | string | Nombre del perfil | | applies_to | enum | Alcance | | fields | array | Lista de campos con configuración | | required_fields_count | integer | Número de campos obligatorios | | enabled_fields_count | integer | Número de campos habilitados | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. Un administrador puede crear múltiples perfiles de configuración de campos. 2. Los campos soportados son: placa, tipo de vehículo, color, marca, modelo, foto, ID conductor, nombre, teléfono, observación, puesto, suscripción. 3. Cada campo puede ser: obligatorio, opcional, o deshabilitado. 4. Se puede asignar un perfil a todas las zonas o a zonas específicas. 5. La validación de campos obligatorios se ejecuta antes de guardar la entrada. 6. Las regex de validación se aplican y muestran errores inline. 7. Los cambios en la configuración no afectan entradas ya registradas. 8. La configuración de campos se refleja en la app del operador al siguiente registro. 9. El sistema provee al menos un perfil por defecto no modificable ("Minimum") con solo placa obligatoria. ---

## Endpoints
- `GET /api/v1/tenants/{tenant_id}/entry-field-configs` — Listar configuraciones - `POST /api/v1/tenants/{tenant_id}/entry-field-configs` — Crear configuración - `PUT /api/v1/tenants/{tenant_id}/entry-field-configs/{id}` — Actualizar configuración - `DELETE /api/v1/tenants/{tenant_id}/entry-field-configs/{id}` — Eliminar configuración - `GET /api/v1/zones/{zone_id}/entry-field-config` — Obtener config para una zona - `GET /api/v1/operators/me/entry-fields?zone_id={id}` — Obtener config para operador ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- En estacionamientos de alto flujo, se recomienda "Fast mode" (solo placa + tipo). - En estacionamientos que requieren auditoría, se recomienda "Full audit" (todos los campos obligatorios). - La foto del vehículo es útil para resolver disputas de daños. - El campo "Identificación del conductor" es requerido en algunas regulaciones locales. - Los regex de validación de placa deben considerar el formato local (ej: ABC-1234 en Colombia).
