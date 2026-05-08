# Requerimientos Funcionales

## Parqueadero — ParkCore SaaS

---

## Grupo 1: Módulo de Disponibilidad y Gestión de Sedes

**RF-001** | Disponibilidad | El sistema debe mostrar el conteo de espacios disponibles por sede en tiempo real (< 5 segundos de actualización) | Alta

**RF-002** | Disponibilidad | El sistema debe permitir consultar disponibilidad por zona dentro de una misma sede | Alta

**RF-003** | Disponibilidad | El sistema debe mantener historial de ocupación por hora para consultas históricas | Media

**RF-004** | Disponibilidad | El sistema debe permitir filtros de disponibilidad por tipo de espacio (cubierta, descubierta, VIP, moto) | Media

---

## Grupo 2: Módulo ANPR (Reconocimiento de Placas)

**RF-005** | ANPR | El sistema debe capturar la placa de un vehículo en el momento de entrada y registrar timestamp | Alta

**RF-006** | ANPR | El sistema debe buscar la placa a la salida, calcular duración y aplicar tarifa vigente | Alta

**RF-007** | ANPR | El sistema debe manejar el caso de placas ilegibles con registro manual por parte del operador | Alta

**RF-008** | ANPR | El sistema debe operar en modo offline si la conectividad se interrumpe, sincronizando al recuperar conexión | Alta

**RF-009** | ANPR | El sistema debe almacenar imágenes de cada captura con hash para auditoría | Media

---

## Grupo 3: Módulo CRM de Pagos y Cobros

**RF-010** | CRM/Pagos | El sistema debe registrar clientes (naturales y empresas) con sus placas asociadas | Alta

**RF-011** | CRM/Pagos | El sistema debe soportar múltiples métodos de pago: efectivo, PSE, tarjeta, Nequi, Daviplata | Alta

**RF-012** | CRM/Pagos | El sistema debe generar facturación electrónica integrada con DIAN | Alta

**RF-013** | CRM/Pagos | El sistema debe gestionar planes tarifarios: por minuto, por hora, diario, mensual, corporativo | Alta

**RF-014** | CRM/Pagos | El sistema debe enviar notificaciones push/SMS/email al cliente al entrar, al salir y ante pagos | Media

**RF-015** | CRM/Pagos | El sistema debe gestionar descuentos, cupones y programas de lealtad | Media

**RF-016** | CRM/Pagos | El sistema debe gestionar la cartera de morosos con bloqueo y desbloqueo de placas | Alta

**RF-017** | CRM/Pagos | El sistema debe soportar prepago (billetera virtual) con cargo y descuento automático | Media

---

## Grupo 4: Módulo de Control de Talanquera (IoT)

**RF-018** | Talanquera IoT | El sistema debe abrir la talanquera de salida solo si el pago está confirmado | Alta

**RF-019** | Talanquera IoT | El sistema debe permitir apertura manual por parte del operador en casos de emergencia | Alta

**RF-020** | Talanquera IoT | El sistema debe monitorear el estado de la talanquera (abierta/cerrada/error) en tiempo real | Alta

**RF-021** | Talanquera IoT | El sistema debe registrar cada comando enviado a la talanquera con timestamp, usuario y motivo | Alta

**RF-022** | Talanquera IoT | El sistema debe detectar falla de talanquera (no abre en 3s) y generar alerta inmediata | Alta

---

## Grupo 5: Módulo BI y Reportes

**RF-023** | BI/Reportes | El sistema debe generar reportes de ingresos, ocupación y tiempo promedio de estadía | Alta

**RF-024** | BI/Reportes | El sistema debe exportar datos a Excel/CSV y conectar con Power BI / Google Data Studio | Media

**RF-025** | BI/Reportes | El sistema debe generar reportes consolidados multi-sede para operadores con múltiples ubicaciones | Alta

---

## Grupo 6: Seguridad y Acceso

**RF-026** | Seguridad | El sistema debe autenticar usuarios con JWT y roles diferenciados (superadmin, admin_sede, operador, cliente) | Alta

