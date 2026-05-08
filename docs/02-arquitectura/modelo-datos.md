# Modelo de Datos

---

## Diagrama Entidad-Relación (Descripción Textual)

El modelo de datos de ParkCore se organiza en las siguientes entidades principales y sus relaciones:

**Sede** es la entidad raíz que representa cada parqueadero físico. Una sede contiene múltiples **Zonas**. Cada zona agrupa **Espacios** individuales de estacionamiento. Los **Talanqueras** están asociadas a una sede y controlan el acceso vehicular en puntos específicos (entrada o salida).

**Cliente** representa una persona natural o empresa que utiliza el parqueadero. Un cliente puede registrar múltiples **Vehículos** a su nombre. Cada vehículo pertenece a un único cliente.

**Registro_entrada** captura cada ingreso de un vehículo al parqueadero: se asocia al vehículo, a la sede, a la talanquera por donde entró, y al espacio asignado (si aplica). **Registro_salida** registra la salida correspondiente, enlazando al registro de entrada origen para calcular duración y costo.

**Pago** se genera al cerrar una estadía: se asocia a un registro de entrada (o a un grupo de registros en planes prepago), a un plan tarifario, y al cliente. **Plan_tarifario** define los precios por hora, fracciones, y tarifas nocturnas o de/abonado por sede y tipo de vehículo.

**Evento_iot** registra cada mensaje recibido de dispositivos IoT (sensores de ocupación, cámaras ANPR, talanqueras): se asocia a una sede y al dispositivo que lo emitió. **Notificacion** registra las alertas enviadas a clientes o operadores.

**Usuario** representa cuentas de acceso al sistema de gestión (diferente de Cliente, que es quien usa el parqueadero). Cada usuario tiene un **Rol** que determina sus permisos. Un rol puede ser asignado a múltiples usuarios.

### Relaciones Resumidas

- sede 1:N zona
- zona 1:N espacio
- sede 1:N talanquera
- sede 1:N evento_iot
- cliente 1:N vehiculo
- vehiculo N:1 cliente
- registro_entrada N:1 vehiculo
- registro_entrada N:1 sede
- registro_entrada N:1 talanquera
- registro_entrada N:1 espacio (nullable)
- registro_salida N:1 registro_entrada
- registro_salida N:1 talanquera
- pago N:1 registro_entrada
- pago N:1 plan_tarifario
- pago N:1 cliente
- notificacion N:1 cliente
- notificacion N:1 registro_entrada (nullable)
- usuario N:1 rol

---

## Diccionario de Datos

### 1. sede

**Descripción**: Representa cada parqueadero físico gestionado por ParkCore.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único de la sede |
| nombre | VARCHAR(100) | NOT NULL | Nombre comercial de la sede |
| direccion | VARCHAR(255) | NOT NULL | Dirección postal completa |
| ciudad | VARCHAR(50) | NOT NULL | Ciudad donde opera la sede |
| latitud | DECIMAL(10,8) | | Coordenada geográfica |
| longitud | DECIMAL(11,8) | | Coordenada geográfica |
| capacidad_total | INTEGER | NOT NULL | Total de espacios disponibles |
| horario_inicio | TIME | NOT NULL | Hora de apertura |
| horario_fin | TIME | NOT NULL | Hora de cierre |
| metadata | JSONB | DEFAULT '{}' | Configuración flexible por sede |
| activa | BOOLEAN | DEFAULT true | Si la sede está operativa |
| modo_operacion | VARCHAR(20) | DEFAULT 'iot' | Modo: iot (talanqueras+ANPR) o manual (sin dispositivos) |
| created_at | TIMESTAMP | DEFAULT NOW() | Fecha de creación |
| updated_at | TIMESTAMP | DEFAULT NOW() | Última modificación |

---

### 1b. configuracion_sede

