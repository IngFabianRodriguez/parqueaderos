# 3. Arquitectura Técnica

En este capítulo se describe la arquitectura tecnológica propuesta para la plataforma de gestión de parqueaderos. Se detallan las decisiones de diseño, el modelo de datos, el stack tecnológico recomendado, los mecanismos de seguridad y las integraciones con servicios externos. El objetivo es proporcionar una solución robusta, escalable y mantenible, capaz de soportar las operaciones diarias de uno o múltiples parqueaderos con alta disponibilidad y rendimiento óptimo.

---

## 3.1 Arquitectura General del Sistema

### 3.1.1 Decisión de Arquitectura: Monolito Modular vs. Microservicios

Se propone una **arquitectura de monolito modular** como punto de partida, con la posibilidad de evolucionar hacia microservicios de forma incremental conforme la plataforma escale. Esta decisión se fundamenta en varios criterios técnicos y operativos:

En primer lugar, la **complejidad inicial** de un parqueadero es manejable dentro de un solo dominio de negocio. Las operaciones de entrada, salida, facturación y control de acceso comparten un modelo de datos cohesivo que se beneficia de transacciones ACID locales. Migrar prematuramente a microservicios introduce overhead de red, consistencia eventual y complejidad operacional que no se justifica con el volumen inicial de operaciones.

En segundo lugar, la **velocidad de desarrollo** es significativamente mayor en un monolito modular. Los equipos pueden compartir código, modelos de datos y bibliotecas sin necesidad de contratos de API ni coordinación entre servicios independientes. Esto es especialmente relevante en las fases iniciales del proyecto, donde los requisitos de negocio aún están evolucionando.

Finalmente, se contempla la **evolución hacia microservicios** para módulos específicos que lo ameriten: el motor de procesamiento de eventos IoT, el módulo de ANPR (Automatic Number Plate Recognition) y el motor de análisis y reportes avanzados. Estos componentes pueden convertirse en servicios independientes cuando su carga computacional o su necesidad de escalamiento independiente lo justifiquen, siguiendo el patrón **Strangler Fig**.

### 3.1.2 Diagrama de Capas

La arquitectura se organiza en tres capas claramente diferenciadas:

**Capa de Presentación**: Comprende el dashboard web administrativo, la aplicación móvil para clientes y la aplicación móvil para operadores de parqueadero. Esta capa se comunica exclusivamente con la capa de lógica de negocio a través de APIs RESTful o GraphQL. No tiene acceso directo a la base de datos ni a los dispositivos IoT.

**Capa de Lógica de Negocio (API)**: Contiene toda la inteligencia del sistema, incluyendo la gestión de espacios, el control de talanqueras, el procesamiento de pagos, la aplicación de tarifas, el manejo de eventos IoT y la generación de reportes. Esta capa está construida como un conjunto de módulos dentro del monolito, cada uno encapsulando un subdominio del negocio. Expone interfaces bien definidas hacia la capa de presentación y hacia los dispositivos IoT.

**Capa de Datos (Persistencia)**: Incluye el motor de base de datos principal (PostgreSQL), los sistemas de caché y tiempo real (Redis), la base de datos de series de tiempo para sensores (TimescaleDB), y el almacenamiento de objetos para grabaciones de video y evidencias fotográficas (S3 o compatible). Esta capa es accedida exclusivamente por la capa de lógica de negocio, nunca de forma directa por la capa de presentación ni por los dispositivos IoT.

### 3.1.3 Cómputo: Cloud-First con Opción On-Premise

Se recomienda un enfoque **cloud-first** utilizando Amazon Web Services (AWS), Google Cloud Platform (GCP) o Microsoft Azure como proveedores de infraestructura. La selección del proveedor cloud específico se realizará en función de factores como la presencia regional del cliente, los costos de transferencia de datos, la integración con servicios de IA/ML, y las políticas de cumplimiento normativo aplicables.

Para clientes del segmento **enterprise** que requieran control total sobre su infraestructura o que tengan restricciones regulatorias de datos, se ofrece la opción **on-premise**. En este modo, la plataforma se despliega en los propios servidores del cliente utilizando la misma arquitectura de contenedores, lo que garantiza paridad funcional entre ambos modos de operación. La operación on-premise se soporta principalmente en escenarios donde la normatividad sectorial o corporativa impide el almacenamiento de datos en la nube pública.

### 3.1.4 Alta Disponibilidad

El diseño de alta disponibilidad contempla dos escenarios según el modelo de operación:

**Modelo activo-pasivo por sede**: En configuraciones de menor escala, se despliega un nodo principal que atiende todas las operaciones y un nodo secundario en espera. El nodo secundario monitorea continuamente la disponibilidad del principal mediante heartbeats y asume el control en caso de falla. Este modelo es adecuado para parqueaderos individuales con tolerancia a un tiempo de recuperación moderado (RTO menor a 15 minutos).