**RF-027** | Seguridad | El sistema debe loguear todas las acciones sensibles en auditoría inmutable | Alta

**RF-028** | Seguridad | El sistema debe implementar RBAC: cada rol tiene permisos sobre recursos específicos | Alta

---

## Grupo 7: Gestión SaaS Multi-Tenant

### 7.1 Gestión de Tenants (Cuentas SaaS)

**RF-029** | SaaS | El sistema debe permitir crear una nueva cuenta tenant con datos básicos (nombre, email, empresa, NIT) | Alta

**RF-030** | SaaS | El sistema debe asignar un slug único a cada tenant (`/app/{slug}`) | Alta

**RF-031** | SaaS | El sistema debe iniciar cada nuevo tenant en un periodo de trial de 14 días sin cobro | Alta

**RF-032** | SaaS | El sistema debe convertir el trial en suscripción activa al confirmarse el primer pago | Alta

**RF-033** | SaaS | El sistema debe permitir que un tenant tenha múltiples usuarios propios (admin, managers, operadores) | Alta

**RF-034** | SaaS | El sistema debe aislar completamente los datos de cada tenant: ningún tenant puede ver datos de otro | Crítica

**RF-035** | SaaS | El sistema debe soportar la suspensión de un tenant por falta de pago (read-only) | Alta

**RF-036** | SaaS | El sistema debe soportar el churn (cancelación) de un tenant, reteniendo datos 90 días antes de eliminar | Media

---

### 7.2 Suscripciones y Facturación

**RF-037** | Billing | El sistema debe permitir seleccionar un plan de suscripción (Starter, Professional, Enterprise, Custom) | Alta

**RF-038** | Billing | El sistema debe cobrar automáticamente el plan mensual el día de renovación | Alta

**RF-039** | Billing | El sistema debe trackear uso excedente (transacciones, sedes extra, API calls) y facturarlo al cierre del ciclo | Alta

**RF-040** | Billing | El sistema debe procesar upgrades de plan con prorrateo inmediato | Alta

**RF-041** | Billing | El sistema debe procesar downgrades de plan al final del ciclo de facturación actual | Alta

**RF-042** | Billing | El sistema debe manejar reintentos de pago fallido (3 intentos en 7 días) antes de suspender | Alta

**RF-043** | Billing | El sistema debe generar invoices internos diferenciando suscripción base, excedentes y impuestos | Alta

**RF-044** | Billing | El sistema debe integralise con Stripe como motor de suscripciones y billing | Alta

**RF-045** | Billing | El sistema debe escuchar webhooks de Stripe para confirmar pagos, cambios de plan y cancelaciones | Alta

---

### 7.3 Branding y Personalización

**RF-046** | Branding | El sistema debe permitir que cada tenant configure su logo, color primario y secundario | Alta

**RF-047** | Branding | El sistema debe aplicar el branding del tenant en el dashboard de sus operadores | Alta

**RF-048** | Branding | El sistema debe aplicar el branding del tenant en los emails transacticionales (desde address, logo) | Alta

**RF-049** | Branding | El sistema debe permitir custom domain para tenants Enterprise+ (SSL automático) | Alta

**RF-050** | Branding | El sistema debe permitir white-label de la app móvil para tenants Custom | Media

---

### 7.4 API Keys y Acceso Externo

**RF-051** | API Keys | El sistema debe permitir que cada tenant genere API keys para integraciones de terceros | Alta

**RF-052** | API Keys | El sistema debe asociar scopes granulares a cada API key (`disponibilidad:read`, `reservas:write`, etc.) | Alta

**RF-053** | API Keys | El sistema debe aplicar rate limits por API key según el plan del tenant | Alta

**RF-054** | API Keys | El sistema debe permitir rotar y revocar API keys desde el dashboard | Alta

**RF-055** | API Keys | El sistema debe registrar el último uso de cada API key para auditoría | Media

---

### 7.5 Feature Flags por Plan

**RF-056** | Features | El sistema debe restringir features según el plan del tenant (multi-sede, BI, SSO, etc.) | Alta