**Descripción**: Configuración granular por sede. Aquí vive TODO lo que el tenant_admin puede cambiar desde el admin panel — no hay valores hardcodeados. Cada sede tiene su propia instancia de esta tabla.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| sede_id | UUID | FK → sede, NOT NULL, UNIQUE | Sede dueña de esta config |
| labels | JSONB | DEFAULT '{}' | Labels personalizables: `{ "espacio_label": "bahía", "zona_label": "sección" }` |
| modulos_activos | JSONB | DEFAULT '{"crm":true,"notificaciones":true,"prepago":true,"flotas":false}' | Módulos activados/desactivados |
| campos_registro | JSONB | DEFAULT '{"requiere_placa":true,"requiere_foto":false,"permite_sin_placa":true}' | Validación en registro manual |
| fraccion_tiempo_min | INTEGER | DEFAULT 15 | Fracción mínima de cobro en minutos |
| tope_maximo_hora | INTEGER | DEFAULT 24 | Horas máximas facturables |
| notificacion_canales | JSONB | DEFAULT '{"entrada":["push","email"],"salida":["push","sms"],"pago":["push"]}' | Canales activos por tipo |
| horario_batch_notif | TIME | DEFAULT '08:00' | Hora envío notificaciones batch |
| dias_bloqueo_mora | INTEGER | DEFAULT 30 | Días para bloquear por mora |
| monto_minimo_bloqueo | DECIMAL(10,2) | DEFAULT 50000 | Monto mínimo para activar bloqueo |
| config_webhook | JSONB | DEFAULT '[]' | Array de webhooks: `{url, eventos[], auth_headers}` |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() |

---

### 2. zona

**Descripción**: Agrupa espacios dentro de una sede por tipo o ubicación (ej: zona covered, zona descubierto, zona VIP).

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único de la zona |
| sede_id | UUID | FK → sede, NOT NULL | Sede a la que pertenece |
| nombre | VARCHAR(100) | NOT NULL | Nombre de la zona |
| tipo | VARCHAR(50) | NOT NULL | Tipo: cubierta, descubierta, VIP, moto |
| capacidad | INTEGER | NOT NULL | Espacios en esta zona |
| tarifa_hora | DECIMAL(10,2) | NOT NULL | Tarifa por hora base |
| metadata | JSONB | DEFAULT '{}' | Atributos adicionales |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 3. espacio

**Descripción**: Unidad individual de estacionamiento, identificada por número o código dentro de una zona.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| zona_id | UUID | FK → zona, NOT NULL | Zona a la que pertenece |
| codigo | VARCHAR(20) | NOT NULL | Número o código del espacio |
| piso | INTEGER | DEFAULT 1 | Piso (para parkings multipiso) |
| estado | VARCHAR(20) | DEFAULT 'libre' | libre, ocupado, mantenimiento, reservado |
| es_accesible | BOOLEAN | DEFAULT false | Si tiene accesibilidad reducida |
| metadata | JSONB | DEFAULT '{}' | Sensores asociados, etc. |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 4. vehiculo

**Descripción**: Vehículos registrados por los clientes para acceso automatizado o seguimiento.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| cliente_id | UUID | FK → cliente, NOT NULL | Propietario del vehículo |
| placa | VARCHAR(10) | NOT NULL, UNIQUE | Placa del vehículo |
| tipo | VARCHAR(30) | NOT NULL | carro, moto, van, bicicleta |
| marca | VARCHAR(50) | | Marca del vehículo |
| modelo | VARCHAR(50) | | Modelo |
| color | VARCHAR(30) | | Color |
| fecha_expiracion_soat | DATE | | Vencimiento del SOAT |
| foto_url | VARCHAR(500) | | URL de foto del vehículo |
| es_preferencial | BOOLEAN | DEFAULT false | Si tiene beneficios |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 5. cliente

**Descripción**: Persona natural o jurídica que utiliza los servicios del parqueadero.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tipo | VARCHAR(20) | NOT NULL | natural o juridica |
| identificacion | VARCHAR(20) | NOT NULL, UNIQUE | CC, NIT, CE |
| nombre | VARCHAR(100) | NOT NULL | Razón social o nombre completo |
| email | VARCHAR(100) | | Correo electrónico |
| telefono | VARCHAR(20) | | Teléfono de contacto |
| direccion | VARCHAR(255) | | Dirección |
| es_enterprise | BOOLEAN | DEFAULT false | Si es cliente empresarial |
| plan_id | UUID | FK → plan_tarifario | Plan prepago asociado |
| saldo_prepago | DECIMAL(12,2) | DEFAULT 0 | Crédito disponible |
| preferencias_notif | JSONB | DEFAULT '{}' | Canales y tipos de notificación |
| activo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 6. registro_entrada

