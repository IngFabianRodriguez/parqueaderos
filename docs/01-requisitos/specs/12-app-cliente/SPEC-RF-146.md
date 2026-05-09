# SPEC-12-app-cliente-146 — El sistema debe permitir al cliente registrar y gestionar sus métodos de pago...

## Metadata
- **RF origen**: RF-146
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** añadir métodos de pago como tarjeta, Nequi o Daviplata y definir uno como predeterminado **para** poder pagar mis parqueos de forma rápida sin tener que ingresar los datos cada vez. ---

## Objetivo
El sistema debe permitir al cliente registrar y gestionar sus métodos de pago desde la app. El cliente puede registrar tarjetas de crédito/débito, cuentas Nequi y Daviplata. Debe poder tener múltiples métodos y designar uno como predeterminado para cobros automáticos. ---

## Comportamiento Específico

### Happy Path
1. (flujo no especificado)

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | metodo_pago_id | UUID | Identificador del método | | tipo | string | 'tarjeta', 'nequi', 'daviplata' | | nombre | string | Nombre para mostrar (ej: "Visa ...4242", "Nequi **1234") | | ultimos_digitos | string | Últimos 4 dígitos (tarjeta) o últimos 4 del teléfono | | esta_default | boolean | Si es el método predeterminado | | marca | string | Marca de la tarjeta (Visa, Mastercard) | | estado | string | 'activo' o 'inactivo' | | fecha_agregado | timestamp | Fecha de registro | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | metodo_pago_id | UUID | Identificador del método | | tipo | string | 'tarjeta', 'nequi', 'daviplata' | | nombre | string | Nombre para mostrar (ej: "Visa ...4242", "Nequi **1234") | | ultimos_digitos | string | Últimos 4 dígitos (tarjeta) o últimos 4 del teléfono | | esta_default | boolean | Si es el método predeterminado | | marca | string | Marca de la tarjeta (Visa, Mastercard) | | estado | string | 'activo' o 'inactivo' | | fecha_agregado | timestamp | Fecha de registro | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente puede agregar hasta 5 métodos de pago. 2. El cliente puede eliminar un método de pago. 3. El cliente puede designar cualquier método activo como predeterminado. 4. Las tarjetas se tokenizan (no se almacena el número completo). 5. Los métodos Nequi y Daviplata se validan mediante código SMS. 6. Al agregar la primera tarjeta, esta se marca automáticamente como default. 7. El método default se usa automáticamente para renovaciones (RF-144) y prepagos (RF-143). 8. El cliente ve solo los últimos 4 dígitos del número de tarjeta/teléfono en la lista. ---

## Endpoints
- `GET /api/v1/cliente/metodos-pago` — Lista los métodos de pago del cliente - `POST /api/v1/cliente/metodos-pago` — Agrega un nuevo método - `DELETE /api/v1/cliente/metodos-pago/{metodo_pago_id}` — Elimina un método - `PUT /api/v1/cliente/metodos-pago/{metodo_pago_id}/default` — Define el método default - `POST /api/v1/pasarela/validar-tarjeta` — Validación y tokenización de tarjeta - `POST /api/v1/pasarela/enviar-codigo` — Envía código de verificación Nequi/Daviplata - `POST /api/v1/pasarela/verificar-codigo` — Verifica el código recibido ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El número de tarjeta completo nunca se almacena en nuestra base de datos; solo el token devuelto por la pasarela. - Las transacciones futuras se cobran usando el token sin necesidad de volver a ingresar datos de tarjeta. - Para Nequi/Daviplata, el número de teléfono actúa como identificador de la cuenta.