**RF-057** | Features | El sistema debe mostrar error 403 cuando un tenant intenta acceder a feature no incluida en su plan | Alta

**RF-058** | Features | El sistema debe permitir añadir features a un plan existente vía upgrade | Alta

---

### 7.6 Onboarding de Nuevo Tenant

**RF-059** | Onboarding | El sistema debe guiar al nuevo usuario con un wizard de setup (datos empresa → primera sede → zona → talanquera → invitación equipo) | Alta

**RF-060** | Onboarding | El sistema debe enviar email de bienvenida con instrucciones de acceso al crear la cuenta | Alta

**RF-061** | Onboarding | El sistema debe verificar el email del usuario mediante OTP | Alta

**RF-062** | Onboarding | El sistema debe ofrecer asistente de configuración de primera sede con templates predefinidos | Media

---

### 7.7 Métricas SaaS

**RF-063** | Métricas SaaS | El sistema debe calcular y almacenar MRR (Monthly Recurring Revenue) por tenant por mes | Alta

**RF-064** | Métricas SaaS | El sistema debe calcular Churn Rate mensual (tenants perdidos / total al inicio del mes) | Alta

**RF-065** | Métricas SaaS | El sistema debe calcular NRR (Net Revenue Retention) mensual | Alta

**RF-066** | Métricas SaaS | El sistema debe trackear eventos significativos de suscripción (trial_started, converted, upgraded, churned, payment_failed) | Alta

---

### 7.8 SSO / SAML (Enterprise)

**RF-067** | SSO | El sistema debe permitir login via SAML 2.0 con IdP externos (Okta, Azure AD, Google Workspace) para tenants Enterprise | Alta

**RF-068** | SSO | El sistema debe hacer just-in-time provisioning: crear usuario en el tenant si el IdP lo autentica por primera vez | Alta

**RF-069** | SSO | El sistema debe mapear roles del IdP a roles internos del tenant según configuración | Media

---

### 7.9 Users Roles por Tenant

**RF-070** | Users | El sistema debe permitir crear usuarios dentro de un tenant con roles específicos | Alta

**RF-071** | Users | El sistema debe permitir que el tenant_admin asigne roles a usuarios de su organización | Alta

**RF-072** | Users | El sistema debe soportar MFA (autenticación de dos factores) para todos los usuarios | Alta

**RF-073** | Users | El sistema debe bloquear usuarios después de 5 intentos fallidos de login | Alta

**RF-074** | Users | El sistema debe permitir que un admin de tenant Restrinja el acceso de sus usuarios a sedes específicas | Alta

---

## Grupo 8: BI Avanzado (solo Enterprise+)

**RF-075** | BI | El sistema debe mostrar dashboard con tendencias de ocupación, ingresos y transacciones en tiempo real | Alta

**RF-076** | BI | El sistema debe comparar métricas entre sedes (benchmarking interno) | Alta

**RF-077** | BI | El sistema debe predecir demanda basándose en patrones históricos (forecasting de ocupación) | Media

**RF-078** | BI | El sistema debe exponer datos vía API GraphQL o REST para conexión con herramientas de BI externas | Media

---

## Grupo 9: Módulo B2B Flotas (Enterprise+)

**RF-079** | B2B | El sistema debe permitir registrar empresas con flotas de vehículos y asignarles un plan empresarial | Alta

**RF-080** | B2B | El sistema debe gestionar límites de gasto por vehículo dentro de una flota | Media

**RF-081** | B2B | El sistema debe generar facturación consolidada mensual por empresa con detalle por vehículo | Alta

**RF-082** | B2B | El sistema debe permitir que el admin de la empresa acceda a reportes de uso de su flota | Alta

---

## Grupo 10: Configuración General del Sistema (Admin Panel)

> Todo el sistema es configurable desde el panel de administración. No hay valores hardcodeados — cada parámetro de negocio vive en la base de datos y se edita desde la UI del tenant_admin o superadmin.

### 10.1 Modo de Operación por Sede

|**RF-083** | Config | El sistema debe permitir configurar el modo de operación por sede: `iot` (talanqueras + ANPR) o `manual` (sin dispositivos, registro por operador) | Alta

