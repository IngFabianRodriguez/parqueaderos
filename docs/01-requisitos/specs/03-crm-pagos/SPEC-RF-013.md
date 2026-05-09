# SPEC-03-013 — Gestionar planes tarifarios (por minuto, hora, diario, mensual, corporativo)

## Metadata
- **RF origen**: RF-013
- **Módulo**: 03-crm-pagos
- **Prioridad**: Alta
- **Servicios**: billing-service, availability-service

---

## User Story
Como Admin del tenant o Sistema **quiero** definir y aplicar tarifas concretas a cada sesión de parqueo **para** que el cliente pague el valor correcto según el tiempo de uso, tipo de espacio y condiciones especiales (hora pico, nocturno, corporativo).

## Objetivo
El sistema debe permitir al tenant_admin configurar planes tarifarios completos con reglas de cálculo de precio final. Cada plan define: tipo de cobro (por minuto, por hora, diario, mensual, corporativo), fracciones de cobro, topes máximos, y multiplicadores para condiciones especiales.

## Comportamiento Específico
### Happy Path (Cálculo en salida - precio final)
1. Vehículo sale (RF-006), sistema obtiene hora de entrada y hora actual
2. Sistema recalcula duración exacta
3. Sistema aplica fracción de cobro del plan (ej: primero 60 min, luego cada 15 min)
4. Si duración excede tope diario, aplica tarifa plana diaria
5. Si es hora pico (configurado): aplica multiplicador
6. Si es nocturno (23:00-06:00): aplica tarifa nocturna si existe
7. Sistema aplica descuentos vigentes (RF-015) si aplica
8. Precio final guardado en sesión

### Edge Cases
| Escenario | Comportamiento |
|-----------|----------------|
| Sin plan configurado para zona | Usa plan fallback global (configurable, default $50/min). Alerta al admin |
| Vehículo con plan corporativo pero contrato expirado | Trata como cliente esporádico con plan default |
| Fracción incompleta al final (ej: 47 min en plan de 15 min) | Cobra una fracción adicional completa |
| Tope diario excedido | Fija en el valor del tope |
| Plan hourly con frac_minima=60, cliente estuvo 45 min | Cobra $3000 (mínimo 1 hora) |

## Datos de Entrada (Plan Tarifario)
| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| nombre | VARCHAR | Nombre del plan | Sí |
| tipo | VARCHAR | minute, hour, day, monthly, corporate | Sí |
| sede_id | UUID | FK a sede (null = todas) | No |
| zona_id | UUID | FK a zona (null = todas las de la sede) | No |
| frac_minima_minutos | INTEGER | Mínimo de minutos facturados | Sí |
| frac_incremento_minutos | INTEGER | Incremento después del mínimo | Sí |
| precio_fraccion | DECIMAL | Valor a cobrar por cada fracción | Sí |
| precio_fraccion_adicional | DECIMAL | Valor por cada incremento adicional | Sí |
| tope_maximo | DECIMAL | Tarifa máxima por día/mes | No |
| multiplicador_hora_pico | DECIMAL | Multiplicador en horas pico (ej: 1.5) | No |
| hora_pico_inicio | TIME | HH:MM inicio hora pico | No |
| hora_pico_fin | TIME | HH:MM fin hora pico | No |
| precio_nocturno | DECIMAL | Tarifa nocturna fija (opcional) | No |
| activo | BOOLEAN | — | Sí |

## Datos de Salida
| Campo | Tipo | Descripción |
|-------|------|-------------|
| plan_tarifario_id | UUID | — |
| nombre | VARCHAR | — |
| tipo | VARCHAR | — |
| precio_final | DECIMAL | Calculado para la sesión |
| fracciones | INTEGER | Número de fracciones cobradas |
| duracion_minutos | INTEGER | Tiempo total en minutos |

## Headers Injectados (del COMP-001)
- X-User-Id, X-Rol, X-Tenant-Id, X-Sede-Id, X-Trace-ID, X-Request-Timestamp

## Criterios de Aceptación
1. El cálculo de precio es determinístico: misma duración + mismo plan = mismo precio
2. Fracciones siempre se cobran completas (no se prorratea la última fracción)
3. Multiplicadores se aplican correctamente según horario configurado
4. Topes máximos se respetan (nunca se cobra más del tope por período)
5. El precio calculado queda registrado en la sesión para auditoría

## Endpoints
- `POST /api/v1/tarifas/planes` — Crear plan tarifario
- `GET /api/v1/tarifas/planes` — Listar planes (filtrable por sede)
- `PUT /api/v1/tarifas/planes/{plan_id}` — Editar plan
- `DELETE /api/v1/tarifas/planes/{plan_id}` — Desactivar plan
- `GET /api/v1/tarifas/calcular?sesion_id=X` — Calcular precio actual (estimado) para una sesión
- `GET /api/v1/tarifas/calcular?placa=X&sede_id=Y&duracion_min=Z` — Estimar precio sin sesión activa

## Health Check
- `GET /health` → `{ "status": "ok", "service": "billing-service" }`

## Notas
- Fracción de cobro más común en Colombia: "primera hora o fracción, luego cada 15 minutos" → frac_minima=60, frac_incremento=15.
- Tarifa en COP. $3000 COP ≈ $0.75 USD.
- Multiplicadores de temporada alta (Navidad, holidays) se configuran por fecha, tienen prioridad sobre multiplicadores de hora pico.
- Planes mensuales se renuevan automáticamente (RF-017) y no se cobra por tiempo excedido en día de renovación.