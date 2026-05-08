# Historias de Usuario

## Parqueadero — ParkCore SaaS

---

### 1. Consultar espacios disponibles

**Como** Cliente (conductor) **quiero** consultar espacios disponibles en una sede antes de llegar **para** planificar mi visita.

**Criterios de aceptación:**
- **Given** el cliente ha iniciado sesión en la app móvil
- **When** el cliente selecciona una sede y solicita disponibilidad
- **Then** el sistema muestra el número de espacios libres por zona con actualización en menos de 5 segundos

---

### 2. Lectura automática de placa a la entrada

**Como** Cliente (conductor) **quiero** que mi placa sea leída automáticamente a la entrada **para** no detenerme a interactuar con un operador.

**Criterios de aceptación:**
- **Given** un vehículo se aproxima a la entrada del parqueadero
- **When** la cámara ANPR captura la imagen de la placa
- **Then** el sistema registra la placa con timestamp y abre la talanquera sin intervención del cliente

---

### 3. Pago desde app móvil

**Como** Cliente (conductor) **quiero** pagar desde mi app móvil sin ir al cajero **para** ahorrar tiempo.

**Criterios de aceptación:**
- **Given** el cliente tiene un vehículo registrado dentro del parqueadero
- **When** inicia el pago desde la app y selecciona el método de pago
- **Then** el sistema confirma el pago, registra la transacción y habilita la salida del vehículo

---

### 4. Notificación de tiempo por vencer

**Como** Cliente (conductor) **quiero** recibir notificación cuando mi tiempo está por vencerse **para** renovar el pago oportunamente.

**Criterios de aceptación:**
- **Given** el cliente tiene un tiempo de permanencia activo
- **When** faltan 15 minutos para el vencimiento del tiempo pagado
- **Then** el sistema envía notificación push/SMS al cliente con opción de renovar desde la app

---

### 5. Ver espacios libres en tiempo real

**Como** Operador de parqueadero **quiero** ver en tiempo real cuántos espacios hay libres **para** orientar a los clientes.

**Criterios de aceptación:**
- **Given** el operador ha iniciado sesión en su panel de control
- **When** consulta la vista de ocupación de la sede
- **Then** el sistema muestra el conteo de espacios libres/ocupados por zona, actualizado en tiempo real

---

### 6. Apertura automática de talanquera tras pago

**Como** Operador de parqueadero **quiero** que la talanquera se abra automáticamente tras validar el pago **para** reducir mi intervención manual.

**Criterios de aceptación:**
- **Given** un cliente ha confirmado el pago desde la app
- **When** el vehículo se aproxima a la salida y el sistema valida el pago
- **Then** la talanquera se abre en menos de 1 segundo sin intervención del operador

---

### 7. Reportes de ingresos por período

**Como** Administrador de sede **quiero** consultar reportes de ingresos por día/semana/mes **para** tomar decisiones operativas.

**Criterios de aceptación:**
- **Given** el administrador tiene permisos de consulta sobre la sede
- **When** solicita un reporte de ingresos seleccionando el período (día/semana/mes)
- **Then** el sistema presenta los ingresos totales, cantidad de transacciones y comparativa con períodos anteriores

---

### 8. Bloqueo de placas de morosos

**Como** Administrador de sede **quiero** bloquear placas de morosos **para** evitar que salgan sin pagar.

**Criterios de aceptación:**
- **Given** existe un cliente con deuda pendiente registrada en el sistema
- **When** el vehículo con placa bloqueada intenta salir
- **Then** la talanquera permanece cerrada y se notifica al operador con los datos del moroso

---

### 9. Dashboard consolidado de KPIs por sede

**Como** Administrador global **quiero** ver KPIs consolidados de todas las sedes en un único dashboard **para** tener visibilidad de la red.

**Criterios de aceptación:**
- **Given** el administrador global tiene acceso a múltiples sedes
- **When** accede al dashboard consolidado
- **Then** el sistema muestra ingresos totales, ocupación promedio, transacciones y alertas cruzadas de todas las sedes

