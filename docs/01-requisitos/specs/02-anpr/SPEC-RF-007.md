# SPEC-02-007 — Manejar placas ilegibles con registro manual

## Metadata
- **RF origen**: RF-007
- **Módulo**: 02-anpr
- **Prioridad**: Alta
- **Servicios**: anpr-service, parking-service

---

## User Story
**Como** Operador de sede **quiero** registrar manualmente la placa cuando el sistema ANPR no puede leerla **para** permitir la entrada y salida de vehículos cuando el OCR falla, sin bloquear la operación.

## Objetivo
Cuando el sistema ANPR reporta una confianza de OCR inferior al umbral mínimo (70%) o cuando el operador detecta que la placa leída es incorrecta, el operador puede ingresar manualmente la placa. Este registro manual genera un registro equivalente a uno automático, con la diferencia de que el campo 'metodo_registro' se marca como 'manual' y se incluye el ID del operador que realizó el registro.

## Comportamiento Específico

### Happy Path
1. Sistema ANPR reporta placa con confianza < 70% o indica 'no_detectada'
2. Sistema muestra alerta en dashboard del operador con imagen de la placa
3. Operador verifica visualmente la placa y la ingresa manualmente en la app
4. Sistema recibe POST /api/v1/entradas/manual con placa, sede_id, operador_id
5. Sistema valida que no exista entrada activa duplicada para el mismo vehículo
6. Sistema crea registro de entrada con metodo_registro='manual' y operador_id
7. Sistema asigna espacio libre o, en salida, calcula tarifa normalmente
8. Talanquera se abre normalmente

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Placa ingresada no tiene formato válido | Se valida formato según normativa colombiana y se muestra error si no coincide |
| Entrada manual duplicada (mismo vehículo ya tiene entrada activa) | Se alerta al operador y se le pregunta si desea corregir o forzar |
| Operador intenta registro manual sin conexión | Se almacena en cola local y se sincroniza cuando haya conexión |
| Operador sin permisos de registro manual | Se deniega el acceso con 403 |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| placa | VARCHAR(20) | Placa ingresada manualmente por el operador | Sí |
| sede_id | UUID | Identificador de la sede | Sí |
| tipo_registro | VARCHAR | 'entrada' o 'salida' | Sí |
| operador_id | UUID | ID del operador que realiza el registro manual | Sí |
| imagen_evidencia | BINARY | Captura de la placa para auditoría | No |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| registro_id | UUID | — |
| placa | VARCHAR | — |
| metodo_registro | VARCHAR | manual |
| operador_id | UUID | — |
| timestamp | TIMESTAMP | — |

## Headers Injectados (del COMP-001)
- X-User-Id: UUID
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID
- X-Trace-ID: UUID v4

## Criterios de Aceptación
1. Registro manual es rastreable hasta el operador específico que lo creó
2. Todos los registros manuales incluyen evidencia fotográfica
3. El sistema no permite más del 10% de registros manuales sobre automáticos (para detectar problemas de ANPR)

## Endpoints
- `POST /api/v1/entradas/manual` — Registro manual de entrada
- `POST /api/v1/salidas/manual` — Registro manual de salida

## Health Check
- `GET /health` → { "status": "ok" }

## Notas
- Formato válido de placa colombiana: letras (A-Z), números (0-9), guiones permitidos. Regex: `^[A-Z]{3}[0-9]{3}$` o `^[A-Z]{3}[0-9]{2}[A-Z]{1}$`
- El porcentaje de registros manuales se calcula como: (manuales / total_registros) * 100 en ventana de 24h
- Si el ratio manual excede 10%, se genera alerta al administrador de sede para revisar cámaras
- El operador debe tener rol 'operador' para poder hacer registros manuales
- En modo offline, los registros se almacenan en SQLite local y se sincronizan con el endpoint RF-008