**Modelo activo-activo por sede**: Para operaciones de mayor criticidad o múltiples sedes, se despliegan múltiples nodos que atienden solicitudes simultáneamente. El balanceador de carga distribuye las peticiones entre los nodos disponibles, y la base de datos se replica de forma síncrona. Este modelo permite tolerancia a fallas de nodos individuales sin interrupción del servicio, reduciendo el RTO a prácticamente cero para las operaciones críticas.

La selección entre activo-pasivo y activo-activo se realiza en función del SLA acordado con el cliente, el volumen de transacciones y el presupuesto disponible.

### 3.1.5 Modelo de Despliegue: Contenedores y Orquestación

Todos los componentes de la plataforma se empaquetan como **contenedores Docker** utilizando imágenes minimalistas basadas en distroless o Alpine para reducir la superficie de ataque. Los contenedores se orquestan mediante **Kubernetes** (o Amazon EKS / Google GKE / Azure AKS según el proveedor cloud seleccionado), lo que proporciona:

- **Auto-scaling** horizontal y vertical basado en métricas de consumo de CPU, memoria y solicitudes por segundo.
- **Service discovery** automático para que los servicios se descubran entre sí sin configuración manual de endpoints.
- **Rolling updates** y rollbacks sin tiempo de inactividad.
- **Gestión de secretos** integrada para credenciales, certificados y claves de API.
- **Health checks** y auto-recuperación de pods que fallen.

### 3.1.6 Zonas de Red

La arquitectura de red se segmenta en tres zonas con políticas de firewall restrictivas:

**DMZ (Zona Desmilitarizada)**: En esta zona se sitúan los dispositivos de edge computing, las cámaras de CCTV, los lectores de placas (ANPR), los sensores de ocupación de espacios y las talanqueras inteligentes. Estos dispositivos se comunican exclusivamente con el broker MQTT situado también en la DMZ, nunca directamente con la red core ni con Internet. La DMZ está aislada de la red core por un firewall stateful que solo permite tráfico saliente hacia el broker MQTT.

**Red Core (Red de Aplicación)**: Alberga los servicios de API, la base de datos, los servicios de mensajería, el motor de procesamiento de eventos y todos los componentes de lógica de negocio. El acceso desde la DMZ está restringido al broker MQTT y a ningún otro servicio. El acceso desde Internet se realiza exclusivamente a través del API Gateway situado en la DMZ.

**Red de Gestión**: Destinada a la administración de la infraestructura, acceso SSH a servidores, consoles de monitoreo y paneles de administración. Esta red tiene acceso restringido a direcciones IP específicas y requiere autenticación multifactor.

---

## 3.2 Modelo de Datos

### 3.2.1 Entidades Principales

El modelo de datos se centra en las siguientes entidades fundamentales que representan los conceptos core del dominio de parqueaderos:

**Sede**: Representa un parqueadero físico individual. Contiene información como nombre comercial, dirección, coordenadas geográficas, horario de operación, configuración de moneda y datos de contacto del responsable. Cada sede opera de manera independiente en términos de tarifas, espacios y personal.

**Zona**: Una subdivisión lógica de una sede que agrupa espacios con características similares. Por ejemplo, "Zona Cubierta", "Zona Exterior", "Zona VIP", "Zona de Motos". Cada zona puede tener su propio conjunto de tarifas y reglas de negocio.

**Espacio**: Representa una plaza de estacionamiento individual. Cada espacio pertenece a una zona y tiene un identificador físico (por ejemplo, "A-15"), tipo de vehículo autorizado (automóvil, moto, bicicleta, etc.), estado actual (libre, ocupado, reservado, mantenimiento) y tipo de tecnología de detección (sensor de ocupación, cámara ANPR, etc.).

**Vehículo**: Contiene información de los vehículos registrados en el sistema. Incluye placa, tipo de vehículo, marca, modelo, color, fotografía y datos del propietario. La placa es el identificador primario y se utiliza para las búsquedas de ANPR.

**Registro**: Representa la entrada o salida de un vehículo al parqueadero. Cada evento de entrada genera un registro de entrada y cada evento de salida genera un registro de salida, ambos vinculados al mismo ticket o sesión. El registro contiene timestamps precisos (con zona horaria), datos del espacio asignado, identificación del dispositivo que generó el evento (cámara, sensor, operador manual) y resultado de la verificación de placa.

**Pago**: Registra cada transacción de pago realizada. Incluye el monto, la moneda, el método de pago (efectivo, PSE, tarjeta crédito/débito, wallet digital), el estado de la transacción (pendiente, completado, fallido, reembolsado), la referencia externa del procesador de pagos, y el registro o registros asociados a los que corresponde el pago.