**Descripción**: Registra cada ingreso de un vehículo al parqueadero.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| vehiculo_id | UUID | FK → vehiculo, NOT NULL | Vehículo que ingresa |
| sede_id | UUID | FK → sede, NOT NULL | Sede donde ingresa |
| talanquera_entrada_id | UUID | FK → talanquera, NOT NULL | Punto de entrada |
| espacio_id | UUID | FK → espacio, NULL | Espacio asignado (nullable) |
| fecha_hora_entrada | TIMESTAMP | NOT NULL | Momento de entrada |
| placa_reconocida | VARCHAR(10) | | Placa leída por ANPR |
| confianza_anpr | DECIMAL(5,2) | | Porcentaje de confianza ANPR |
| tipo_ingreso | VARCHAR(20) | DEFAULT 'normal' | normal, manual, emergencia |
| observaciones | TEXT | | Notas del operador |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 7. registro_salida

**Descripción**: Registra la salida de un vehículo y calcula la duración de la estadía.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| registro_entrada_id | UUID | FK → registro_entrada, NOT NULL, UNIQUE | Entrada asociada |
| talanquera_salida_id | UUID | FK → talanquera, NOT NULL | Punto de salida |
| fecha_hora_salida | TIMESTAMP | NOT NULL | Momento de salida |
| duracion_minutos | INTEGER | NOT NULL | Duración calculada |
| espacio_id | UUID | FK → espacio | Espacio que ocupaba |
| tipo_salida | VARCHAR(20) | DEFAULT 'normal' | normal, manual, cancelada |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 8. pago

**Descripción**: Registro financiero de cada transacción de parqueadero.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| cliente_id | UUID | FK → cliente, NOT NULL | Cliente que paga |
| registro_entrada_id | UUID | FK → registro_entrada, NOT NULL | Estadía que se paga |
| plan_tarifario_id | UUID | FK → plan_tarifario, NOT NULL | Tarifa aplicada |
| monto_base | DECIMAL(10,2) | NOT NULL | Subtotal sin descuentos |
| monto_descuento | DECIMAL(10,2) | DEFAULT 0 | Descuento aplicado |
| monto_total | DECIMAL(10,2) | NOT NULL | Total a pagar |
| forma_pago | VARCHAR(30) | NOT NULL | efectivo, tarjeta, transferencia, prepago |
| estado | VARCHAR(20) | DEFAULT 'completado' | completado, pendiente, reembolsado |
| referencia_externa | VARCHAR(100) | | ID de la pasarela de pago |
| fecha_pago | TIMESTAMP | NOT NULL | Momento del pago |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 9. plan_tarifario

**Descripción**: Define las tarifas y planes disponibles por sede y tipo de vehículo.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| sede_id | UUID | FK → sede, NULL | Sede específica o NULL para global |
| nombre | VARCHAR(100) | NOT NULL | Nombre del plan |
| tipo | VARCHAR(30) | NOT NULL | por_hora, fijo, prepago, empresarial |
| tarifa_hora | DECIMAL(10,2) | | Tarifa por hora |
| tarifa_fraccion | DECIMAL(10,2) | | Tarifa por fracción de 15min |
| tarifa_noche | DECIMAL(10,2) | | Tarifa nocturna fija |
| tarifa_dia | DECIMAL(10,2) | | Tarifa diaria máxima |
| maximo_dia | DECIMAL(10,2) | | Tope máximo por día |
| horario_noche_inicio | TIME | | Inicio horario nocturno |
| horario_noche_fin | TIME | | Fin horario nocturno |
| vigencia_desde | DATE | NOT NULL | Fecha inicio vigencia |
| vigencia_hasta | DATE | | Fecha fin vigencia |
| activo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 10. talanquera

