# SPEC-12-app-cliente-150 — El sistema debe enviar promociones y descuentos personalizados a los clientes...

## Metadata
- **RF origen**: RF-150
- **Módulo**: 12-app-cliente
- **Prioridad**: Alta
- **Servicios**: No especificados

---

## User Story
**Como** cliente **quiero** recibir promociones y descuentos personalizados según mi historial de uso **para** incentivarme a usar más el servicio y sentir que la marca me reconoce. ---

## Objetivo
El sistema debe enviar promociones y descuentos personalizados a los clientes basándose en su perfil de uso, frecuencia de visitas, y comportamiento. Las promociones aparecen en la app y pueden ser exclusivas por segmento (frecuentes, nuevos, inactivos). ---

## Comportamiento Específico

### Happy Path
1. El sistema ejecuta un job diario de evaluación de segmentos de clientes. 2. Por cada cliente, se determina su segmento: - **Nuevo**: Menos de 3 parqueos en los últimos 30 días. - **Frecuente**: Más de 10 parqueos al mes. - **Inactivo**: Sin parqueos en los últimos 45 días. - **Estándar**: El resto. 3. Se seleccionan las promociones activas del tenant que aplican para el segmento del cliente. 4. Las promociones se almacenan en la cola de entrega por canal configurado (push/email). 5. Se envían las notificaciones de promoción según las preferencias del cliente (RF-149). 6. El cliente abre la app y ve la sección "Ofertas" con las promociones disponibles. 7. El cliente pulsa sobre una promoción para ver el detalle: - Tipo de descuento (% o valor fijo). - Condiciones (duración, zonas, días aplicables). - Código de promoción o aplicación automática. - Vigencia (fecha de inicio y fin). 8. Al hacer un prepago (RF-143), si hay promoción aplicable, se muestra automáticamente para que el cliente elija si usarla o no. ---

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| (ninguno definido) | — |

## Datos de Entrada
| Campo | Tipo | Descripción | |-------|------|-------------| | promocion_id | UUID | Identificador | | nombre | string | Nombre de la promoción | | descripcion | string | Descripción | | tipo_descuento | string | Tipo de descuento | | valor_descuento | decimal | Valor del descuento | | codigo | string | Código promocional | | badge | string | Texto del badge (ej: "¡Nuevo!", "Solo hoy", "Inactivo") | | vigencia_hasta | date | Fecha de expiración | | aplicable | boolean | Si aplica al perfil actual del cliente | | razon_no_aplicable | string | Razón si no aplica (ej: "Monto mínimo $10,000") | ---

## Datos de Salida
| Campo | Tipo | Descripción | |-------|------|-------------| | promocion_id | UUID | Identificador | | nombre | string | Nombre de la promoción | | descripcion | string | Descripción | | tipo_descuento | string | Tipo de descuento | | valor_descuento | decimal | Valor del descuento | | codigo | string | Código promocional | | badge | string | Texto del badge (ej: "¡Nuevo!", "Solo hoy", "Inactivo") | | vigencia_hasta | date | Fecha de expiración | | aplicable | boolean | Si aplica al perfil actual del cliente | | razon_no_aplicable | string | Razón si no aplica (ej: "Monto mínimo $10,000") | ---

## Headers Injectados (del COMP-001)
- X-User-Id: UUID del usuario autenticado
- X-Rol: tenant_admin | sede_manager | operador | cliente
- X-Tenant-Id: UUID del tenant
- X-Sede-Id: UUID de la sede (si aplica)
- X-Trace-ID: UUID v4 para trazabilidad distributed
- X-Request-Timestamp: unix timestamp

## Criterios de Aceptación
1. El cliente ve las promociones activas aplicables a su segmento en la sección "Ofertas". 2. El sistema segmenta a los clientes en: nuevo, frecuente, inactivo, estándar. 3. Las promociones se muestran con su badge, descuento, vigencia y condiciones. 4. Durante el prepago (RF-143), se aplica automáticamente la promoción si cumple condiciones. 5. El cliente puede copiar el código de promoción o usarlo directamente. 6. Las notificaciones de promoción se envían según las preferencias del cliente (RF-149). 7. Se limita el uso de cada promoción según los parámetros configurados. 8. El historial de uso de promociones se registra para métricas y evitar duplicados. ---

## Endpoints
- `GET /api/v1/cliente/promociones` — Lista promociones disponibles para el cliente - `GET /api/v1/cliente/promociones/{promocion_id}` — Detalle de una promoción - `POST /api/v1/cliente/promociones/{promocion_id}/canjear` — Marca la promoción como usada - `GET /api/v1/cliente/segmento` — Obtiene el segmento actual del cliente ---

## Health Check
- `GET /health` → `{ "status": "ok" }`


## Notas

- El segmento se recalcula diariamente; un cliente frecuente que deja de usar el servicio eventual se reaclasifica a inactivo. - Las promociones no son stackables: solo se aplica una promoción por parqueo. - El sistema puede envíar "promociones de last call" cuando un cliente está por vencer pero aún no ha salido del parqueadero. - El código de promoción puede ingresarse manualmente en el checkout o aplicarse automáticamente si está configurado como tal.