**Cliente**: Representa la persona natural o jurídica que utiliza el parqueadero. Un cliente puede tener múltiples vehículos registrados y múltiples métodos de pago. Los clientes se clasifican en ocasionales (no registrados) y frecuentes (registrados en el sistema).

**PlanTarifario**: Define las tarifas aplicables a una zona o a un tipo de cliente. Contiene tarifa base, tarifa por hora adicional, tarifas nocturnas, tarifas de paquetes (diario, semanal, mensual), descuentos por fidelidad y reglas de tarifación especiales (horas valle, temporada alta, etc.).

**Talanquera**: Representa una barrera física de acceso. Cada talanquera está asociada a una sede, tiene un tipo (entrada, salida, entrada/salida), un identificador del controlador (IP, MAC), y se vincula a los espacios que controla si es una talanquera de zona.

**EventoIoT**: Almacena los eventos generados por dispositivos IoT (sensores, cámaras, lectores). Incluye tipo de evento, dispositivo origen, timestamp, payload con datos específicos del evento (imagen, lectura de sensor, estado de alarma), y referencia al registro associated si el evento está correlacionado con una operación de negocio.

**Usuario**: Representa a una persona con acceso al sistema. Contiene credenciales de autenticación (hash de contraseña, factores de segundo factor), perfil de acceso, datos personales y estado de la cuenta. Los usuarios pueden ser administradores, operadores de piso, cobradores o clientes.

**Rol**: Define un conjunto de permisos dentro del sistema. Los roles se asignan a los usuarios y determinan qué operaciones pueden realizar. Los roles prédéfinidos incluyen superadmin, admin_sede, operador, cobrador y cliente.

### 3.2.2 Relaciones entre Entidades

Las relaciones entre entidades se organizan de la siguiente manera:

Una **Sede** contiene una o múltiples **Zonas**. Esta relación es de uno a muchos: cada zona pertenece exclusivamente a una sede y no puede compartirse entre sedes. Esta restricción garantiza que la gestión de espacios y tarifas sea autocontenida dentro de cada parqueadero.

Una **Zona** contiene cero o múltiples **Espacios**. La relación es de uno a muchos: los espacios siempre pertenecen a una zona y una zona puede tener desde cero espacios (en configuración inicial) hasta cientos de ellos.

Un **Espacio** puede estar asociado a cero o un **Vehículo** en un momento dado a través del **Registro** activo. En cualquier instante, un espacio está libre (sin vehículo asociado) u ocupado (con un vehículo cuya entrada está registrada pero aún no tiene salida registrada).

Un **Registro** pertenece a exactamente un **Vehículo** y a exactamente una **Sede**. Un vehículo puede tener múltiples registros a lo largo del tiempo (historial) y una sede genera múltiples registros. Un registro está asociado a un **Espacio** específico donde se estacionó el vehículo.

Un **Pago** está asociado a uno o más **Registros** (en el caso de pagos que cubran múltiples días o sesiones) y a un **Cliente** que realizó el pago. Un cliente puede tener múltiples pagos en su historial.

Un **Cliente** puede tener cero o múltiples **Vehículos** registrados a su nombre. Un vehículo pertenece a un único cliente (aunque puede haber vehículos compartidos entre varios clientes en configuraciones especiales).

Un **PlanTarifario** aplica a una **Zona** específica y puede aplicarse a uno o múltiples **Clientes** (en el caso de planes corporativos o de fidelidad). La relación entre zonas y planes es de muchos a muchos a través de una tabla intermedia que permite vigencia temporal de tarifas.

Las **Talanqueras** están asociadas a una **Sede** y pueden estar vinculadas a una **Zona** específica (en cuyo caso controlan el acceso a los espacios de esa zona) o funcionar como talanqueras de perímetro de sede.

Los **EventoIoT** están asociados al **Dispositivo** que los generó (identificado por su ID único) y opcionalmente a un **Espacio** o **Registro** cuando el evento es relevante para una operación de negocio específica.

Los **Usuarios** tienen asignado un **Rol** que determina sus permisos. Un usuario puede tener múltiples roles (por ejemplo, un administrador de sede que también opera en piso). Los roles están definidos globalmente pero los usuarios están asociados a una o más sedes según su ámbito de trabajo.

### 3.2.3 Motor de Base de Datos

**PostgreSQL** se selecciona como motor de base de datos principal por las siguientes razones técnicas:

