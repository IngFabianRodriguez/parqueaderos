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
|- **And** se genera nota débito/crédito si hay ajustes

---

### 31. Modo manual: operar sin talanqueras ni ANPR

**Como** Operador de un parqueadero pequeño sin dispositivos IoT **quiero** registrar entradas y salidas desde la app móvil **para** usar ParkCore sin inversión en hardware.

**Criterios de aceptación:**
- **Given** la sede está configurada en modo `manual` (sin dispositivos)
- **When** el operador abre la app y toca "Registrar entrada"
- **Then** el sistema muestra un formulario: placa (manual o selec. cliente), fecha/hora (default ahora), observación opcional
- **And** la entrada se registra igual que si hubiera pasado por una talanquera
- **And** al registrar salida, el sistema calcula duración y muestra el valor a pagar
- **And** el operador puede registrar el pago manualmente

---

### 32. Cambiar modo de operación de una sede

**Como** Admin de tenant **quiero** cambiar el modo de operación de una sede de `iot` a `manual` (o viceversa) **para** adaptarme a mi presupuesto o infraestructura.

**Criterios de aceptación:**
- **Given** la sede tiene 6 meses de datos en modo `iot`
- **When** el admin cambia el modo a `manual` desde el panel de configuración
- **Then** los datos históricos se preservan intactamente
- **And** las talanqueras y sensores quedan como "desactivados" pero no se eliminan
- **And** los operadores ven la interfaz de modo manual al día siguiente

---

### 33. Personalizar labels de la interfaz

**Como** Admin de tenant en Colombia **quiero** que las zonas se llamen "bahías" en lugar de "espacios" **para** que la interfaz sea familiar para mis operadores.

**Criterios de aceptación:**
- **Given** el tenant opera en Cartagena y sus operadores hablan de "bahías"
- **When** el admin guarda la configuración: `{"espacio_label": "bahía", "zona_label": "sección", "sede_label": "parqueadero"}`
- **Then** toda la app móvil y dashboard del tenant muestra los labels personalizados
- **And** los reportes también usan esos labels en headers y columnas

---

### 34. Activar/desactivar módulos completos

**Como** Admin de tenant **quiero** desactivar el módulo de CRM si mi parqueadero solo hace cobro puntual sin clientes frecuentes **para** simplificar la interfaz para mis operadores.

**Criterios de aceptación:**
- **Given** el tenant no necesita el módulo de clientes ni facturación electrónica
- **When** el admin desactiva `modulos_activos.crm = false`
- **Then** el menú de CRM desaparece del dashboard del tenant
- **And** los operadores no ven opciones de registro de clientes
- **And** el sistema sigue funcionando para operaciones básicas de entrada/salida/pago

---

### 35. Configurar templates de notificación

**Como** Admin de tenant **quiero** personalizar el mensaje que reciben mis clientes al entrar al parqueadero **para** reforzar mi marca.

**Criterios de aceptación:**
- **Given** el tenant quiere un mensaje personalizado de bienvenida
- **When** el admin edita el template de notificación de entrada: `"Bienvenido a {{sede_nombre}}, su espacio está en zona {{zona}}"`
- **Then** todos los clientes que ingresan reciben ese mensaje
- **And** el sistema permite variables: `{{sede_nombre}}`, `{{cliente_nombre}}`, `{{fecha}}`, `{{placa}}`
- **And** existe preview en tiempo real antes de guardar

---

### 36. Definir reglas de tarifación especiales

**Como** Admin de tenant **quiero** configurar tarifas especiales para Navidad y temporada alta **para** cobrar correctamente en fechas especiales.

**Criterios de aceptación:**
- **Given** el parqueadero quiere cobrar 1.5x en diciembre
- **When** el admin crea una regla: `{ "nombre": "Temporada alta", "desde": "2026-12-01", "hasta": "2026-12-31", "multiplicador": 1.5, "aplicable_a": ["todas"] }`
- **Then** durante ese periodo el sistema aplica el multiplicador automáticamente
- **And** las facturas generadas mostram el detalle de la regla especial aplicada

