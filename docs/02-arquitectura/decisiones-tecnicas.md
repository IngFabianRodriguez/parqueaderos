# Decisiones de Arquitectura (ADR)

---

**ADR-001: Arquitectura de microservicios en lugar de monolito**

**Estado**: Aceptado

**Contexto**: El sistema de gestión de parqueaderos ParkCore necesita escalar de manera independiente por módulo (facturación, ANPR, IoT, reservas) y permitir que equipos autónomos trabajen en cada dominio sin depender de un único repositorio monolítico. Se anticipa crecimiento en cantidad de sedes y volumen de transacciones simultáneas.

**Decisión**: Se adopta una arquitectura de microservicios donde cada dominio de negocio (autenticación, reservas, pagos, IoT, notificaciones) se despliega como un servicio independiente con su propia base de datos. Para el MVP, se contempla un enfoque de monolito modular como fallback: todos los módulos viven en un solo repositorio pero separados por paquetes/namespace, permitiendo migrar a microservicios sin reescribir lógica de negocio.

**Consecuencias**:
- **Positivas**: escalabilidad independiente por módulo, equipos autónomos, aislamiento de fallos entre servicios, tecnología heterogénea por dominio.
- **Negativas**: complejidad operacional mayor (orquestación, service discovery, red), mayor curva de aprendizaje en DevOps, necesidad de contratos API rigurosos entre servicios.

---

**ADR-002: FastAPI (Python) para APIs de negocio**

**Estado**: Aceptado

**Contexto**: Las APIs de negocio del parqueadero (consulta de espacios, registro de entrada/salida, facturación, integración con ANPR) requieren alto rendimiento en operaciones I/O concurrentes, tipado estático para mantenimiento a largo plazo y documentación automática para reducir la fricción entre equipos frontend y backend.

**Decisión**: Se selecciona FastAPI (Python 3.11+) como framework principal para todas las APIs de negocio. FastAPI ofrece rendimiento async comparable a Node.js/Golang, validación de tipos con Pydantic, generación automática de documentación OpenAPI 3.0 y compatibilidad con el ecosistema de machine learning (útil para futuras integraciones de analítica).

**Consecuencias**:
- **Positivas**: documentación automática, rendimiento async, tipado estático con Pydantic, rápida curva de aprendizaje, gran ecosistema de librerías Python.
- **Negativas**: menor rendimiento en cómputo puro comparado con Go/Rust, GIL limita paralelismo real en operaciones CPU-bound, ecosistema menos maduro para microservicios que Node.js.

---

**ADR-003: PostgreSQL como base de datos principal**

**Estado**: Aceptado

**Contexto**: ParkCore necesita una base de datos transaccional que garantice ACID para el registro de entradas, salidas y pagos, que soporte datos semiestructurados (metadatos de vehículos, configuración de sedes en JSON) y que permita manejar series de tiempo generadas por los sensores IoT.

**Decisión**: Se elige PostgreSQL 16 como motor de base de datos principal. Se utiliza la extensión TimescaleDB para el almacenamiento optimizado de series de tiempo (eventos IoT, métricas de ocupación). JSONB se emplea para atributos semiestructurados que varían entre sedes o clientes enterprise.

**Consecuencias**:
- **Positivas**: ACID garantizado, JSONB para semiestructurado, TimescaleDB para series de tiempo, amplia comunidad, herramientas de monitoreo maduras (pg_stat_statements, EXPLAIN ANALYZE).
- **Negativas**: escalabilidad horizontal más compleja que bases NoSQL, require tuning para cargas altas en writes concurrentes, replicación multi-región requiere configuración avanzada.

---

**ADR-004: MQTT como protocolo IoT para dispositivos en sede**

**Estado**: Aceptado

**Contexto**: Los dispositivos IoT en cada sede (talanqueras, sensores de ocupación por espacio, cámaras ANPR, paneles de disponibilidad) requieren un protocolo de comunicación ligero, con patrón pub/sub, bajo consumo de energía y tolerancia a conexiones intermitentes.

**Decisión**: Se adopta MQTT 5.0 como protocolo estándar para la comunicación con dispositivos IoT en sede. Los dispositivos publican eventos (entrada detectada, espacio ocupado, talanquera abierta) y el broker MQTT retransmite a los suscriptores correspondientes (servicio de registro, servicio de facturación). Se utiliza un broker Mosquitto con clustering para alta disponibilidad.

**Consecuencias**:
- **Positivas**: protocolo ligero ideal para IoT, patrón pub/sub desacopla productores y consumidores, QoS configurable, bajo ancho de banda.
- **Negativas**: no es HTTP, requiere integrar un bridge MQTT→HTTP para algunos servicios, gestión de QoS añade complejidad, broker MQTT es un punto adicional de operación.