- Soporte robusto de transacciones ACID con cumplimiento total de propiedades ACID, indispensable para la integridad financiera de las operaciones de cobro.
- Excelente manejo de datos geométricos y geográficos a través de la extensión PostGIS, útil para consultas de proximidad y geofencing.
- Sistema de índices avanzados incluyendo B-tree, Hash, GIN, GiST y BRIN, que permiten optimizar consultas complejas sobre eventos y registros.
- Soporte nativo para JSON y JSONB, facilitando el almacenamiento de payloads variables de eventos IoT.
- Replicación lógica y físicas que garantizan alta disponibilidad y opciones de lectura distribuida.
- Amplio ecosistema de herramientas de monitoreo, respaldo y administración.

**Redis** se utiliza para dos propósitos fundamentales:

- **Caché de consultas frecuentes**: información de espacios disponibles, tarifas actuales y datos de clientes frecuentes. El caché se invalida estratégicamente cuando los datos subyacentes cambian.
- **Almacenamiento de estado en tiempo real**: sesiones de usuario, contadores atómicos de espacios disponibles, locks distribuidos para evitar condiciones de carrera en la asignación de espacios, y cola de mensajes para procesamiento asíncrono.

**TimescaleDB** (una extensión de PostgreSQL) se encarga del almacenamiento de series de tiempo generadas por los sensores IoT. Su arquitectura hypertable permite consultas analíticas eficientes sobre millones de eventos de sensores con particionamiento automático por tiempo. Es la elección ideal para almacenar datos de sensores de ocupación, eventos de talanqueras y métricas de uso.

### 3.2.4 Estrategia de Retención de Datos

La estrategia de retención de datos se basa en un modelo de **tiers de temperatura** que optimiza costos de almacenamiento y rendimiento:

**Tier Hot (Datos Activos)**: Los últimos 90 días de eventos IoT, registros de entrada/salida y pagos se almacenan en TimescaleDB con discos de alta velocidad (SSD NVMe). Estos datos son accesibles para consultas operativas en tiempo real, reportes de gestión y detección de anomalías. Los índices están optimizados para consultas por rango de fechas y por sede.

**Tier Warm (Datos Históricos)**: Los datos entre 90 días y 2 años se transfieren a almacenamiento de menor costo (discos HDD o object storage con acceso infrecuente). Estos datos permanecen en TimescaleDB pero en chunks archivados. Están disponibles para consultas bajo demanda, auditorías y reportes históricos. Las consultas sobre este tier tienen latencia mayor pero son soportadas.

**Tier Cold (Archivo)**: Los datos con más de 2 años se mueven a almacenamiento de archivo (Amazon S3 Glacier o equivalente) con compresión y opcionalmente encriptación adicional. Estos datos se conservan por razones legales y regulatorias. El acceso requiere un proceso de restauración que puede tomar de minutos a horas. La información de clientes y vehículos sensibles se retiene según las políticas de privacidad aplicables.

Los **logs de auditoría** (acciones de operadores, cambios de tarifa, aperturas manuales de talanquera) se retienen en un bucket de object storage separado con formato estructurado (JSON Lines) para facilitar análisis de seguridad.

### 3.2.5 Índices y Particionamiento

El particionamiento de tablas se implementa en dos dimensiones principales:

**Por sede**: Las tablas más grandes (Registro, EventoIoT, Pago) se particionan horizontalmente por sede utilizando el esquema de particionamiento declarativo de PostgreSQL. Cada partición corresponde a una sede y contiene únicamente los datos de esa sede. Esto permite архивировать y eliminar datos de una sede específica sin afectar las demás, y facilita el cumplimiento de requisitos de localización de datos.

**Por rango de fechas**: Dentro de cada partición por sede, las tablas de eventos se subdividen por rangos de tiempo (típicamente mensual o semanal según el volumen). Esto optimiza las consultas por rango de fechas que son frecuentes en reportes de gestión, y permite la purga eficiente de datos antiguos mediante detachment de particiones.

Los índices se crean estratégicamente para las consultas más frecuentes:

- Índice compuesto en (sede_id, fecha_entrada) para consultas de ocupación por fecha.
- Índice en (placa, fecha) para búsqueda de historial vehicular.
- Índice en (espacio_id, estado) para consulta de espacios disponibles.
- Índice en (cliente_id, fecha_pago) para historial de pagos por cliente.

---

## 3.3 Stack Tecnológico Recomendado

### 3.3.1 Capa de Presentación

**Dashboard Web**: Se recomienda **React** como framework de frontend por su ecosistema maduro, la disponibilidad de desarrolladores en el mercado y su excelente rendimiento con aplicaciones de una sola página (SPA). Como biblioteca de componentes UI se sugiere **PrimeNG** o **Material UI**, que proporcionan componentes empresariales listos para producción. Para la gestión de estado global se puede utilizar Redux Toolkit o Zustand, y para la comunicación con APIs, Axios o TanStack Query.