---

### 10. Precisión en lectura de placas mayor a 95%

**Como** Sistema (ANPR) **quiero** leer placas con precisión mayor a 95% **para** garantizar el flujo sin errores.

**Criterios de aceptación:**
- **Given** la cámara captura la imagen de una placa en condiciones normales de iluminación
- **When** el motor ANPR procesa la imagen
- **Then** la precisión de reconocimiento de caracteres es mayor al 95% y el resultado se devuelve en menos de 500ms

---

### 11. Registro de eventos de apertura en log inmutable

**Como** Sistema (ANPR) **quiero** registrar cada evento de apertura de talanquera en log inmutable **para** auditoría.

**Criterios de aceptación:**
- **Given** ocurre una apertura de talanquera (manual o automática)
- **When** el evento se dispara
- **Then** el sistema registra en un log inmutable: timestamp, placa, sede, tipo de apertura, usuario/actor que la detonó y resultado

---

### 12. Gestión de planes tarifarios

**Como** Administrador de sede **quiero** gestionar planes tarifarios (por hora, diario, mensual, flotas) **para** adaptar la oferta comercial.

**Criterios de aceptación:**
- **Given** el administrador de sede tiene permisos de configuración
- **When** crea, edita o elimina un plan tarifario
- **Then** el sistema aplica la tarifa correspondiente según el plan asociado al cliente o al tipo de vehículo

---

## Historias SaaS — Gestión de Tenant y Suscripción

---

### 13. Registro de nuevo tenant con trial

**Como** Usuario nuevo **quiero** registrarme y obtener 14 días de prueba gratis **para** evaluar la plataforma sin compromiso.

**Criterios de aceptación:**
- **Given** el usuario accede a la página de registro
- **When** completa: nombre empresa, email, contraseña y acepta términos
- **Then** el sistema crea una cuenta tenant en estado `trial`, envía email de bienvenida y muestra wizard de setup
- **And** el trialexpira en 14 días sin cobrar

---

### 14. Wizard de configuración de primera sede

**Como** Usuario con cuenta nueva **quiero** configurar mi primera sede siguiendo un wizard guiado **para** tener el sistema operativo rápidamente.

**Criterios de aceptación:**
- **Given** el usuario completó el registro y accedió al wizard
- **When** sigue los steps: (1) datos sede, (2) zonas, (3) talanqueras, (4) sensores, (5) invitar equipo
- **Then** al finalizar el wizard, la sede aparece operativa en el dashboard
- **And** el usuario recibe email de confirmación de setup completado

---

### 15. Renovación automática de suscripción

**Como** Sistema (billing) **quiero** cobrar automáticamente la suscripción el día de renovación **para** garantizar continuidad del servicio sin intervención manual.

**Criterios de aceptación:**
- **Given** es el día de renovación del tenant y el método de pago está vigente
- **When** Stripe intenta cobrar la suscripción
- **Then** si el cobro es exitoso, la suscripciónpermanece activa y se registra el evento en `subscription_events`
- **And** se envía email de confirmación de pago al admin del tenant
- **And** el contador de transacciones del mes se resetea

---

### 16. Upgrade de plan

**Como** Admin de tenant **quiero** hacer upgrade a un plan superior **para** acceder a features que necesito.

**Criterios de aceptación:**
- **Given** el tenant está en plan Starter y el admin accede a gestión de suscripción
- **When** selecciona hacer upgrade a Professional
- **Then** el sistema calcula el prorrateo del mes en curso, cobra la diferencia inmediatamente vía Stripe
- **And** el plan se actualiza instantáneamente, habilitando las nuevas features
- **And** se registra evento `upgraded` en `subscription_events`

---

### 17. Dunning: reintento de pago fallido

**Como** Sistema (billing) **quiero** reintentar pagos fallidos con escalada progresiva **para** maximizar la recuperación antes de suspender al tenant.