|**RF-084** | Config | En modo `manual`, el operador registra entrada/salida desde la app sin dispositivos IoT | Alta

|**RF-085** | Config | En modo `iot`, el sistema espera eventos de talanquera y ANPR para registrar ingresos/salidas automáticamente | Alta

|**RF-086** | Config | El sistema debe permitir cambiar el modo de operación de una sede en cualquier momento sin perder datos | Alta

### 10.2 Personalización de Campos y Flujos

|**RF-087** | Config | El sistema debe permitir que el tenant_admin defina campos personalizados (metadata) por sede, zona y espacio desde el admin | Alta

|**RF-088** | Config | El sistema debe permitir configurar labels personalizados (ej: " bahía" vs "espacio" vs "box") según el país/region del tenant | Alta

|**RF-089** | Config | El sistema debe permitir activar/desactivar módulos completos desde el admin (ej: desactivar módulo CRM si el parqueadero no factura) | Alta

### 10.3 Notificaciones y Canales

|**RF-090** | Config | El sistema debe permitir activar/desactivar tipos de notificación por canal (push, SMS, email, WhatsApp) desde el admin | Alta

|**RF-091** | Config | El sistema debe permitir personalizar templates de notificación (mensaje de entrada, salida, recordatorio de pago) desde el admin | Alta

|**RF-092** | Config | El sistema debe permitir configurar horarios de envío de notificaciones batch (ej: resumen diario a las 8am) | Media

### 10.4 Reglas de Negocio Configurables

|**RF-093** | Config | El sistema debe permitir definir reglas de tarifación desde el admin: fracciones de tiempo, topes máximos, tarifas especiales (navidad, hora pico) | Alta

|**RF-094** | Config | El sistema debe permitir configurar descuentos y promociones desde el admin con reglas de validez y uso máximo | Alta

|**RF-095** | Config | El sistema debe permitir configurar políticas de bloqueo de vehículos (días de mora, monto mínimo) desde el admin | Alta

### 10.5 Integraciones y Webhooks

|**RF-096** | Config | El sistema debe permitir configurar webhooks salientes (URL, eventos suscritos, headers de autenticación) desde el admin | Alta

|**RF-097** | Config | El sistema debe permitir probar el envío de webhooks desde el admin antes de activar | Media

### 10.6 App Móvil y UX

|**RF-098** | Config | El sistema debe permitir cambiar el orden de las secciones en la app móvil del operador desde el admin | Media

|**RF-099** | Config | El sistema debe permitir configurar campos obligatorios/opcionales en el registro de entrada manual (ej: requiere placa, requiere foto) | Alta

---

## Grupo 11: Observabilidad y Monitoreo

> El sistema debe ser transparente para el equipo interno y el tenant_admin. Toda anomalía se detecta antes de que el cliente la reporte.

### 11.1 Health Checks y Estado del Sistema

|**RF-100** | Observabilidad | El sistema debe exponer endpoints `/health` por microservicio que retornen el estado de la DB, dependencias externas y memoria | Alta

|**RF-101** | Observabilidad | El sistema debe mostrar un dashboard de salud general con uptime de todos los microservicios actualizado cada 30 segundos | Alta

|**RF-102** | Observabilidad | El sistema debe detectary alertar cuando un microservicio deixe de responder (critical) o su latencia exceeda 2x el baseline (warning) | Alta

### 11.2 Métricas de Infraestructura

|**RF-103** | Observabilidad | El sistema debe trackear uso de CPU, RAM, disco y red por cada microservicio con retención de 30 días | Alta

|**RF-104** | Observabilidad | El sistema debe trackear latencia de API Gateway, tiempo de respuesta de cada endpoint y throughput (req/min) | Alta

|**RF-105** | Observabilidad | El sistema debe exponer métricas en formato Prometheus (`/metrics`) para integración con Grafana | Alta

### 11.3 Alertas Configurables

|**RF-106** | Alertas | El sistema debe permitir que el tenant_admin configure umbrales de alerta (threshold) por métrica desde el admin | Alta