**Aplicación Móvil (Clientes)**: Se recomienda **Flutter** para el desarrollo cross-platform nativo. Flutter ofrece rendimiento nativo comparable a aplicaciones escritas en Kotlin o Swift, con una sola base de código para iOS y Android. Su sistema de widgets permite crear interfaces de usuario consistentes con el diseño del dashboard web.Alternativamente, **React Native** es una opción válida si el equipo de desarrollo tiene experiencia previa en React, ya que permite compartir lógica de negocio y estructura de proyecto con el dashboard web.

**Aplicación Móvil (Operadores)**: Para los módulos de operador de piso y cobrador, se recomienda una aplicación móvil liviana basada en **React Native** que pueda compartir componentes con el dashboard web. Esta aplicación necesita funcionar offline en escenarios de pérdida de conectividad con el servidor central, sincronizando datos cuando la conexión se restored.

### 3.3.2 Capa de Lógica de Negocio (Backend)

Se evaluaron dos opciones principales para el backend:

**NestJS (Node.js/TypeScript)**: Ofrece una arquitectura modular similar a Angular, con inyección de dependencias, pipes, guards y decorators que facilitan el desarrollo de APIs robustas. TypeScript proporciona tipado estático que reduce errores en tiempo de desarrollo. El ecosistema npm ofrece bibliotecas maduras para prácticamente cualquier integración. NestJS es especialmente adecuado para equipos con experiencia en JavaScript/TypeScript y para proyectos que requieran alta productividad.

**FastAPI (Python)**: Framework moderno de Python que ofrece rendimiento comparable a Node.js gracias a su base en Starlette y Uvicorn. Soporta generación automática de documentación OpenAPI y validación de datos con Pydantic. Es ideal para equipos con experiencia en Python y para proyectos que requieran integración intensiva con bibliotecas de machine learning o ciencia de datos.

**Decisión**: Se recomienda **NestJS** como opción principal por su arquitectura modular que se alinea con el enfoque de monolito modular, su excelente soporte para TypeScript que mejora la mantenibilidad del código, y su ecosistema maduro para desarrollo empresarial. FastAPI se recomienda como alternativa cuando el proyecto requiera integración profunda con modelos de ML para ANPR o analítica predictiva.

### 3.3.3 Message Broker para Eventos IoT

Para la ingestión de eventos provenientes de dispositivos IoT se recomienda **Apache Kafka** como broker de mensajes. Kafka ofrece:

- Alta capacidad de throughput (millones de mensajes por segundo), adecuado para escenarios con múltiples cámaras y sensores enviando eventos constantemente.
- Persistencia en disco con replicación, garantizando que ningún evento se pierda incluso ante fallas de componentes.
- Modelo de consumo por grupos que permite que múltiples consumidores procesen los mismos eventos (por ejemplo, uno para actualizar estado en tiempo real y otro para analítica).
- Retención configurable que permite reprocesar eventos en caso de errores de consumo.

Como alternativa, **RabbitMQ** es una opción válida para despliegues de menor escala o cuando se prefiera un modelo de cola tradicional con acknowledgment de mensajes. RabbitMQ es más simple de operar pero tiene limitaciones en throughput comparadas con Kafka.

### 3.3.4 Protocolo IoT: MQTT

**MQTT** (Message Queuing Telemetry Transport) es el protocolo recomendado para la comunicación con dispositivos IoT. Su diseño ligero lo hace ideal para dispositivos con recursos limitados y conexiones de red no siempre disponibles. El broker MQTT (por ejemplo, Mosquitto o EMQX) se sitúa en la DMZ y recibe mensajes de los dispositivos. El backend consume estos mensajes a través del Kafka Connect MQTT o mediante un servicio puente.

### 3.3.5 ANPR (Reconocimiento Automático de Placas)

Para el reconocimiento de placas vehiculares se contemplan dos Approaches:

**Integración con APIs de terceros**: Servicios como **Plate Recognizer** u **OpenALPR** ofrecen APIs de reconocimiento de placas con alta precisión y bajo costo. Se envían las imágenes capturadas por las cámaras y el servicio retorna la placa detectada junto con la confianza de la lectura. Esta Approach es rápida de implementar y no requiere infraestructura de ML propia.

**Modelo propio con YOLO**: Para casos de uso con volúmenes muy altos o requisitos de personalización (por ejemplo, reconocimiento de placas colombianas con formatos específicos), se puede entrenar un modelo de YOLO (You Only Look Once) optimizado para el dominio local. Este modelo se despliega en GPUs de edge computing y ofrece latencia mínima y control total sobre el procesamiento.

Se recomienda iniciar con la integración de APIs de terceros y evolucionar hacia un modelo propio si los costos de API lo justifican o si se requieren capacidades no disponibles (por ejemplo, reconocimiento de placas en condiciones de iluminación difíciles específicas del entorno).

### 3.3.6 Notificaciones

