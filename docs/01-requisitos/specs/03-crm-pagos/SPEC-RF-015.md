# SPEC-03-015 — Gestionar descuentos, cupones y programas de lealtad

## Metadata
- **RF origen**: RF-015
- **Módulo**: 03-crm-pagos
- **Prioridad**: Media
- **Servicios**: billing-service, crm-service

---

## User Story
Como Admin del tenant o Cliente **quiero** aplicar descuentos y cupones a mis pagos de parqueo **para** atraer clientes, fidelizar y hacer promociones estacionales.

## Objetivo
El sistema debe permitir crear y gestionar: (1) descuentos manuales aplicados por el operador en caja, (2) cupones canjeables con código alfanumérico, (3) programas de lealtad que acumulan puntos. Cada descuento tiene reglas de validez y se aplica al cálculo del precio antes del pago.

## Comportamiento Específico
### Happy Path (Cliente canjea cupón)
1. Cliente presenta código de cupón (en app, por email, o diciéndolo al operador)
2. Sistema busca cupón por código
3. Sistema valida: activo, dentro de fecha, no ha alcanzado límite, cliente aplicable
4. Si válido: descuento aplicado al precio
5. Uso del cupón incrementado
6. Comprobante refleja el descuento aplicado

### Happy Path (Programa de lealtad - acumulación)
1. Cliente realiza pago (RF-011)
2. Sistema determina si el cliente participa del programa de lealtad
3. Sistema calcula puntos ganados: (monto_pesos / 1000) * puntos_por_mil configured
4. Sistema acredita puntos a la cuenta del cliente
5. Notificación enviada confirmando puntos ganados

### Happy Path (Canje de puntos)
1. Cliente decide canjear puntos en app o en caja
2. Sistema muestra opciones de redención (descuentos, parqueo gratis, etc.)
3. Cliente selecciona
4. Sistema genera cupón temporal o aplica directamente
5. Descuento aplicado al pago

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Cupón expirado | Mensaje claro: "Este cupón venció el [fecha]" |
| Cupón con usos agotados | Mensaje: "Este cupón ya no tiene usos disponibles" |
| Cupón de descuento % con monto mayor al precio | Se aplica solo hasta dejar el precio en 0 (no se devuelve) |
| Descuento manual sin observación | Sistema no permite guardar sin observación (auditoría) |
| Puntos de lealtad canjeados pero cliente sin puntos suficientes | Validación prevents redemption, muestra puntos actuales y requeridos |
| Cupón intentando usarse dos veces en la misma transacción | Sistema solo permite uno por sesión |

## Datos de Entrada
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| nombre | VARCHAR | Nombre de la promoción | Sí |
| tipo | VARCHAR | porcentaje, valor_fijo, puntos_lealtad | Sí |
| codigo | VARCHAR | Código alfanumérico (unique) | No (generado si no ingresa) |
| valor | DECIMAL | Porcentaje o valor fijo en COP | Sí |
| fecha_inicio | DATE | — | Sí |
| fecha_fin | DATE | — | Sí |
| uso_maximo | INTEGER | Límite global de usos (null = ilimitado) | No |
| uso_maximo_por_cliente | INTEGER | — | No |
| minimo_compra | DECIMAL | Monto mínimo para aplicar | No |
| aplicable_a | VARCHAR | all, clientes_nuevos, clientes_frecuentes, corporativo | Sí |
| punto_kg | DECIMAL | Puntos ganados por cada 1000 COP (lealtad) | No |
| activo | BOOLEAN | — | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| descuento_id | UUID | — |
| codigo | VARCHAR | — |
| tipo | VARCHAR | — |
| valor | DECIMAL | — |
| monto_descuento | DECIMAL | Calculado para esta sesión |
| puntos_ganados | INTEGER | Si aplica programa de lealtad |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. Cada descuento aplicado queda registrado con: sesión, operador, tipo, valor, observación
2. Un cupón no puede ser usado más veces que su `uso_maximo`
3. Solo un cupón puede aplicarse por sesión (no acumulativo)
4. Descuentos manuales siempre tienen observación obligatoria
5. El precio final después de descuento nunca es negativo

## Endpoints
- `POST /api/v1/descuentos` — Crear descuento/cupón
- `GET /api/v1/descuentos` — Listar descuentos activos
- `PUT /api/v1/descuentos/{descuento_id}` — Editar descuento
- `DELETE /api/v1/descuentos/{descuento_id}` — Desactivar cupón
- `POST /api/v1/descuentos/validar` — Validar si un código es aplicable (para UI)
- `POST /api/v1/descuentos/aplicar` — Aplicar cupón a una sesión

## Health Check
- `GET /health` → `{ "status": "ok", "service": "billing-service" }`

## Notas
- Cupones con código deben tener al menos 8 caracteres para evitar brute force.
- Programa de puntos: configurable la relación pesos → puntos. Ejemplo: 1 punto por cada 1000 COP gastados.
- Umbral de redención mínimo: 5000 puntos = $5000 COP descuento.
- Los puntos no expiran dentro del año calendario, pero pueden tener expiry si el admin lo configura.