|**RF-107** | Alertas | El sistema debe permitir elegir el canal de notificación de alertas: email, SMS, Slack, webhook | Alta

|**RF-108** | Alertas | El sistema debe permitir configurar ventanas de silencio (maintenance windows) donde las alertas no se envíen | Media

### 11.4 Dispositivos IoT: Heartbeat y Latencia

|**RF-109** | IoT | El sistema debe recibir heartbeat de cada talanquera y ANPR cada 60 segundos y marcar el dispositivo como offline si no llega | Alta

|**RF-110** | IoT | El sistema debe trackear la latencia comando-respuesta de cada talanquera (el tiempo entre enviar "abrir" y confirmar "abierta") y alertar si exceede 3 segundos | Alta

|**RF-111** | IoT | El sistema debe generar alerta inmediata cuando una talanquera reporta estado de error o no responde durante más de 2 minutos | Alta

### 11.5 Trazabilidad Distributed (Tracing)

|**RF-112** | Tracing | El sistema debe asignar un `trace_id` a cada request API y propagarlo a todos los microservicios involucrados | Media

|**RF-113** | Tracing | El sistema debe permitir buscar logs por `trace_id` para reconstruir el flujo completo de una transacción | Media

### 11.6 Dashboard SLA

|**RF-114** | SLA | El sistema debe calcular y mostrar el uptime real de cada microservicio por mes (disponible / total minutos) | Alta

|**RF-115** | SLA | El sistema debe marcar en rojo los servicios cuyo uptime del mes esté por debajo del SLA contratado (99.9% para Enterprise) | Alta

---

## Grupo 12: Informes y Reportes Operativos

### 12.1 Reportes de Ingresos

|**RF-116** | Reportes | El sistema debe generar reportes de ingresos con: total, impuestos, descuentos, netos, por forma de pago, por sede | Alta

|**RF-117** | Reportes | El sistema debe permitir filtrar reportes por: sede, operador, cliente, rango de fechas, tipo de vehículo | Alta

|**RF-118** | Reportes | El sistema debe mostrar comparativa automática del período vs período anterior (ej: mayo vs abril) con variación % | Alta

### 12.2 Reportes de Ocupación

|**RF-119** | Reportes | El sistema debe generar reportes de ocupación por hora, mostrando: espacios ocupados, tasa ocupación %, duración promedio | Alta

|**RF-120** | Reportes | El sistema debe generar heatmaps de ocupación por día de la semana y hora (gráfico de calor) | Media

|**RF-121** | Reportes | El sistema debe proyectar ocupación futura basándose en patrones históricos (forecasting) | Media

### 12.3 Reportes de Morosidad y Bloqueos

|**RF-122** | Reportes | El sistema debe generar reporte de morosos: clientes con deuda pendiente, monto total, antigüedad de la deuda, veces contactado | Alta

|**RF-123** | Reportes | El sistema debe generar reporte de vehículos bloqueados con razón del bloqueo y fecha | Alta

### 12.4 Reportes de Operador y Productividad

|**RF-124** | Reportes | El sistema debe generar reporte de productividad por operador: transacciones abiertas/cerradas, cobros, aperturas manuales, reembolsos | Alta

|**RF-125** | Reportes | El sistema debe identificar anomalías: operador con reembolsos anormalmente altos o cierres de transacción sin pago | Alta

### 12.5 Reportes de Cliente y Flota (B2B)

|**RF-126** | Reportes | El sistema debe generar reporte de historial de cliente: visitas, tiempo promedio, gasto total, última visita, métodos de pago usados | Alta

|**RF-127** | Reportes | El sistema debe generar reporte de uso de flota: vehículos de la empresa con más uso, custo por vehículo, límite de gasto剩余 | Alta

### 12.6 Exportación y Programación

|**RF-128** | Reportes | El sistema debe permitir exportar cualquier reporte a Excel (.xlsx), CSV y PDF | Alta

|**RF-129** | Reportes | El sistema debe permitir programar reportes periódicos (diario, semanal, mensual) con entrega por email automático | Alta