**Firebase Cloud Messaging (FCM)** se recomienda para el envío de push notifications a las aplicaciones móviles. FCM es gratuito hasta un volumen significativo de mensajes y ofrece alta deliverabilidad en Android. Para iOS se requiere configuración adicional del APNs, pero FCM abstrae esta complejidad.

Para **SMS** se recomienda **Twilio** o **Vonage** (anteriormente Nexmo). Ambos ofrecen cobertura internacional, APIs bien documentadas y tarifas competitivas para el mercado colombiano. Twilio es la opción con mayor presencia en América Latina.

### 3.3.7 Pasarelas de Pago

Para el mercado colombiano se recomienda integración con pasarelas de pago locales que ofrezcan métodos de pago populares en la región:

**Wompi**: Pasarela de pago colombiana que soporta pagos con tarjeta de crédito/débito, PSE, Nequi y Daviplata. Ofrece integración simple y widget embebido que reduce los requisitos de PCI compliance.

**ePayco**: Otra pasarela colombiana con soporte para múltiples métodos de pago locales y panel de administración en español.

**Stripe**: Como alternativa global, Stripe ofrece soporte para tarjetas internacionales y métodos de pago locales. Es la opción recomendada si el sistema busca attracting clientes extranjeros o si se requiere soporte para metod de pago no disponibles en pasarelas colombianas.

Se recomienda implementar una capa de abstracción de pasarela de pago en el backend para permitir conmutación entre proveedores según disponibilidad, costos o preferencias del cliente.

### 3.3.8 Almacenamiento de Videos e Imágenes

Para grabaciones de video de CCTV y evidencias fotográficas (capturas de placas en entrada/salida) se recomienda **Amazon S3** o almacenamiento compatible (MinIO para despliegues on-premise). Los videos se almacenan en formato MP4 con códec H.264 para optimizar espacio. La configuración del ciclo de vida mueve automáticamente videos antiguos a storage classes de menor costo (S3 Infrequent Access, S3 Glacier).

### 3.3.9 Monitoreo y Observabilidad

Se recomienda la pila **Grafana + Prometheus** como solución de monitoreo open source:

- **Prometheus** collecte métricas de todos los servicios (uso de CPU, memoria, latencia de solicitudes, errores) mediante endpoints de métricas exportadas por cada componente.
- **Grafana** proporciona dashboards visuales para monitoreo en tiempo real, alertas configurables y exploración de datos.
- **Loki** o **Elasticsearch** para agregación de logs distribuidos.
- **Jaeger** o **Zipkin** para trazabilidad distribuida de solicitudes entre servicios.

Como alternativa enterprise, **Datadog** ofrece una solución integrada de APM (Application Performance Monitoring), log management y monitoreo de infraestructura con menor esfuerzo de configuración pero a un costo recurrente significativo.

---

## 3.4 Seguridad y Autenticación

### 3.4.1 Autenticación

El sistema de autenticación se fundamenta en **JSON Web Tokens (JWT)** con un modelo de acceso y refresh tokens. Cuando un usuario inicia sesión, el sistema genera un access token con vigencia corta (típicamente 15 minutos) y un refresh token con vigencia más larga (típicamente 7 días). El access token se incluye en el encabezado Authorization de cada solicitud API. Cuando expira, el cliente lo intercambia por uno nuevo utilizando el refresh token.

Para el flujo de **login social** se implementa **OAuth2** con los proveedores más comunes (Google, Apple). El flujo sigue el estándar Authorization Code con PKCE para seguridad reforzada. Esto permite que los usuarios se autentiquen con sus cuentas existentes sin necesidad de crear credenciales nuevas.

Adicionalmente, se soporta **autenticación multifactor (MFA)** mediante códigos TOTP (Time-based One-Time Password) generados por aplicaciones como Google Authenticator o Authy. El MFA es obligatorio para usuarios con roles de administrador y operador, y opcional pero incentivado para clientes frecuentes.

### 3.4.2 Autorización: RBAC

El control de acceso basado en roles (RBAC) define los siguientes roles prédéfinidos en el sistema:

**Superadmin**: Acceso total a todas las funcionalidades del sistema, incluyendo gestión de clientes enterprise, configuración global, acceso a reportes consolidados de múltiples sedes y gestión de usuarios administradores. Este rol se asigna al equipo de soporte y operaciones del proveedor de la plataforma.

**Admin de Sede**: Control total sobre una o más sedes específicas. Puede configurar zonas, espacios, tarifas, talanqueras y horarios. Gestiona operadores y cobradores de sus sedes. Accede a reportes financieros y operativos de sus sedes asignadas. No puede acceder a datos de otras sedes.

**Operador**: Acceso a funcionalidades operativas del día a día: apertura y cierre de sesiones, atención de excepciones, consulta de espacios, generación de reportes operativos básicos. No tiene acceso a configuración de tarifas ni a reportes financieros detallados.