---

### 37. Configurar webhooks para integraciones

**Como** Admin de tenant (desarrollador) **quiero** recibir eventos de ParkCore en mi sistema propio **para** integrarme con el flujo de la empresa.

**Criterios de aceptación:**
- **Given** el tenant quiere que cada pago realizado envie un POST a `https://api.empresa.com/webhook/parkcore`
- **When** el admin configura: `{ "url": "https://api.empresa.com/webhook/parkcore", "eventos": ["pago.completado", "entrada.registrada"], "auth_header": "Bearer token123" }`
- **Then** el sistema envía webhooks a esa URL cuando ocurren esos eventos
- **And** el admin puede ver el log de webhooks con: intentos, códigos de respuesta, cuerpos enviados
- **And** puede reenviar manualmente un webhook fallido

---

### 38. Probar webhook antes de activar

**Como** Admin de tenant **quiero** enviar un webhook de prueba antes de activar la integración **para** verificar que la URL receptora funciona.

**Criterios de aceptación:**
- **Given** el admin ha configurado un webhook con URL y eventos
- **When** toca el botón "Probar conexión"
- **Then** el sistema envía un payload de prueba a la URL configurada
- **And** muestra en tiempo real: código HTTP respuesta, cuerpo respuesta, latencia
- **And** si el respuesta es 2xx, muestra check verde; si no, muestra error con detalle

---

### 39. Configurar campos obligatorios en registro manual

**Como** Admin de tenant **quiero** que el registro manual de entrada requiera sí o sí la placa **para** mantener trazabilidad even sin ANPR.

**Criterios de aceptación:**
- **Given** la sede opera en modo `manual`
- **When** el admin configura: `{ "requiere_placa": true, "permite_sin_placa": false }`
- **Then** el operador no puede registrar entrada sin ingresar la placa
- **And** si intenta hacerlo, ve el mensaje: "Debe ingresar la placa para continuar"
- **And** el historial muestra todas las placas registradas

---

### 40. Restringir acceso de operadores a sedes específicas

**Como** Admin de empresa con múltiples sedes **quiero** que el operador de la sede Centro solo vea datos de esa sede **para** mantener independencia entre ubicaciones.

**Criterios de aceptación:**
- **Given** el operador "Juan" tiene `sede_ids = [id_sede_centro]`
- **When** Juan inicia sesión
- **Then** ve únicamente el dashboard de la sede Centro
- **And** no puede ver reportes, transacciones ni configuraciones de la sede Norte
- **And** si intenta acceder por URL directa a la sede Norte, recibe 403

---

### 41. Definir promoción con uso máximo

**Como** Admin de tenant **quiero** crear un descuento del 20% para los primeros 100 clientes del mes **para** impulsar uso en temporada baja.

**Criterios de aceptación:**
- **Given** el admin crea promoción: `{ "nombre": "20% off mayo", "descuento_pct": 20, "max_uso": 100, "valido_desde": "2026-05-01", "valido_hasta": "2026-05-31" }`
- **Then** el sistema permite el descuento a los primeros 100 clientes
- **And** al llegar a 100 usos, el descuento deja de aplicarse automáticamente
- **And** el admin ve el contador de usos en el dashboard

---

### 42. Dashboard de salud del sistema (Observabilidad)

**Como** Equipo interno de ParkCore **quiero** ver en tiempo real qué microservicios están arriba o caídos **para** reaccionar antes de que los clientes se quejen.

**Criterios de aceptación:**
- **Given** el equipo accede al dashboard de salud
- **When** todos los microservicios están responding
- **Then** muestra verde con uptime del día: "api-gateway ✓, auth-service ✓, parking-service ✓"
- **And** cuando un servicio deja de responder, el recuadro pasa a rojo y envía alerta a Slack

---

### 43. Configurar umbral de alerta y canal de notificación

**Como** Tenant_admin **quiero** recibir una alerta por Slack cuando la latencia de la API exceda 500ms **para** estar informado sin recibir spam por email.

