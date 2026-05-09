# SPEC-03-010 — Registrar clientes naturales y empresas con placas asociadas

## Metadata
- **RF origen**: RF-010
- **Módulo**: 03-crm-pagos
- **Prioridad**: Alta
- **Servicios**: crm-service

---

## User Story
Como Cliente (registro), Operador (registro asistido) **quiero** registrar un cliente en el sistema con sus datos personales y las placas de sus vehículos asociados **para** permitir que el sistema reconozca al cliente en ingresos futuros y aplique tarifación preferente si corresponde.

## Objetivo
Crear y mantener un registro completo del cliente que incluya: tipo (persona natural o empresa), datos de identificación, información de contacto, y lista de placas asociadas. El cliente puede tener múltiples vehículos registrados y un perfil de tarifación especial.

## Comportamiento Específico
### Happy Path
1. Cliente u operador inicia registro desde app móvil o panel admin
2. Sistema recibe POST /api/v1/clientes con datos del cliente
3. Sistema valida que el documento no exista en otro cliente activo
4. Sistema crea registro en tabla cliente
5. Sistema vincula las placas ingresadas creando registros en placa_asociada
6. Si cliente tiene plan prepago, se crea wallet con saldo inicial 0
7. Sistema retorna cliente_id y confirmación

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Documento ya existe | Retorna 409 con los datos del cliente existente y opción de actualizar |
| Cliente empresa sin NIT verificado | Se crea pero con estado 'pendiente_verificacion' |
| Más de 5 placas por cliente | Se permite hasta 10, más de eso requiere aprobación del admin |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| tipo_cliente | VARCHAR | natural o empresa | Sí |
| documento | VARCHAR | Cédula o NIT | Sí |
| nombre | VARCHAR | Nombre completo o Razón Social | Sí |
| email | VARCHAR | Correo electrónico | Sí |
| telefono | VARCHAR | Teléfono de contacto | Sí |
| placas | ARRAY | Array de placas a asociar | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| cliente_id | UUID | — |
| documento | VARCHAR | — |
| nombre | VARCHAR | — |
| placas_count | INTEGER | — |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Documento único por tenant (no duplicado)
2. Placa validada contra formato colombiano antes de asociar
3. Cliente queda inmediatamente activo tras el registro

## Endpoints
- `POST /api/v1/clientes` — Registrar cliente con placas asociadas

## Health Check
- `GET /health` → `{ "status": "ok", "service": "crm-service" }`

## Notas
- Formato placa colombiana: 3 letras + 3 números (ej: ABC123). Se valida con regex `/^[A-Z]{3}[0-9]{3}$/`.
- Wallet se crea con saldo inicial 0 al registrar cliente, no al hacer la primera recarga.
- Cliente persona natural: documento = CC (cédula ciudadanía). Cliente empresa: documento = NIT.