**Cobrador**: Rol especializado para el personal de cobro. Permite consultar saldos pendientes, procesar pagos y generar recibos. No tiene acceso a funciones de configuración del sistema.

**Cliente**: Acceso a su información personal, historial de entradas y salidas, vehículos registrados, métodos de pago, y funcionalidades de auto-gestión desde la aplicación móvil.

### 3.4.3 Cifrado

**Datos en tránsito**: Toda comunicación entre clientes y servidores está cifrada mediante **TLS 1.3**. Se prohíben explícitamente versiones anteriores de TLS y algoritmos criptográficos débiles. Los certificados se gestionan a través de una PKI interna o Let's Encrypt para entornos de producción.

**Datos en reposo**: La información sensible almacenada en bases de datos (datos personales de clientes, información financiera) se cifra utilizando **AES-256**. PostgreSQL proporciona cifrado a nivel de tablas o columnas utilizando pgcrypto. Los backups de bases de datos también se cifran antes de ser almacenados en destinos de respaldo.

### 3.4.4 Auditoría

Todas las acciones sensibles realizadas dentro del sistema son registradas en un log de auditoría inmutable. Las acciones auditadas incluyen pero no se limitan a:

- Inicio y cierre de sesión de usuarios (con dirección IP y dispositivo).
- Apertura manual de talanqueras (con identificación del operador y justificación).
- Ajustes de tarifas y planes tarifarios.
- Modificaciones en la configuración de espacios y zonas.
- Procesamiento de pagos y reembolsos.
- Creación, modificación y eliminación de usuarios y sus roles.
- Acceso a datos sensibles de clientes (con marco legal apropiado).

Los logs de auditoría se almacenan en un repositorio separado con acceso de solo lectura para el equipo de seguridad, y se retienen por un período mínimo de 5 años según requisitos regulatorios.

### 3.4.5 Rate Limiting y Protección DDoS

Se implementan múltiples capas de protección contra ataques de denegación de servicio y abuso de APIs:

**Rate limiting a nivel de API Gateway**: Cada endpoint tiene límites de solicitudes por minuto según su naturaleza. Los endpoints públicos de consulta de disponibilidad tienen límites generosos, mientras que endpoints sensibles como login tienen límites estrictos.

**Protección DDoS de capa 7**: Se utiliza un WAF (Web Application Firewall) como AWS WAF, Cloudflare o equivalente para detectar y bloquear patrones de ataque comunes (SQL injection, XSS, enumeration attacks).

**Rate limiting a nivel de aplicación**: Implementación adicional de rate limiting en el código de la API para protección granular contra abuse.

### 3.4.6 Pentesting y Bug Bounty

Se establece un programa de **pentesting recurrente** con una firma de seguridad externa calificada. Las pruebas incluyen análisis estático y dinámico de código, pruebas de penetración de infraestructura y aplicaciones, y revisión de configuración de seguridad. Los resultados se documentan y priorizan en el backlog de seguridad.

Complementariamente, se evalúa la implementación de un **programa de bug bounty** que invite a investigadores de seguridad a reportar vulnerabilidades a cambio de compensaciones económicas. Esto proporciona una evaluación de seguridad continua más allá de las pruebas puntuales.

### 3.4.7 Compliance y Regulación de Datos

El sistema cumple con la **Ley 1581 de 2012** de protección de datos personales de Colombia y su decreto reglamentario 1377 de 2013. Esto implica:

- Obtención de autorización explícita de los titulares de datos para su tratamiento.
- Implementación de un registro de actividades de tratamiento de datos.
- Designación de un oficial de datos personales o encargado del tratamiento.
- Establecimiento de procedimientos para el ejercicio de derechos de los titulares (acceso, corrección, supresión, revocatoria).
- Contratos de encargado de tratamiento con todos los proveedores que procesan datos personales.

Adicionalmente, el sistema está diseñado para facilitar el cumplimiento de normativas de PCI DSS si se procesan tarjetas de crédito directamente, aunque se recomienda delegar el procesamiento de tarjetas a pasarelas de pago certificadas para minimizar el alcance de PCI.

---

## 3.5 Integraciones Externas

### 3.5.1 Pasarelas de Pago

La plataforma se integra con las principales pasarelas de pago del mercado colombiano:

**Wompi**: Ofrece procesamiento de pagos con tarjeta de crédito y débito, transferencias bancarias vía PSE, y wallets digitales como Nequi y Daviplata. Su widget embebido minimiza los requisitos de integración PCI para el comercio. Wompi proporciona APIs RESTful bien documentadas y un ambiente de pruebas completo.

**ePayco**: Similar a Wompi en cobertura de métodos de pago locales, con panel de administración en español y soporte técnico local. Su modelo de comisiones es competitivo para el mercado colombiano.