**Criterios de aceptación:**
- **Given** el tenant tiene configurado un umbral de alerta: latencia > 500ms por 3 min
- **When** la latencia de la API Gateway llega a 600ms durante 4 minutos
- **Then** se dispara una alerta con severity "warning" al canal de Slack configurado
- **And** el evento queda registrado en alerta_evento con trace_id para debugging

---

### 44. Heartbeat de talanquera y alerta offline

**Como** Operador de sede **quiero** recibir alerta cuando una talanquera lleva 2 minutos sin responder **para** evitar que los vehículos queden atrapados.

**Criterios de aceptación:**
- **Given** la talanquera T1 deja de enviar heartbeats (normalmente cada 60s)
- **When** pasan 120 segundos sin heartbeat
- **Then** el sistema marca T1 como "offline" en el dashboard
- **And** el operador recibe push notification: "⚠️ Talanquera T1 offline hace 2min"
- **And** se crea un alerta_evento con severity "critical"

---

### 45. Generar reporte de ingresos con comparativa

**Como** Admin de sede **quiero** ver el reporte de ingresos de mayo con comparativa vs abril **para** entender cómo vamos vs el mes pasado.

**Criterios de aceptación:**
- **Given** el admin selecciona reporte de ingresos para mayo 2026
- **Then** el sistema muestra: total ingresos $45.2M COP, 1,847 transacciones, forma de pago breakdown
- **And** comparativa automática: "vs abril: +12.3% (abril: $40.2M, 1,620 transacciones)"
- **And** exportable a Excel y PDF

---

### 46. Programar reporte diario de morosidad

**Como** Admin de tenant **quiero** recibir un email cada lunes con el reporte de morosos **para** hacer seguimiento sin entrar al sistema.

**Criterios de aceptación:**
- **Given** el admin configura un reporte programado: morosidad, frecuencia weekly, cada lunes 8am, email gerencia@empresa.com
- **When** llega el lunes a las 8am
- **Then** el sistema genera el reporte y lo envía a gerencia@empresa.com
- **And** se guarda un registro en reporte_log con: destinatario, hora envío, estado, file_url

---

### 47. Operador hace cierre de turno con diferencia de caja

**Como** Operador **quiero** reportar el cierre de turno al final de mi jornada **para** dejar la caja cuadrada y con registro.

**Criterios de aceptación:**
- **Given** el operador ha trabajado 8 horas y la caja debería tener $2,350,000
- **When** cuenta el dinero físico y encuentra $2,340,000 (diferencia de -$10,000, que es -0.43%)
- **Then** el sistema marca el cierre como "en discrepancia"
- **And** el operador debe ingresar justificación: "Falta un billete de $10,000 - se cayó al suelo"
- **And** el admin recibe notificación de cierre con discrepancia

---

### 48. Cliente crea ticket de soporte desde la app

**Como** Cliente que tuvo problema con el cobro **quiero** reportarlo desde la app sin llamar **para** dejar registro escrito de mi queja.

**Criterios de aceptación:**
- **Given** el cliente fue cobrado dos veces por la misma transacción
- **When** abre la app, toca "Ayuda" → "Reportar problema", selecciona la transacción y describe el error
- **Then** se crea un ticket con tipo "incidente", prioridad "alta", estado "open"
- **And** el operador de la sede recibe la notificación del ticket
- **And** el cliente recibe confirmación: "Tu ticket #2847 fue creado, tiempo estimado de respuesta: 2 horas"

---

### 49. Cliente deja feedback después de la transacción

**Como** Cliente **quiero** calificar mi experiencia después de salir del parqueadero **para** que el operador sepa cómo estoy.

**Criterios de aceptación:**
- **Given** el cliente completó su transacción y salió del parqueadero
- **When** recibe la notificación "Califica tu experiencia"
- **Then** puede calificar 1-5 estrellas y dejar un comentario opcional
- **And** el admin de la sede ve la calificación en el dashboard: "Calificación promedio: 4.3 ★ (últimos 30 días)"
- **And** si la calificación es 1-2 estrellas, el ticket se eleva a prioridad "urgente"