**Criterios de aceptación:**
- **Given** el primer intento de cobro falló
- **When** pasan D+1, D+3, D+7 sin cobro exitoso
- **Then** se envía email de alerta en cada intento fallido
- **And** tras 3 intentos fallidos, el tenant pasa a estado `suspended` (read-only)
- **And** se registra evento `payment_failed` en `subscription_events`

---

### 18. Suspensión y recuperación de tenant

**Como** Admin de tenant **quiero** resolver un problema de pago para recuperar el acceso completo **para** no perder mi configuración y datos.

**Criterios de aceptación:**
- **Given** el tenant está en estado `suspended` por pago fallido
- **When** el admin actualiza el método de pago y Stripe cobra exitosamente
- **Then** el tenant vuelve a estado `active` instantáneamente
- **And** todas las funcionalidades se restauran
- **And** se envía email de confirmación de recuperación

---

### 19. Churn (cancelación) de tenant

**Como** Admin de tenant **quiero** cancelar mi suscripción **para** dejar de usar la plataforma.

**Criterios de aceptación:**
- **Given** el admin de tenant accede a gestión de suscripción y selecciona cancelar
- **When** confirma la cancelación
- **Then** el acceso al sistema se revoca al final del ciclo de facturación actual
- **And** los datos se retienen durante 90 días (estado `churned`)
- **And** se registra evento `churned` en `subscription_events`
- **And** se envía email de confirmación de cancelación con fecha de acceso final

---

### 20. Aislamiento de datos entre tenants

**Como** Admin de tenant A **quiero** estar seguro de que el tenant B no puede ver mis datos **para** confiar en la seguridad de la plataforma.

**Criterios de aceptación:**
- **Given** el admin de tenant A está autenticado en su sesión
- **When** intenta acceder a recursos (sedes, usuarios, transacciones) de otro tenant
- **Then** el sistema retorna 403 Forbidden
- **And** el intento se registra en el log de auditoría
- **And** el middleware de tenant injection filtra todos los queries con `tenant_id` del token JWT

---

### 21. Gestión de usuarios dentro de un tenant

**Como** Admin de tenant **quiero** crear, editar y desactivar usuarios de mi organización **para** administrar el equipo que tiene acceso.

**Criterios de aceptación:**
- **Given** el admin de tenant está autenticado
- **When** accede a gestión de usuarios y crea un nuevo usuario con rol `operador`
- **Then** el nuevo usuario recibe email de invitación con enlace para crear contraseña
- **And** el usuario aparece en la lista de usuarios del tenant con estado `activo`
- **And** solo puede ver/operar las sedes asignadas a su rol

---

### 22. Restricción de acceso por sede para operadores

**Como** Admin de tenant **quiero** asignar sedes específicas a cada operador **para** que solo vean la información de las sedes que les corresponden.

**Criterios de aceptación:**
- **Given** existe un operador con rol `sede_operator`
- **When** el admin le asigna sedes A y B pero no C
- **Then** el operador al iniciar sesión solo ve dashboard de A y B, sin acceso a C
- **And** cualquier API call a sede C retorna 403 Forbidden

---

### 23. Configuración de branding por tenant

**Como** Admin de tenant **quiero** personalizar el logo y colores de la plataforma con mi marca **para** que mis operadores vean una experiencia coherente.

**Criterios de aceptación:**
- **Given** el admin de tenant accede a configuración de marca
- **When** sube logo, selecciona color primario y secundario, y guarda
- **Then** el dashboard de todos los usuarios del tenant muestra el branding personalizado
- **And** los emails transaccionales usan el logo y email address configurados

---

### 24. Custom domain para tenant Enterprise

**Como** Admin de tenant Enterprise **quiero** usar mi propio dominio para la plataforma **para** dar una experiencia white-label a mis operadores.