**Stripe**: Como pasarela global, Stripe se integra para procesar pagos con tarjetas internacionales y métodos de pago que no estén disponibles en las pasarelas locales. Es particularmente útil para parqueaderos en zonas turísticas o con alta presencia de visitantes extranjeros.

Todas las integraciones siguen el patrón de **adaptador** del Gang of Four, donde una interfaz común abstrae las diferencias entre proveedores. Esto permite conmutar entre pasarelas sin modificar la lógica de negocio, y habilita configuraciones multi-pasarela donde el sistema selecciona automáticamente la pasarela disponible según el método de pago del cliente.

### 3.5.2 APIs de Reconocimiento de Placas (ANPR)

**Plate Recognizer**: Servicio de reconocimiento de placas basado en machine learning que ofrece alta precisión para vehículos latinoamericanos. Proporciona APIs para detección de placas, lectura de caracteres y reconocimiento de color del vehículo. Ofrece modelos especializados para placas colombianas.

**OpenALPR**: Alternativa establecida con fuerte presencia en el mercado de seguridad y estacionamientos. Proporciona Cloud API para reconocimiento en la nube y Agent para procesamiento on-premise cuando se requiere baja latencia o privacidad de datos.

La integración con estas APIs permite enviar frames capturados por las cámaras de vigilancia y recibir en respuesta la placa detectada con su nivel de confianza. El sistema correlaciona estas lecturas con los registros de entrada y salida para verificación automática.

### 3.5.3 Servicios de Notificación

**Firebase Cloud Messaging (FCM)**: Se utiliza para push notifications a aplicaciones móviles. Cuando un cliente registra un vehículo y este entra o sale del parqueadero, el sistema envía una notificación al dispositivo del cliente con los detalles del evento. FCM permite segmentación de usuarios, personalización de mensajes y analytics de entrega.

**Twilio / Vonage**: Para notificaciones por SMS se integran estos proveedores. Los casos de uso incluyen códigos de verificación de teléfono, alertas de pago recibido, y recordatorios de salida. Los costos de SMS se minimizan utilizando push notifications como canal primario y SMS como fallback.

### 3.5.4 Integración con Sistemas de CCTV y NVR

Las cámaras de vigilancia del parqueadero se integran mediante protocolos estándar de la industria:

**RTSP (Real Time Streaming Protocol)**: Protocolo estándar para la transmisión de video en tiempo real desde cámaras IP. El sistema puede solicitar streams de video para visualización en vivo desde el dashboard de operaciones.

**ONVIF (Open Network Video Interface Forum)**: Estándar de interoperabilidad para dispositivos de video en red. Permite el descubrimiento automático de cámaras compatibles, control de PTZ (pan-tilt-zoom) cuando está disponible, y gestión centralizada de configuración.

La integración con NVRs (Network Video Recorders) permite acceder a grabaciones archivadas para revisión de incidentes o como evidencia en disputas. Se implementa esta integración siguiendo las APIs específicas del fabricante del NVR.

### 3.5.5 Aplicaciones de Mapas

Para mostrar la disponibilidad de espacios en tiempo real en aplicaciones externas o en el widget de reserva, se integra con **Google Maps** y **Waze**:

**Google Maps Platform**: Permite overlay de la información de disponibilidad del parqueadero sobre el mapa, incluyendo número de espacios disponibles por zona, tarifas actuales y tiempo de espera estimado. La API de Places permite mostrar el parqueadero en búsquedas locales.

**Waze**: A través de la plataforma de партнерства de Waze, los parqueaderos pueden transmitir disponibilidad en tiempo real que se muestra a los conductores antes de decidir su ruta. Esto es particularmente valioso para atraer clientes que utilizan Waze como navegador principal.

### 3.5.6 API Pública para Terceros

Se diseña y documenta una **API pública** que permite a aplicaciones de terceros integrar funcionalidades de consulta y operación del parqueadero. Esta API sigue el estándar **OpenAPI 3.0** y está versionada para mantener compatibilidad hacia atrás.

Los casos de uso previstos incluyen:

- Integración con aplicaciones de delivery o mensajería para validación de acceso de vehículos autorizados.
- Integración con sistemas de gestión de flotas empresariales para control de uso de vehículos.
- Integración con aplicaciones de reservas de parqueadero de terceros.
- Alimentadores de datos para plataformas de smart city o aplicaciones de movilidad urbana.

La API pública implementa autenticación mediante API keys y OAuth2, rate limiting específico para cada plan de uso, y logging detallado de todas las solicitudes para facturación y auditoría.

---

*Documento elaborado con fines de propuesta comercial. Las tecnologías y arquitecturas describedas pueden variar según los requisitos específicos del cliente y las condiciones del mercado.*