---

### 50. App operador: abrir talanquera manualmente

**Como** Operador **quiero** abrir la talanquera desde la app si el sistema automático falla **para** no dejar a un cliente atrapado.

**Criterios de aceptación:**
- **Given** la talanquera de salida está cerrada y el cliente no tiene cómo pagar (la app de pago está caída)
- **When** el operador toca "Abrir talanquera" y confirma con doble tap
- **Then** el comando se envía al dispositivo
- **And** se registra en auditoría: "talanquera_abierta_manual, operador Juan Pérez, motivo: falla_sistema_pago"
- **And** el admin recibe notificación del evento

---

### 51. Cliente hace prepago desde la app

**Como** Cliente **quiero** pagar anticipadamente mi parqueo antes de llegar al parqueadero **para** no preocuparme por el pago al salir.

**Criterios de aceptación:**
- **Given** el cliente tiene vehículo Mazda CX-5 placas ABC123 registrado en la app
- **When** desde la app selecciona "Prepagar" y elige 2 horas
- **Then** se genera un prepago de $12,000 que queda asociado a la placa ABC123
- **And** cuando el vehículo entre, el sistema detecta que tiene crédito prepagado y habilita la salida
- **And** al salir no necesita hacer pago adicional

---

### 52. Admin configura horarios de silencio para mantenimiento

**Como** Tenant_admin **quiero** configurar una ventana de silencio de 2am-4am los domingos para que las alertas de mantenimiento no molesten **para** evitar waking a nadie en la noche.

**Criterios de aceptación:**
- **Given** el admin configura una alerta: "CPU > 80%" canal email
- **And** configura ventana de silencio: domingo 2am-4am
- **When** el domingo a las 2:30am el CPU llega a 85%
- **Then** la alerta NO se envía
- **And** queda registrada en alerta_evento con metadata "silenciada: true"
- **When** a las 5am sigue en 85% CPU
- **Then** la alerta SÍ se envía

---

### 53. Ver audit log filtrado por usuario y acción

**Como** Tenant_admin **quiero** buscar el audit log para saber qué hizo el operador "María" ayer **para** resolver una dispute.

**Criterios de aceptación:**
- **Given** hay un audit log inmutable de todas las acciones
- **When** el admin filtra: usuario "María", acción "talanquera_abierta", ayer
- **Then** el sistema muestra: "María abrió talanquera T2 el 2026-05-07 14:32:15 (turno tarde) motivo: emergencia"
- **And** no se puede modificar ni eliminar ningún registro del audit log

---

### 54. Chat en tiempo real entre cliente y operador

**Como** Cliente **quiero** chatear con el operador desde la app si tengo un problema **para** resolverlo sin llamar ni esperar ticket.

**Criterios de aceptación:**
- **Given** el cliente tiene un ticket abierto #2847
- **When** dentro del ticket toca "Chatear ahora"
- **Then** se abre un chat en tiempo real con el operador asignado
- **And** los mensajes aparecen instantáneamente (WebSocket)
- **And** el operador puede responder desde su app o desde el admin web

---

### 55. Admin ve dashboard NPS por sede

**Como** Tenant_admin **quiero** ver el NPS de cada sede para saber dónde está fallando la experiencia **para** tomar decisiones de mejora.

**Criterios de aceptación:**
- **Given** en los últimos 30 días hubo 847 feedbacks
- **When** el admin accede al dashboard de satisfacción
- **Then** ve: NPS global 62, sede Centro 58, sede Norte 71, sede Sur 55
- **And** la sede Sur con NPS 55 tiene un ticket abierto de un cliente que se quejó de "tiempo de espera muy largo"
- **And** puede filtrar por período, сравнивать con mes anterior

---

*Total: 55 historias de usuario (12 core + 18 SaaS + 25 ops/support/apps)*