**Criterios de aceptación:**
- **Given** el tenant tiene plan Enterprise y el admin accede a custom domain
- **When** configura `app.cliente.com` apuntando a ParkCore
- **Then** ParkCore provisiona certificado SSL automáticamente (Let's Encrypt)
- **And** el API Gateway routing requests basados en Host header
- **And** el usuario accede a `app.cliente.com` y ve la plataforma con su branding

---

### 25. Generación y uso de API keys

**Como** Admin de tenant **quiero** crear API keys para integraciones de terceros **para** que aplicaciones externas accedan a datos de mi organización.

**Criterios de aceptación:**
- **Given** el admin de tenant accede a gestión de API keys
- **When** crea una nueva key con nombre "Waze Integration" y scopes `disponibilidad:read`
- **Then** el sistema muestra la key completa una sola vez (pk_live_xxxx...)
- **And** la key queda almacenada como hash SHA-256
- **And** cualquier request con esa key tiene rate limit según plan (500 req/min para Professional)
- **And** la key puede ser revocada en cualquier momento

---

### 26. Login SSO con Okta (Enterprise)

**Como** Usuario de empresa con Okta **quiero** hacer login con mis credenciales corporativas **para** no gestionar otra contraseña.

**Criterios de aceptación:**
- **Given** el tenant tiene SSO configurado con Okta
- **When** el usuario accede a `/auth/saml/{slug}/login` y es redirigido a Okta
- **Then** tras autenticarse en Okta, es redirigido de vuelta a ParkCore con sesión activa
- **And** si el usuario no existía, se crea automáticamente en el tenant (just-in-time provisioning)
- **And** el rol se mapea según configuración del IdP

---

### 27. Feature flag: restricción de BI avanzado

**Como** Sistema **quiero** denegar acceso a BI avanzado para tenants Starter **para** que el plan diferenciador de Enterprise sea atractivo.

**Criterios de aceptación:**
- **Given** un tenant con plan Starter intenta acceder a `/api/v1/reportes/prediccion`
- **When** el request llega al middleware de feature flags
- **Then** el sistema retorna 403 Forbidden con mensaje "Upgrade to Enterprise for BI advanced"
- **And** el intento se loguea para métricas de conversion funnel

---

### 28. Tracking de métricas SaaS

**Como** Equipo interno de ParkCore **quiero** consultar MRR, churn y NRR por mes **para** entender la salud del negocio.

**Criterios de aceptación:**
- **Given** hay transacciones de suscripción y pagos procesados
- **When** se consulta el dashboard de métricas SaaS
- **Then** el sistema muestra: MRR actual, ARR, Churn Rate %, NRR %, LTV estimado, CAC
- **And** los datos se actualizan daily con el cierre del día

---

### 29. Onboarding multi-sede

**Como** Admin de tenant **quiero** agregar nuevas sedes desde el dashboard **para** expandir mi operación sin contactar a soporte.

**Criterios de aceptación:**
- **Given** el tenant tiene plan Professional (3 sedes incluidas)
- **When** el admin crea una nueva sede llenando: nombre, dirección, capacidad, zonas
- **Then** la sede aparece en el dashboard listada como `pending`
- **And** el wizard de configuración de sensores y talanqueras se presenta para esa sede
- **And** cuando se completa, la sede cambia a `active`

---

### 30. Facturación consolidada B2B por flota

**Como** Admin de empresa con flota **quiero** recibir una factura mensual con todas las transacciones de mis vehículos **para** simplificar mi contabilidad.

**Criterios de aceptación:**
- **Given** la empresa tiene 50 vehículos registrados en ParkCore
- **When** termina el mes y hay transacciones de uso de esos vehículos
- **Then** se genera una factura consolidada con: resumen de transacciones por vehículo, total a pagar, detalle por sede
- **And** la factura se entrega al email financiero registrado
- **And** se genera nota débito/crédito si hay ajustes

---

*Total: 30 historias de usuario (12 core + 18 SaaS)*