---

**ADR-005: Redis para caché de sesiones y disponibilidad en tiempo real**

**Estado**: Aceptado

**Contexto**: El sistema requiere acceso en tiempo real a la disponibilidad de espacios por sede, caché de sesiones de usuario para evitar re-autenticaciones en cada request, y un store compartido para contadores atómicos (ocupación actual, tickets activos) que requieren latencia sub-milisegundo.

**Decisión**: Se despliega Redis 7 en modo cluster para caché de sesiones (JWT refresh tokens invalidated blacklist), caché de datos de disponibilidad de espacios, y contadores atómicos para ocupación en tiempo real. Redis Sentinel gestiona la conmutación por error automática.

**Consecuencias**:
- **Positivas**: latencia sub-milisegundo, estructuras de datos ricas (sorted sets, hashes, streams), expiry automático de sesiones, alto rendimiento en lecturas.
- **Negativas**: persistencia opcional (RDB/AOF) puede perder datos en fallos, requiere estrategia de caché invalidation, máximo 256MB por valor, no es fuente primaria de verdad.

---

**ADR-006: ANPR via API externa (Plate Recognizer) en lugar de modelo propio**

**Estado**: Aceptado

**Contexto**: El reconocimiento automático de placas (ANPR) es un componente crítico para la entrada/salida automática de vehículos. Entrenar y mantener un modelo propio de computer vision requiere expertise especializado, GPU dedicada y datos de entrenamiento extensivos; el time-to-market es prioritario.

**Decisión**: Se integra la API de Plate Recognizer (oalternativamente OpenALPR) como servicio externo de ANPR. Cada cámara de sede envía la imagen al servicio API y obtiene la placa reconocida con confianza. Se implementa lógica de fallback: si la confianza es menor al 90%, se marca para revisión manual por un operador.

**Consecuencias**:
- **Positivas**: precisión >98% lista para producción, time-to-market acelerado, sin costo de GPU ni entrenamiento, actualizaciones del modelo incluidas por el proveedor.
- **Negativas**: dependencia de proveedor externo, costo por llamada API, latencia adicional por llamada de red, datos de placas viajan fuera del infrastructure (requiere evaluación de seguridad/Ley 1581).

---

**ADR-007: JWT para autenticación de APIs**

**Estado**: Aceptado

**Contexto**: Los microservicios de ParkCore requieren un mecanismo de autenticación stateless que pueda validarse en cada servicio sin consultar una base de datos centralizada en cada request, compatible con la arquitectura distribuida y múltiples clientes (app móvil, app web, integración第三方).

**Decisión**: Se implementa autenticación con JWT (JSON Web Tokens). El servicio de autenticación emite access tokens firmados con RS256 (15 minutos de vida) y refresh tokens rotativos (7 días). Los refresh tokens se almacenan en Redis para poder revocarlos explícitamente. Cada microservicio valida el JWT usando la clave pública del servicio de autenticación.

**Consecuencias**:
- **Positivas**: estándar industry, stateless, fácil de validar en cualquier lenguaje, granularidad de claims, múltiples clientes soportados.
- **Negativas**: tokens no pueden revocarse instantly (short expiry mitiga), tamaño del token en cada request, complejidad en refresh token rotation, almacenamiento en cliente requiere seguridad (XSS).

---

**ADR-008: Docker + Kubernetes como plataforma de despliegue**

**Estado**: Aceptado

**Contexto**: ParkCore se desplegará en múltiples sedes con infraestructura heterogénea (desde VPS para early adopters hasta máquinas bare-metal en sedes enterprise). Se requiere portabilidad entre entornos, orquestación de contenedores, auto-scaling según demanda y despliegues zero-downtime.

**Decisión**: Cada microservicio se empaqueta en contenedores Docker con imágenes basadas en distroless/python-slim. Kubernetes (K3s para edge/on-premise, GKE/EKS para cloud) orquesta los contenedores, gestiona ingress, volumes, secrets y políticas de red. Helm charts versionados controlan el despliegue. ArgoCD o Flux se usa para GitOps.

**Consecuencias**:
- **Positivas**: portabilidad entre cloud y on-premise, auto-scaling, rolling updates zero-downtime, isolation entre servicios, secretos cifrados en etcd.
- **Negativas**: curva de aprendizaje pronunciada, overhead operacional significativo, debugging distribuido más complejo, costo de cluster management, требует dedicated DevOps engineer.