**Descripción**: Dispositivo físico de control de acceso (barrera) instalado en un punto de entrada o salida.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| sede_id | UUID | FK → sede, NOT NULL | Sede donde está instalada |
| codigo | VARCHAR(20) | NOT NULL | Identificador del dispositivo |
| tipo | VARCHAR(20) | NOT NULL | entrada o salida |
| modelo | VARCHAR(50) | | Modelo del dispositivo |
| ip_address | VARCHAR(45) | | Dirección IP |
| mqtt_topic | VARCHAR(100) | | Topic MQTT del dispositivo |
| estado | VARCHAR(20) | DEFAULT 'operativa' | operativa, mantenimiento, offline |
| configuraciones | JSONB | DEFAULT '{}' | Configuración específica |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 11. evento_iot

**Descripción**: Registro de cada evento generado por dispositivos IoT en las sedes.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| sede_id | UUID | FK → sede, NOT NULL | Sede donde ocurrió |
| talanquera_id | UUID | FK → talanquera, NULL | Dispositivo origen |
| espacio_id | UUID | FK → espacio, NULL | Espacio asociado |
| tipo_evento | VARCHAR(50) | NOT NULL | entrada, salida, ocupacion, alarma, latencia |
| dispositivo_id | VARCHAR(100) | NOT NULL | ID del dispositivo IoT |
| payload | JSONB | NOT NULL | Datos del evento |
| calidad_senal | INTEGER | | Fuerza de señal (%) |
| timestamp_dispositivo | TIMESTAMP | NOT NULL | Timestamp del dispositivo |
| received_at | TIMESTAMP | DEFAULT NOW() | Timestamp de recepción |
| processed_at | TIMESTAMP | | Cuándo se procesó el evento |

---

### 12. notificacion

**Descripción**: Registro de notificaciones enviadas a clientes o usuarios del sistema.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| cliente_id | UUID | FK → cliente, NOT NULL | Destinatario |
| registro_entrada_id | UUID | FK → registro_entrada, NULL | Estadía relacionada |
| tipo | VARCHAR(50) | NOT NULL | entrada_registrada, salida_pendiente, pago_recibido, promocion |
| canal | VARCHAR(20) | NOT NULL | push, sms, email, whatsapp |
| titulo | VARCHAR(200) | NOT NULL | Asunto de la notificación |
| cuerpo | TEXT | NOT NULL | Contenido del mensaje |
| estado_envio | VARCHAR(20) | DEFAULT 'pendiente' | pendiente, enviado, fallido, entregado |
| fecha_envio | TIMESTAMP | | Momento del envío |
| metadatos | JSONB | DEFAULT '{}' | Datos adicionales |
| created_at | TIMESTAMP | DEFAULT NOW() | |

---

### 13. usuario

**Descripción**: Cuentas de acceso al panel de gestión (operadores, administradores, superadmins). Diferente de cliente.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Nombre de usuario |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Correo electrónico |
| password_hash | VARCHAR(255) | NOT NULL | Hash de contraseña (bcrypt) |
| nombre | VARCHAR(100) | NOT NULL | Nombre completo |
| rol_id | UUID | FK → rol, NOT NULL | Rol asignado |
| sede_id | UUID | FK → sede, NULL | Sede restringida (NULL = todas) |
| estado | VARCHAR(20) | DEFAULT 'activo' | activo, inactivo, bloqueado |
| ultimo_acceso | TIMESTAMP | | Último login exitoso |
| intentos_fallidos | INTEGER | DEFAULT 0 | Conteo de login fallidos |
| bloqueado_hasta | TIMESTAMP | | Lockout automático |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

### 14. rol

**Descripción**: Define los permisos asignados a los usuarios del sistema de gestión.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| nombre | VARCHAR(50) | NOT NULL, UNIQUE | Nombre del rol |
| descripcion | TEXT | | Descripción del propósito |
| permisos | JSONB | NOT NULL | Lista de permisos granted |
| nivel | INTEGER | DEFAULT 0 | Nivel jerárquico (para herencia) |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

---

## Estrategia de Indexación

### Índices Primarios