|**RF-130** | Reportes | El sistema debe guardar un log de reportes programados entregados con: destinatario, fecha/hora, formato, estado | Media

---

## Grupo 13: App Móvil del Operador

### 13.1 Dashboard y Vista Principal

|**RF-131** | App Operador | El sistema debe mostrar en la app móvil del operador: conteo de espacios disponibles, ocupación en tiempo real, ingresos del día | Alta

|**RF-132** | App Operador | El sistema debe permitir al operador cambiar entre sedes rápidamente desde un selector en la app | Alta

### 13.2 Registro Manual de Entrada/Salida

|**RF-133** | App Operador | El operador puede registrar entrada manualmente con: placa (manual o seleccionada de lista), fecha/hora, observación | Alta

|**RF-134** | App Operador | El operador puede registrar salida manualmente y el sistema calcula el valor a pagar mostrando un resumen al conductor | Alta

|**RF-135** | App Operador | El operador puede registrar el pago asociado a una salida (efectivo, transferencia) desde la app | Alta

### 13.3 Gestión de Talánqueras

|**RF-136** | App Operador | El operador puede abrir/cerrar una talanquera desde la app con confirmación de gesto (doble tap) | Alta

|**RF-137** | App Operador | La app muestra en tiempo real el estado de cada talanquera (abierta/cerrada/error/offline) | Alta

### 13.4 Notificaciones y Alertas en App

|**RF-138** | App Operador | La app recibe push notifications cuando: un vehículo lleva más de X horas sin pago, una talanquera está offline, alerta de mora | Alta

|**RF-139** | App Operador | El operador puede resolver/descartar alertas desde la app y ver el historial de alertas de las últimas 24 horas | Media

### 13.5 Búsqueda de Cliente y Vehículo

|**RF-140** | App Operador | El operador puede buscar un cliente por nombre, placa o teléfono y ver su historial completo | Alta

|**RF-141** | App Operador | El operador puede bloquear/desbloquear un vehículo desde la app con confirmación de contraseña | Alta

---

## Grupo 14: App Móvil del Cliente (Usuario Final)

### 14.1 Disponibilidad y Reserva

|**RF-142** | App Cliente | El cliente puede ver espacios disponibles en tiempo real por sede y zona | Alta

|**RF-143** | App Cliente | El cliente puede pagar el parqueo anticipadamente desde la app (prepago) y seleccionar duración | Alta

|**RF-144** | App Cliente | El cliente recibe recordatorio push si el tiempo pagado está por vencer y puede renovar desde la app | Alta

### 14.2 Gestión de Cuenta y Vehículos

|**RF-145** | App Cliente | El cliente puede agregar/editar/eliminar vehículos de su cuenta | Alta

|**RF-146** | App Cliente | El cliente puede añadir métodos de pago (tarjeta, Nequi, Daviplata) y definir uno como default | Alta

### 14.3 Historial y Facturas

|**RF-147** | App Cliente | El cliente puede ver su historial de transacciones con detalle: fecha, sede, duración, monto, forma de pago | Alta

|**RF-148** | App Cliente | El cliente puede ver y descargar sus facturas electrónicas | Alta

### 14.4 Notificaciones y Promociones

|**RF-149** | App Cliente | El cliente puede configurar qué notificaciones quiere recibir y por qué canal (push/SMS/email) | Alta

|**RF-150** | App Cliente | El sistema envía promociones y descuentos al cliente según su perfil de uso | Media

---

## Grupo 15: Panel de Administración (Admin Panel)

### 15.1 Gestión de Usuarios y Permisos

|**RF-151** | Admin | El tenant_admin puede crear, editar, desactivar usuarios de su organización con roles específicos | Alta

|**RF-152** | Admin | El tenant_admin puede asignar restricción de sedes a cada usuario (sede_ids) | Alta

|**RF-153** | Admin | El tenant_admin puede ver la actividad reciente de cada usuario (último acceso, acciones realizadas) | Media

### 15.2 Facturación y Suscripción

|**RF-154** | Admin | El tenant_admin puede ver su suscripción actual: plan, precio, fecha de renovación, métodos de pago | Alta

