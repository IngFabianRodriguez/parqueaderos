# Visión General del Proyecto

## ¿Qué es ParkCore?

**ParkCore** es una plataforma centralizada de gestión para redes de parqueaderos que integra múltiples tecnologías y módulos funcionales en un ecosistema unificado. Diseñada desde cero para operadores profesionales y cadenas de estacionamientos, la plataforma ofrece capacidades de monitoreo en tiempo real, automatización del control de acceso vehicular mediante lectura automática de placas (ANPR), gestión integral de pagos y cobros, y herramientas de inteligencia de negocio (BI) que permiten tomar decisiones basadas en datos.

En su esencia, ParkCore funciona como el "cerebro" operativo de un parqueadero o de una red de ellos: conecta cámaras de vigilancia con software de reconocimiento de matrículas, integra barreras físicas (talanqueras) controladas por relés IoT, procesa transacciones financieras a través de pasarelas de pago, y presenta toda esta información en dashboards visuales tanto para operadores en sala como para gerentes remotos.

La plataforma no es simplemente un sistema de registro de vehículos; es una solución end-to-end que abarca desde el momento en que un vehículo cruza la entrada del parqueadero —con su placa leída automáticamente por cámaras ANPR— hasta la generación de reportes consolidados de ocupación, facturación y comportamiento del cliente.

---

## Para quién es ParkCore

### Operadores independientes de parqueaderos

El propietario o administrador de un parqueadero independiente que actualmente maneja sus operaciones con talonarios, ticketeras manuales o sistemas básicos de reloj discretario encuentra en ParkCore una forma de profesionalizar su operación sin necesidad de grandes inversiones en infraestructura de TI. La plataforma permite tener visibilidad completa de la ocupación del parqueadero, automatizar la cobro por tiempo y generar reportes que antes solo eran posibles con sistemas costosos de terceros.

### Cadenas de estacionamientos

Las empresas que administran múltiples sedes de parqueaderos necesitan visibilidad consolidada. ParkCore permite operar cada sede de forma independiente pero ver el desempeño global desde un único dashboard. Esto es especialmente valioso para cadenas que buscan estandarizar procesos, aplicar políticas de precios consistentes y detectar oportunidades de optimización across-sedes. La arquitectura multi-sede soporta desde dos hasta cientos de ubicaciones geográficas.

### Empresas con flotas propias

Compañías que mantienen flotas vehiculares propias —empresas de distribución, transporte escolar, servicio de mensajería, utility companies— enfrentan el desafío de controlar quién usa qué vehículo, durante cuánto tiempo y bajo qué condiciones. ParkCore ofrece un módulo B2B que permite a estas empresas gestionar el acceso de sus vehículos a instalaciones propias o a parqueaderos de terceros, con facturación consolidada y reportes de uso por vehículo, conductor o departamento.

---

## Qué resuelve ParkCore

### Problema 1: Falta de visibilidad operativa

En parqueaderos tradicionales, el operador en turno no sabe cuántos espacios están disponibles sin salir a verificar físicamente. ParkCore resuelve esto con un tablero de disponibilidad en tiempo real por sede, actualizado segundo a segundo, mostrando exactamente cuántos espacios hay libres, cuántos ocupados y la tasa de ocupación histórica.

### Problema 2: Errores y fraude en la lectura de placas

La digitación manual de placas es propensa a errores humanos: un número mal escrito, una placa incompleta, un vehículo que se "cola" sin pagar. El módulo ANPR (Automatic Number Plate Recognition) de ParkCore lee automáticamente la matrícula al ingreso y la compara con el registro al egreso, eliminando ambigüedades y reduciendo el fraude por placas mal digitadas.

### Problema 3: Gestión fragmentada de pagos y cobros

Sin un CRM integrado, cada parqueadero lleva sus propios registros de clientes frecuentes, prepagos, exonerados y deudores de forma manual o en hojas de cálculo. ParkCore centraliza toda la información de pagos y clientes en un solo lugar, permitiendo históricamente saber cuándo un vehículo entró, cuánto tiempo permaneció, cuánto pagó y si tiene saldos pendientes.

### Problema 4: Control de acceso físico sin integración

Las talanqueras y barreras de acceso tradicionalmente funcionan como sistemas independientes conectados al sistema del parqueadero a través de integraciones complicadas o simplemente operan de forma aislada. ParkCore las integra nativamente a través de módulos IoT basados en el protocolo MQTT: cuando el sistema valida que el pago está en orden, la talanquera se levanta automáticamente. Si hay un conflicto (vehículo no registrado, placa no coincide, deuda pendiente), la barrera permanece cerrada y se genera una alerta.

### Problema 5: Ausencia de inteligencia de negocio

Los parqueaderos que sobreviven sin datos confiables toma decisiones de precio, capacidad y operación basándose en intuición. ParkCore provee dashboards BI que muestran ocupación por hora/día/mes, ingresos promedio por espacio, peak hours, y comparativas entre sedes para operadores multi-ubicación. Esta información es la base para decisiones de pricing dinámico, expansión de capacidad o renegociación de contratos con clientes corporativos.

---

## Arquitectura modular de ParkCore

ParkCore se compone de los siguientes módulos funcionales, cada uno con responsabilidades bien definidas y diseñado para operar de forma independiente o integrada con los demás:

| Módulo | Descripción |
|---|---|
| **ANPR** | Recognition engine that captures license plates at entry/exit points using camera feeds. Supports multiple camera configurations per lane, multiple lanes per site. |
| **Disponibilidad en tiempo real** | Motor de ocupación que mantiene actualizada la disponibilidad de espacios por sede, con lógica de conteo de entrada/salida y capacidad configurable. |
| **CRM de pagos y cobros** | Gestión de clientes, tarifarios, descuentos, exoneraciones, prepagos y facturación. Historial completo de movimientos por vehículo y por cliente. |
| **Control de talanquera IoT** | Actor IoT que se comunica con relés y barreras físicas a través de MQTT. Abre/cierra según reglas de negocio predefinidas. Soporta fallback manual. |
| **Dashboard BI** | Interfaz visual con métricas clave, gráficos de tendencia, reportes exportables y alertas configurables. Orientado a operadores y gerentes. |
| **App Operador** | Aplicación móvil para que el personal en sitio gestione excepciones, valide documentos y atienda incidentes sin necesidad de estar en un terminal fijo. |
| **App Cliente** | Aplicación para usuarios finales que permite consulta de saldo, historial de الاستخدام، pagos anticipados y reservas (según módulo de reservas). |

---

## Stack tecnológico tentativo

La siguiente tabla muestra las tecnologías candidatas para cada capa del sistema. La selección final dependerá de los resultados de la fase de prototipado y de las capacidades del equipo de desarrollo:

| Capa | Tecnología | Rol |
|---|---|---|
| **Backend** | Python / FastAPI | API REST/GraphQL, lógica de negocio, procesamiento de eventos, middleware de integración con dispositivos IoT |
| **Frontend web** | React o Angular | Dashboard BI, consola de administración, portal de reportes |
| **Base de datos principal** | PostgreSQL | Almacenamiento transaccional: vehículos, registros, tarifas, clientes, transacciones |
| **Cache y real-time** | Redis | Disponibilidad en tiempo real, pub/sub para eventos de talanquera, sesión de usuarios |
| **Broker IoT** | MQTT (Mosquitto o EMQX) | Comunicación con relés de talanquera, cámaras, sensores de occupancy |
| **ANPR** | Integración con motor ANPR de terceros (OpenALPR, Plate Recognizer, o solución custom con OpenCV/TensorFlow) | Reconocimiento de matrículas desde flujo de video |
| **Pasarela de pagos** | API dePSD2 o proveedor local (Mercado Pago, PayU, Stripe, dLocal) | Procesamiento de pagos electrónicos |
| **Contenedores** | Docker + Docker Compose (desarrollo), Kubernetes (producción) | Despliegue, escalabilidad y orquestación |
| **CI/CD** | GitHub Actions o GitLab CI | Integración y entrega continua |

---

## Estado del proyecto

ParkCore se encuentra actualmente en **desarrollo activo**, específicamente en la **fase MVP (Minimum Viable Product)**. Esta fase tiene una duración estimada de tres meses (Mes 1 a Mes 3) y como objetivo principal es validar los supuestos centrales del negocio con una sede piloto funcional, un flujo completo de ingreso-egreso de vehículos y un conjunto limitado de integraciones.

Durante el MVP se espera demostrar:
- Que la lectura ANPR funciona con precisión aceptable (>95%) en condiciones de operación reales
- Que la apertura automática de talanquera responde en menos de 2 segundos desde la validación
- Que un operador puede gestionar la sede sin necesidad de capacitación extensa
- Que la información de ocupación y transacciones se refleja en el dashboard sin demoras perceptibles

Una vez completado el MVP, el proyecto avanzará a la Fase 1 (V1) donde se incorporarán multi-sede, dashboard consolidado, app operador y la primera integración con una pasarela de pago real.

---

## Cómo navegar la documentación

La documentación del proyecto está organizada en carpetas temáticas dentro del directorio `docs/`. A continuación se presenta la tabla de contenidos con enlaces relativos a cada sección:

| Sección | Descripción |
|---|---|
| [00-general/](./00-general/) | Documentos generales del proyecto: visión, roadmap, changelog, licencia |
| [01-resumen-ejecutivo/](./01-resumen-ejecutivo/) | Resumen ejecutivo del proyecto y propuesta de valor |
| [02-modulos-funcionales/](./02-modulos-funcionales/) | Descripción detallada de cada módulo funcional |
| [03-arquitectura-tecnica/](./03-arquitectura-tecnica/) | Arquitectura técnica, diagramas de sistema y decisiones de diseño |
| [04-monetizacion-roi/](./04-monetizacion-roi/) | Modelo de monetización, proyecciones financieras y ROI |
| [05-riesgos-compliance/](./05-riesgos-compliance/) | Análisis de riesgos, consideraciones legales y compliance |

**Convenciones usadas en esta documentación:**

- Los documentos escritos en español usan puntuación y formato según la Real Academia Española
- Los diagramas técnicos usan notación estándar UML 2.0
- El versionado sigue SemVer (Semantic Versioning): `MAJOR.MINOR.PATCH`
- Los nombres de archivos en minúsculas con guiones medios: `nombre-archivo.md`
- Los commits siguen Conventional Commits: `tipo(alcance): descripción`

---

## Licencia y contacto

Este proyecto y su documentación son propiedad del equipo de desarrollo de ParkCore. Para consultas, colaboraciones o reporte de errores, consultar la documentación de contribución o contactar al equipo a través de los canales internos del proyecto.