| Tabla | Campo(s) | Tipo de Índice | Justificación |
|---|---|---|---|
| sede | id | B-tree (PK) | Acceso por ID |
| zona | sede_id | B-tree | Filtrar zonas por sede |
| espacio | zona_id | B-tree | Filtrar espacios por zona |
| espacio | estado | B-tree | Consultar espacios por estado |
| vehiculo | placa | B-tree, UNIQUE | Búsqueda por placa (ANPR) |
| vehiculo | cliente_id | B-tree | Vehículos por cliente |
| registro_entrada | sede_id, fecha_hora_entrada | B-tree | Consulta de ingresos por sede y rango |
| registro_entrada | vehiculo_id, fecha_hora_entrada | B-tree | Historial de un vehículo |
| registro_entrada | placa_reconocida | B-tree | Búsqueda por placa leída |
| registro_salida | registro_entrada_id | B-tree (UNIQUE) | Vincular salida a entrada |
| pago | cliente_id | B-tree | Historial de pagos por cliente |
| pago | estado, fecha_pago | B-tree | Transacciones pendientes o por rango |
| evento_iot | sede_id, timestamp_dispositivo | B-tree | Consulta de eventos por sede y rango |
| evento_iot | tipo_evento | B-tree | Filtrar por tipo de evento |
| notificacion | cliente_id, created_at | B-tree | Notificaciones por cliente |
| usuario | email | B-tree, UNIQUE | Login |
| usuario | sede_id | B-tree | Operadores por sede |

### Índices Compuestos para Queries Frecuentes

- `(sede_id, fecha_hora_entrada)` en registro_entrada para reportes diarios
- `(vehiculo_id, fecha_hora_entrada DESC)` en registro_entrada para historial recientes
- `(sede_id, estado)` en espacio para disponibilidad en tiempo real
- `(cliente_id, estado)` en pago para saldos pendientes

---

## Particionamiento

### Tablas Particionadas por Rango de Fechas

Las tablas de alto volumen transaccional se particionan mensualmente para optimizar queries sobre rangos de fechas y facilitar la purga de datos antiguos.

**Tablas sujetas a particionamiento**:

1. **registro_entrada** — partición por `fecha_hora_entrada`
2. **registro_salida** — partición por `fecha_hora_salida`
3. **pago** — partición por `fecha_pago`
4. **evento_iot** — partición por `timestamp_dispositivo`
5. **notificacion** — partición por `created_at`

### Estrategia de Particionamiento

Cada tabla se particiona mensualmente usando PostgreSQL Range Partitioning. Se crean particionesmes a futuro para evitar gaps (por ejemplo, en enero se crean particiones hasta marzo). particiones históricas se архивиan o descartan según la política de retención (default: 7 años para financiero, 2 años para IoT).

Ejemplo de creación para registro_entrada:

```sql
CREATE TABLE registro_entrada (
    id UUID DEFAULT gen_random_uuid(),
    vehiculo_id UUID NOT NULL,
    sede_id UUID NOT NULL,
    ...
    fecha_hora_entrada TIMESTAMP NOT NULL
) PARTITION BY RANGE (fecha_hora_entrada);

CREATE TABLE registro_entrada_2026_01 PARTITION OF registro_entrada
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

---

## Sección SaaS: Modelo de Datos Multi-Tenant

### 15. tenant

**Descripción**: Representa cada cuenta SaaS (cliente de la plataforma ParkCore). Cada tenant tiene su propia organización, usuarios, sedes y datos aislados.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único del tenant |
| nombre | VARCHAR(200) | NOT NULL | Razón social o nombre de la empresa |
| slug | VARCHAR(100) | NOT NULL, UNIQUE | URL única (`parkcore.io/{slug}`) |
| tipo | VARCHAR(20) | DEFAULT 'trial' | trial, active, suspended, churned |
| plan_id | UUID | FK → subscription_plan, NOT NULL | Plan de suscripción activo |
| fecha_contrato | DATE | NOT NULL | Inicio del contrato |
| fecha_renovacion | DATE | NOT NULL | Próximo cobro (día de facturación) |
| billing_email | VARCHAR(255) | NOT NULL | Email para facturas y billing |
| branding_enabled | BOOLEAN | DEFAULT true | Si tiene branding personalizado activo |
| custom_domain | VARCHAR(255) | | Dominio propio (Enterprise+) |
| stripe_customer_id | VARCHAR(100) | | ID del cliente en Stripe |
| stripe_subscription_id | VARCHAR(100) | | ID de la suscripción en Stripe |
| metadata | JSONB | DEFAULT '{}' | Configuración flexible adicional |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

### 16. subscription_plan

**Descripción**: Define los planes de suscripción SaaS disponibles con sus features y límites.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| nombre | VARCHAR(50) | NOT NULL, UNIQUE | starter, professional, enterprise, custom |
| precio_mensual_cop | BIGINT | NOT NULL | Precio mensual en COP (centavos) |
| sedes_incluidas | INTEGER | NOT NULL | Número de sedes incluidas en el plan |
| transacciones_incluidas | INTEGER | NOT NULL | Transacciones mensuales incluidas |
| seats_incluidos | INTEGER | NOT NULL | Usuarios incluídos |
| features | JSONB | NOT NULL | Matriz de features booleanas |
| rate_limit_api | INTEGER | NOT NULL | Requests por minuto para API keys |
| limites | JSONB | NOT NULL | Límites: max_sedes, max_vehiculos, max_api_calls_mes |
| activo | BOOLEAN | DEFAULT true | Si el plan está disponible para venta |
| created_at | TIMESTAMP | DEFAULT NOW() | |
| updated_at | TIMESTAMP | DEFAULT NOW() | |

**Ejemplo de features JSON:**
```json
{
  "multi_sede": true,
  "sedes_max": 10,
  "app_operador": true,
  "bi_advanced": true,
  "api_access": true,
  "sso": true,
  "white_label": false,
  "custom_domain": true,
  "mfa": true,
  "audit_logs_days": 365,
  "soporte": "priority",
  "sla": 99.9
}
```

### 17. tenant_user

**Descripción**: Usuarios dentro de un tenant (diferente de `usuario` del sistema de gestión legacy). Cada usuario pertenece a un tenant y tiene roles scoped a ese tenant.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant al que pertenece |
| email | VARCHAR(255) | NOT NULL | Email (único por tenant) |
| password_hash | VARCHAR(255) | NOT NULL | Hash bcrypt |
| nombre | VARCHAR(100) | NOT NULL | Nombre completo |
| rol | VARCHAR(50) | NOT NULL | tenant_admin, sede_manager, sede_operator, viewer |
| estado | VARCHAR(20) | DEFAULT 'activo' | activo, inactivo, bloqueado |
| mfa_enabled | BOOLEAN | DEFAULT false | Si tiene 2FA activo |
| mfa_secret | VARCHAR(255) | | Secret TOTP (cifrado) |
| ultimo_acceso | TIMESTAMPTZ | | |
| intentos_fallidos | INTEGER | DEFAULT 0 | |
| bloqueado_hasta | TIMESTAMPTZ | | |
| sede_ids | UUID[] | DEFAULT '{}' | Sedes a las que tiene acceso (vacío = todas) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE | | (tenant_id, email) | |

**Índices:**
- `idx_tenant_user_tenant` en `(tenant_id)`
- `idx_tenant_user_email_tenant` en `(tenant_id, email)`

### 18. api_key

**Descripción**: API keys para integraciones de terceros asociadas a un tenant. La key real se almacena como SHA-256 hash.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant propietario |
| nombre | VARCHAR(100) | NOT NULL | Descripción: "Integración Waze" |
| key_hash | VARCHAR(255) | NOT NULL | SHA-256 de la key completa |
| key_prefix | VARCHAR(12) | NOT NULL | Primeros 12 chars para identificar (ej: `pk_live_xqk`) |
| scopes | JSONB | NOT NULL | Lista de scopes: `["disponibilidad:read", "reservas:write"]` |
| rate_limit | INTEGER | NOT NULL | Requests por minuto (override del plan si aplica) |
| expires_at | TIMESTAMPTZ | | NULL = nunca expira |
| last_used_at | TIMESTAMPTZ | | |
| created_by | UUID | FK → tenant_user | Usuario que creó la key |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| revoked_at | TIMESTAMPTZ | | Si no es NULL, la key está revocada |
| UNIQUE | | (tenant_id, nombre) | |

**Índices:**
- `idx_api_key_tenant` en `(tenant_id)`
- `idx_api_key_prefix` en `(key_prefix)`

### 19. tenant_branding

**Descripción**: Configuración de marca personalizada por tenant (logo, colores, dominio, email).

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| tenant_id | UUID | FK → tenant, PK | Tenant propietario |
| logo_url | VARCHAR(500) | | URL S3 del logo |
| favicon_url | VARCHAR(500) | | URL S3 del favicon |
| primary_color | VARCHAR(7) | DEFAULT '#2563EB' | Color primario (#RRGGBB) |
| secondary_color | VARCHAR(7) | DEFAULT '#1E40AF' | Color secundario |
| font_heading | VARCHAR(100) | DEFAULT 'Inter' | Font para títulos |
| font_body | VARCHAR(100) | DEFAULT 'Inter' | Font para cuerpo |
| email_from_name | VARCHAR(100) | | "Parqueadero Los Andes" |
| email_from_address | VARCHAR(255) | | "no-reply@cliente.com" |
| custom_css | TEXT | | CSS custom adicional (Enterprise) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### 20. subscription_event

**Descripción**: Log de eventos significativos de suscripción para métricas SaaS y auditoría.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant afectado |
| tipo | VARCHAR(50) | NOT NULL | trial_started, converted, upgraded, downgraded, churned, payment_failed, payment_succeeded, subscription_updated |
| plan_id | UUID | FK → subscription_plan | Plan al momento del evento |
| monto_cop | BIGINT | | Monto cobrado en COP (centavos) |
| metadata | JSONB | DEFAULT '{}' | Datos adicionales: reason, error_code, etc. |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

**Índices:**
- `idx_subscription_event_tenant_mes` en `(tenant_id, created_at)` para métricas mensuales
- `idx_subscription_event_tipo` en `(tipo)`

### 21. saas_metrics

**Descripción**: Métricas SaaS calculadas y almacenadas mensualmente para reporting y dashboards de negocio.

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NULL | NULL = métrica agregada global |
| mes | DATE | NOT NULL | Primer día del mes |
| mrr_cents | BIGINT | | MRR en centavos de COP |
| arr_cents | BIGINT | | ARR en centavos de COP |
| seats_count | INTEGER | | Total de usuarios activos |
| transacciones_count | INTEGER | | Transacciones del mes |
| seats_billable | INTEGER | | Usuarios facturables |
| churned | BOOLEAN | DEFAULT false | Si el tenant se dio de baja este mes |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE | | (tenant_id, mes) | |

### 22. usage_record

**Descripción**: Registros de uso para billing por excedente (transacciones adicionales, sedes extra, API calls).

|| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant |
| tipo | VARCHAR(30) | NOT NULL | transacciones, sedes_extra, api_calls, almacenamiento_gb |
| cantidad | INTEGER | NOT NULL | Cantidad consumed |
| periodo | DATE | NOT NULL | Mes del uso (primer día) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE | | (tenant_id, tipo, periodo) | |

**Índices:**
- `idx_usage_record_tenant_period` en `(tenant_id, periodo)`

### 23. webhook_delivery

**Descripción**: Log de entregas de webhooks salientes (para debugging de integraciones con pasarelas de pago y IdP SSO).

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NULL | Tenant (NULL para webhooks internos) |
| endpoint_url | VARCHAR(500) | NOT NULL | URL destino |
| event_type | VARCHAR(50) | NOT NULL | Tipo de evento enviado |
| payload | JSONB | NOT NULL | Cuerpo del webhook |
| attempt_count | INTEGER | DEFAULT 0 | Intentos realizados |
| status | VARCHAR(20) | DEFAULT 'pending' | pending, delivered, failed |
| last_attempt_at | TIMESTAMPTZ | | |
| response_code | INTEGER | | Código HTTP de respuesta |
| response_body | TEXT | | Cuerpo de respuesta |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |

### 24. promocion

**Descripción**: Descuentos y promociones configurados por el tenant_admin con límites de uso y fechas de validez.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant propietario |
| nombre | VARCHAR(100) | NOT NULL | "20% off mayo 2026" |
| tipo | VARCHAR(20) | NOT NULL | porcentaje, valor_fijo, gratis_horas |
| valor | DECIMAL(10,2) | NOT NULL | 20.00 (porcentaje) o 5000.00 (COP) |
| max_uso | INTEGER | | NULL = ilimitado |
| uso_actual | INTEGER | DEFAULT 0 | Contador de usos |
| valido_desde | DATE | NOT NULL | |
| valido_hasta | DATE | NOT NULL | |
| aplicable_a | JSONB | DEFAULT '["todas"]' | ['todas'] o ['zona_vip'] o ['tipo_carro'] |
| activo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

### 25. notificacion_template

**Descripción**: Templates personalizables de notificación por canal y tipo de evento. Cada tenant define sus propios mensajes.

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant propietario |
| canal | VARCHAR(20) | NOT NULL | push, sms, email, whatsapp |
| tipo_evento | VARCHAR(50) | NOT NULL | entrada_registrada, salida_pendiente, pago_recibido, recordatorio |
| titulo_template | VARCHAR(200) | NOT NULL | Template del título |
| cuerpo_template | TEXT | NOT NULL | Template del cuerpo con variables `{{variable}}` |
| activo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |
| UNIQUE | | (tenant_id, canal, tipo_evento) | |

**Variables disponibles en templates:**
- `{{cliente_nombre}}`, `{{placa}}`, `{{sede_nombre}}`, `{{zona}}`, `{{espacio}}`, `{{fecha}}`, `{{hora}}`, `{{monto}}`, `{{duracion}}`

### 26. regla_tarifacion_especial

**Descripción**: Reglas de tarifación especiales por temporada o evento especial (Navidad, hora pico, etc.).

| Campo | Tipo | Constraints | Descripción |
|---|---|---|---|
| id | UUID | PK | Identificador único |
| tenant_id | UUID | FK → tenant, NOT NULL | Tenant propietario |
| sede_id | UUID | FK → sede, NULL | NULL = aplica a todas las sedes |
| nombre | VARCHAR(100) | NOT NULL | "Temporada alta diciembre" |
| multiplicador | DECIMAL(4,2) | NOT NULL | 1.5 = 150% del tarifa normal |
| dias_semana | JSONB | DEFAULT '[0,1,2,3,4,5,6]' | Días aplicables (0=domingo) |
| horario_inicio | TIME | | Inicio ventana horaria (NULL = todo el día) |
| horario_fin | TIME | | Fin ventana horaria |
| fecha_inicio | DATE | NOT NULL | |
| fecha_fin | DATE | NOT NULL | |
| zona_ids | UUID[] | DEFAULT '{}' | Zonas donde aplica (vacío = todas) |
| activo | BOOLEAN | DEFAULT true | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | |

**Índices:**
- `idx_regla_tarifaria_sede_fechas` en `(sede_id, fecha_inicio, fecha_fin)`

## Índices Adicionales para SaaS

|| Tabla | Campo(s) | Tipo | Justificación |
|---|---|---|---|---|
| tenant | slug | B-tree, UNIQUE | Lookup por slug |
| tenant | stripe_customer_id | B-tree | Webhook Stripe |
| tenant_user | tenant_id | B-tree | Lista de usuarios por tenant |
| tenant_user | email | B-tree, UNIQUE global | Login SSO |
| api_key | key_prefix | B-tree | Identificar key en requests |
| subscription_event | tenant_id, created_at | B-tree | Métricas por tenant |
| subscription_event | tipo | B-tree | Filtrar por tipo de evento |
| saas_metrics | tenant_id, mes | B-tree, UNIQUE | Unique por tenant/mes |
| usage_record | tenant_id, periodo | B-tree | Tracking mensual |

## Particionamiento Adicional SaaS

- **subscription_event**: partición por `created_at` (mensual, retención 36 meses)
- **saas_metrics**: partición por `mes` (mensual, retención 60 meses)
- **webhook_delivery**: partición por `created_at` (mensual, retención 6 meses)
- **usage_record**: partición por `periodo` (mensual, retención 24 meses)