|**RF-155** | Admin | El tenant_admin puede descargar invoices históricas de su suscripción | Alta

|**RF-156** | Admin | El tenant_admin puede hacer upgrade/downgrade de plan desde el admin | Alta

### 15.3 Configuración de Dispositivos

|**RF-157** | Admin | El tenant_admin puede agregar, editar y desactivar talanqueras y cámaras ANPR asociadas a una sede | Alta

|**RF-158** | Admin | El tenant_admin puede ver el estado y latency de cada dispositivo en el admin | Alta

### 15.4 Gestión de Espacios y Zonas

|**RF-159** | Admin | El tenant_admin puede crear/editar/eliminar zonas y espacios dentro de una sede con sus tarifas asociadas | Alta

|**RF-160** | Admin | El tenant_admin puede marcar espacios como: libre, ocupado, mantenimiento, reservado | Alta

### 15.5 Configuración de Tarifas y Promociones

|**RF-161** | Admin | El tenant_admin puede crear planes tarifarios con fracciones, topes, tarifas nocturnas | Alta

|**RF-162** | Admin | El tenant_admin puede crear reglas de tarifación especial (temporada alta, hora pico) con multiplicadores | Alta

|**RF-163** | Admin | El tenant_admin puede crear y gestionar promociones con límite de uso | Alta

### 15.6 Webhooks e Integraciones

|**RF-164** | Admin | El tenant_admin puede configurar webhooks con URL, eventos y auth headers | Alta

|**RF-165** | Admin | El tenant_admin puede probar webhooks y ver historial de intentos con respuesta | Alta

### 15.7 Configuración de Alertas

|**RF-166** | Admin | El tenant_admin puede configurar canales de alerta (email, Slack, SMS) y sus umbrales | Alta

### 15.8 Audit Log

|**RF-167** | Admin | El sistema debe guardar log inmutable de todas las acciones sensibles: login, logout, cambios de config, creaciones, eliminaciones | Alta

|**RF-168** | Admin | El tenant_admin puede buscar el audit log filtrando por: usuario, acción, recurso, rango de fechas | Alta

---

## Grupo 16: Módulo de Conciliación y Cierre de Turno

### 16.1 Conciliación de Dinero

|**RF-169** | Conciliación | El sistema debe calcular el total de efectivo esperado vs registrado por operador por turno | Alta

|**RF-170** | Conciliación | El sistema debe marcar como "en discrepancia" toda diferencia mayor al 0.5% entre efectivo esperado y real | Alta

|**RF-171** | Conciliación | El operador puede registrar una diferencia de caja con justificación y evidencia (foto del dinero contado) | Alta

### 16.2 Cierre de Turno

|**RF-172** | Cierre | El sistema debe permitir al operador hacer cierre de turno consolidando: ingresos, aperturas de talanquera, alertas atendidas | Alta

|**RF-173** | Cierre | El sistema debe generar un reporte de cierre de turno en PDF con firma digital del operador | Alta

|**RF-174** | Cierre | El sistema debe notificar al admin cuando un operador hace cierre de turno | Alta

---

## Grupo 17: Soporte y Atención al Cliente

### 17.1 Tickets de Soporte

|**RF-175** | Soporte | El cliente puede crear un ticket de soporte desde la app describiendo su problema | Alta

|**RF-176** | Soporte | El operador puede ver y atender tickets de soporte de los clientes de su sede | Alta

|**RF-177** | Soporte | El sistema debe trackear SLA de tickets: tiempo de primera respuesta, tiempo de resolución | Media

### 17.2 Chat de Soporte

|**RF-178** | Soporte | El sistema debe permitir chat en tiempo real entre cliente y operador dentro de la app | Media

### 17.3 Valoración y Feedback

|**RF-179** | Soporte | El sistema debe solicitar feedback al cliente después de cada transacción con opción de calificación (1-5 estrellas) y comentario | Media

|**RF-180** | Soporte | El tenant_admin puede ver el NPS (Net Promoter Score) y calificación promedio por sede | Media

---

*Total: 180 requerimientos funcionales*