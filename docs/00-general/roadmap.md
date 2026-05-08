# Roadmap del Proyecto

## Introducción

Este documento establece la hoja de ruta planeada para el desarrollo de **ParkCore** desde su concepción hasta su escalamiento a nivel multi-ciudad. El roadmap está dividido en cuatro fases principales que abarcan aproximadamente 18 meses de desarrollo, con objetivos claros, entregables definidos y estados de avance trazables.

Es importante señalar que las fechas estimadas son targets de planificación sujetos a ajustes basados en retroalimentación del MVP, disponibilidad del equipo y factores externos como regulaciones locales, integración con proveedores de pago o disponibilidad de hardware ANPR en el mercado regional.

Cada fase construye sobre los logros de la anterior, lo que significa que al finalizar la Fase 1 tendremos un sistema funcional para múltiples sedes, y la Fase 2 añadirá capacidades B2B y BI avanzadas sobre esa base.

---

## Resumen de fases

| Fase | Descripción | Estado | Fecha estimada |
|------|-------------|--------|-----------------|
| **Fase 0** | MVP — Una sede piloto con funcionalidad core | ⏳ En desarrollo | Mes 1–3 |
| **Fase 1** | V1 — Multi-sede, dashboard consolidado, app operador | 📋 Planeado | Mes 4–6 |
| **Fase 2** | V2 — Módulo B2B flotas, facturación electrónica, BI avanzado, app cliente, APIs abiertas | 📋 Planeado | Mes 7–10 |
| **Fase 3** | Escalamiento — Multi-ciudad, modelo license/franchise, ML predicción demanda, dynamic pricing | 📋 Planeado | Mes 11–18 |

---

## Fase 0: MVP — Minimum Viable Product

**Período estimado:** Mes 1–3  
**Estado actual:** ⏳ En desarrollo  
**Sede de pruebas:** Una sede piloto seleccionada por el equipo de operaciones

### Descripción

La Fase 0 tiene como objetivo principal validar los supuestos centrales del negocio y la viabilidad técnica de ParkCore en condiciones reales de operación. Esta fase no busca un producto completo ni una experiencia de usuario pulida; busca demostrar que el concepto funciona en campo y que la tecnología seleccionada cumple con los requisitos mínimos de confiabilidad.

Durante esta fase se implementará una instalación completa en una sede piloto que servirá simultáneamente como ambiente de desarrollo/pruebas y como demostración comercial para potenciales inversores o primeros clientes. La sede piloto será operada por personal del equipo con soporte directo del equipo de desarrollo.

### Objetivos específicos

- **Validar integración ANPR en campo:** Verificar que la lectura automática de matrículas funciona con una precisión aceptable (target >95%) bajo condiciones reales de iluminación, velocidad de vehículos y calidad de placas variadas (diferentes países, estados, formatos).
- **Validar latencia de apertura de talanquera:** Confirmar que el tiempo total desde la lectura de placa hasta la apertura de la barrera es menor a 2 segundos en el 95% de los casos.
- **Validar el flujo transaccional básico:** Comprobar que el sistema registra correctamente un ingreso, calcula el tiempo de permanencia, genera el cargo correcto y procesa el pago.
- **Obtener feedback del operador:** Documentar la experiencia del primer usuario operativo real para informar el diseño de la app operador y la interfaz del dashboard.
- **Generar datos reales para planificación:** Recopilar métricas de ocupación, patrones de ingreso/egreso y datos de pago que servirán para calibrar las proyecciones financieras de fases posteriores.

### Alcance funcional

- Una (1) sede operativa con dos puntos de control (entrada y salida)
- Hasta dos (2) carriles por punto de control
- Lectura ANPR en cada carril con una cámara dedicada
- Relay de talanquera controlado por el sistema
- Registro manual de transacciones (el operador inicia el proceso desde una pantalla en el punto de control)
- Dashboard de disponibilidad en tiempo real (pocos espacios, ocupación actual, último vehículo registrado)
- Base de datos local con PostgreSQL (no se contempla redundancia en esta fase)
- Sin integración con pasarela de pago — pagos en efectivo únicamente
- Sin app móvil; toda la operación desde terminal web fija

### Entregables de la Fase 0

1. **Documento de especificación técnica (MVP)** — Descripción detallada de cada módulo y sus límites funcionales para la fase piloto.
2. **Infraestructura de sede piloto** — Diagrama de cableado, posicionamiento de cámaras y configuración de red.
3. **API backend funcional** — Endpoints para registro de ingreso/egreso, consulta de disponibilidad, gestión básica de tarifas.
4. **Dashboard de monitoreo** — Interfaz web para el operador en sitio con vista de ocupación en tiempo real.
5. **Documento de lecciones aprendidas** — Reporte interno con findings, riesgos materializados y ajustes recomendados para la Fase 1.
6. **Video demo** — Grabación corta (<3 min) del flujo completo funcionando en la sede piloto para uso comercial.

---

## Fase 1: V1 — Primera versión operativa

**Período estimado:** Mes 4–6  
**Estado actual:** 📋 Planeado  
**Alcance geográfico:** Hasta 5 sedes

### Descripción

La Fase 1 marca la transición de "prueba de concepto" a "producto utilizable". Una vez validado el MVP, el enfoque cambia de validar que la tecnología funciona a asegurar que el producto es usable por personal no técnico, escalable a múltiples ubicaciones y preparado para integrar métodos de pago electrónicos.

Durante esta fase se incorporarán las primeras funcionalidades que van más allá del control de acceso básico: un dashboard consolidado que permite ver múltiples sedes simultáneamente, una aplicación móvil para que los operadores en sitio atiendan incidentes y excepciones sin estar atados a un terminal fijo, y la primera integración real con una pasarela de pago.

### Objetivos específicos

- **Multi-sede:** Extender la arquitectura para soportar hasta 5 sedes simultáneas, cada una con su propia configuración de carriles, cámaras, tarifarios y operadores.
- **Dashboard consolidado:** Crear una vista única que agregue métricas de todas las sedes activas: ocupación total, ingresos del día, transacciones procesadas, alertas activas.
- **App Operador:** Desarrollar una aplicación móvil nativa (iOS y Android) que permita al personal en sitio realizar operaciones comunes: apertura manual de talanquera, consulta de historial de vehículo, gestión de exoneraciones, atención de excepciones (vehículo sin placa, falla de cámara, pago fallido).
- **Integración con pasarela de pago:** Conectar con al menos una pasarela de pago regional (ej. Mercado Pago, PayU, Stripe o equivalente local) para procesar pagos electrónicos automáticos al egreso.
- **CRM básico:** Registrar clientes frecuentes con datos de contacto, vehículos asociados y preferencias de pago. Soporte para exoneraciones y descuentos configurables.
- **Notificaciones básicas por email:** Alertas al cliente cuando su vehículo ingresa/egresa, recepción de comprobante de pago.

### Alcance funcional

- Hasta cinco (5) sedes operativas, cada una con configuración independiente
- Múltiples puntos de control por sede (entrada, salida, opcionalmente piso/nivel)
- App operador (iOS/Android) para gestión en sitio
- Dashboard web multi-sede con métricas consolidadas
- Integración con una (1) pasarela de pago
- CRM básico: registro de clientes, asociación de vehículos, historial de transacciones
- Sistema de notificaciones por email (eventos de ingreso/egreso, comprobantes)
- Gestión de tarifarios por sede y por tipo de cliente (horario, mensual, exonerado)
- Reportes básicos exportables (CSV/PDF): resumen diario, resumen mensual, libro de ventas

### Entregables de la Fase 1

1. **Sistema multi-sede desplegado** — Cinco sedes operando simultáneamente sobre la misma plataforma.
2. **App Operador v1.0** — Publicada en App Store y Google Play, con funcionalidades de: apertura manual, consulta vehicular, gestión de excepciones.
3. **Dashboard consolidado** — Vista gerencial multi-sede con métricas clave y capacidad de drill-down por sede.
4. **Integración de pago funcional** — Pagos electrónicos procesándose en al menos una sede piloto.
5. **CRM funcional** — Registro y consulta de clientes frecuentes, aplicación automática de tarifas preferenciales.
6. **Documentación de usuario operador** — Manuales de operación para personal en sitio y administradores de sede.

---

## Fase 2: V2 — Plataforma completa con ecosistema B2B

**Período estimado:** Mes 7–10  
**Estado actual:** 📋 Planeado  
**Alcance geográfico:** Hasta 20 sedes, múltiples ciudades de un mismo país

### Descripción

La Fase 2 expande ParkCore de una herramienta de gestión operativa a una plataforma con ecosistema. El diferenciador principal de esta fase es la apertura hacia el segmento B2B: empresas con flotas de vehículos podrán gestionar el acceso de sus automotores a través de APIs públicas, con facturación consolidada y reportes de uso por departamento o proyecto.

Simultáneamente, se introducirá la app de cliente final para usuarios que usan parqueaderos ParkCore de forma frecuente, permitiéndoles consultar su saldo prepagado, recibir notificaciones de sus ingresos y egresos, y gestionar sus vehículos registrados. La facturación electrónica integrará al sistema tributario local, y el BI avanzado proporcionará herramientas analíticas que van más allá de dashboards estáticos.

### Objetivos específicos

- **Módulo B2B Flotas:** Permitir a empresas registrar sus flotas vehiculares, configurar políticas de acceso (horarios permitidos, espacios restringidos, conductoress autorizados), consultar uso en tiempo real y recibir facturación consolidada mensual.
- **Facturación electrónica:** Integración con la autoridad tributaria local para emitir comprobantes electrónicos (facturas, notas de crédito/débito) de forma automática en cada transacción o de forma consolidada para clientes B2B.
- **BI avanzado:** Dashboards interactivos con capacidad de filtering dinámico, comparativas período a período, proyecciones basadas en tendencias históricas y exportación de datos en múltiples formatos. Orientado a gerentes de operaciones y directors financieros.
- **App Cliente:** Aplicación para usuarios finales con las siguientes funcionalidades: registro de vehículos, consulta de saldo prepagado, historial de ingresos/egresos, configuración de notificaciones, carga de saldo.
- **APIs abiertas:** Documentación y publicación de APIs REST que permitan a clientes B2B integrar sus sistemas internos (ERP, RRHH, fleet management) con ParkCore. Endpoints para: consulta de saldo, registro de ingreso, consulta de consumo, descarga de reportes.
- **Notificaciones push:** Implementación de notificaciones push para ambas apps (operador y cliente) para eventos que requieren atención inmediata.

### Alcance funcional

- Hasta veinte (20) sedes operativas distribuidas en múltiples ciudades
- Módulo B2B con portal de administración de flotas dedicado para empresas
- Portal de autoservicio para clientes frecuentes (web y app)
- Facturación electrónica integrada con el sistema tributario local
- BI avanzado con reportes interactivos, alertas configurables y exportabilidad
- APIs abiertas documentadas con especificación OpenAPI (Swagger)
- Notificaciones push para eventos críticos (entrada/salida de vehículo, alertas de seguridad)
- Soporte para múltiples idiomas y monedas (preparación para expansión regional)
- Sistema de reservas básico (opcional, sujeto a definición): reserva de espacio por anticipado via app

### Entregables de la Fase 2

1. **Portal B2B funcional** — Empresas pueden darse de alta, registrar flotas, configurar políticas y consultar reportes.
2. **Facturación electrónica operativa** — Comprobantes electrónicos generándose y validándose con la autoridad tributaria.
3. **App Cliente v1.0** — Publicada en App Store y Google Play con funcionalidades de registro, consulta y prepago.
4. **BI avanzado desplegado** — Dashboard interactivo con todas las métricas clave y herramientas de análisis.
5. **Documentación de APIs** — Portal de desarrollador con referencia completa de endpoints, ejemplos de uso y sandbox.
6. **Manual de integración B2B** — Guía técnica para empresas que deseen integrarse con las APIs de ParkCore.

---

## Fase 3: Escalamiento — Plataforma madura y escalable

**Período estimado:** Mes 11–18  
**Estado actual:** 📋 Planeado  
**Alcance geográfico:** Multi-ciudad, modelo de licenciamiento y/o franchising

### Descripción

La Fase 3 representa la madurez del producto y su preparación para escalar a nivel nacional e internacional. En esta fase se introduce el modelo de licenciamiento que permite a terceros (operadores de parqueaderos independientes, cadenas regionales) adoptar la plataforma ParkCore bajo un esquema de licencia SaaS o franchise, manteniendo su marca pero operando sobre la infraestructura tecnológica de ParkCore.

El diferenciador técnico más significativo de esta fase es la incorporación de inteligencia artificial para predicción de demanda y pricing dinámico: el sistema utilizará modelos de machine learning entrenados con datos históricos de ocupación para predecir la demanda futura (por hora, día, evento) y sugerir o aplicar automáticamente tarifas que maximicen la ocupación y el ingreso.

### Objetivos específicos

- **Multi-ciudad / Multi-país:** Extender la operación a ciudades adicionales, con soporte para regulaciones locales, impuestos regionales y monedas múltiples.
- **Modelo de licenciamiento (SaaS / Franchise):** Diseñar y documentar el modelo de negocio de licencia que permita a terceros operar bajo la marca ParkCore o su propia marca (white-label). Incluye: términos de licencia, SLAs, soporte técnico, actualizaciones.
- **Machine Learning para predicción de demanda:** Implementar modelos predictivos que utilizan variables como hora del día, día de la semana, mes, clima, eventos locales y tendencias históricas para predecir la ocupación futura con anticipación de 1 a 24 horas.
- **Dynamic pricing:** Sistema de tarifación inteligente que ajusta precios automáticamente según la demanda predicted y reglas de negocio configurables (ej.: pricing mayor durante peak hours, pricing reducido durante baja ocupación para atraer más vehículos).
- **High availability (HA):** Migrar la infraestructura a un modelo de alta disponibilidad con redundancia en todas las capas críticas, soporte para failover automático y RTO (Recovery Time Objective) menor a 5 minutos.
- **Escalabilidad horizontal:** Arquitectura que permita agregar nuevas sedes sin degradación de performance, con capacidad para manejar miles de transacciones simultáneas.

### Alcance funcional

- Arquitectura multi-región con soporte para operación en múltiples países
- Plataforma SaaS con tenants independientes (cada operador tiene su propia base de datos, configuración y branding)
- Modelo de franchise con kit de implementación, capacitación y soporte dedicado
- Motor de ML con modelos de predicción de demanda por sede, entrenados continuamente con datos nuevos
- Sistema de pricing dinámico con reglas configurables y dashboard de impacto financiero proyectado vs. real
- Infraestructura de alta disponibilidad con SLA del 99.9% (3 nueves)
- Centro de operaciones de red (NOC) interno para monitoreo de todas las sedes desde un punto único
- Soporte para integraciones con apps de mapas (Google Maps, Waze, Apple Maps) para mostrar disponibilidad de parqueaderos en tiempo real

### Entregables de la Fase 3

1. **Plataforma SaaS multi-tenant** — Sistema de licenciamiento funcional con portal de administración para proveedores de licencia.
2. **Kit de franchising** — Documentación completa del programa de franchise, incluyendo manuales de operación, tecnología requerida, capacitación y material de marketing.
3. **Motor de predicción ML en producción** — Modelos predictivos operativos con dashboards de predicción vs. realidad.
4. **Sistema de pricing dinámico** — Motor de tarifación inteligente con reglas configurables y reportes de impacto.
5. **Infraestructura de HA** — Arquitectura redundante desplegada con monitoreo 24/7.
6. **Integración con apps de mapas** — APIs de terceros integradas para mostrar disponibilidad en tiempo real.

---

## Por definir (Backlog priorizado)

Las siguientes funcionalidades y características están identificadas como necesarias o valiosas, pero su alcance, prioridad y fecha de implementación no han sido definidos formalmente. Permanecen en el backlog del proyecto hasta que el equipo defina su scope en una fase de planificación posterior.

### Autenticación OAuth2

Se requiere evaluar e implementar un sistema de autenticación robusto basado en OAuth2 (OpenID Connect) que permita:
- SSO (Single Sign-On) para usuarios dentro de la organización ParkCore
- Integración con proveedores de identidad corporativos (Google Workspace, Microsoft Entra, Okta)
- Tokens JWT con refresh automático para las apps móviles
- Gestión de permisos y roles (RBAC) con granularidad por sede y por funcionalidad

**Estado:** Pendiente de evaluación. Depende de la definición del equipo de seguridad y del proveedor de identidad seleccionado.

### Push notifications

Sistema de notificaciones push para ambas aplicaciones móviles (Operador y Cliente) que cubra los siguientes casos de uso:
- Notificación al cliente cuando su vehículo ingresa a un parqueadero
- Notificación al cliente cuando su vehículo egresa con el monto a pagar
- Notificación al operador cuando ocurre una anomalía (intento de acceso con placa no reconocida, falla de cámara, talanquera trabada)
- Notificación al administrador cuando una sede supera un umbral de ocupación definido

**Estado:** Pendiente. Se priorizará después de que la Fase 2 esté estable. Requiere evaluación de proveedor de servicios de push (Firebase Cloud Messaging para Android, APNs para iOS, o alternativa unificada como OneSignal).

### Integración con apps de mapas

Capacidad de publicar la disponibilidad de espacios en parqueaderos ParkCore hacia aplicaciones de navegación y mapas de terceros, tales como:
- **Google Maps** — A través de Google Maps Platform (Places API, Live Location Sharing)
- **Waze** — Mediante integración de APIs de terceros o protocolos de compartir ubicación
- **Apple Maps** — A través de MapKit JS o integración de negocio

El caso de uso principal es que un conductor que busca estacionamiento vea en su app de navegación favorita cuántos espacios libres hay en el parqueadero más cercano y pueda navegar directamente a él.

**Estado:** Dependiente de la Fase 3 (disponibilidad consolidada). Requiere negociación comercial con los proveedores de mapas y validación de APIs disponibles.

### Módulo de reservas

Funcionalidad que permita a los usuarios finales reservar un espacio de estacionamiento con anticipación, ya sea para una hora específica o para un período recurrente (ej. todas las mañanas de lunes a viernes). El flujo esperado incluye:
- Selección de sede, fecha y hora de reserva desde la app
- Pago anticipado para confirmar la reserva
- Check-in automático al llegar al parqueadero (validación de placa en la entrada)
- Penalizaciones por no-show o cancelación tardía

**Estado:** Identificado como deseable en Fase 2, pero su implementación depende de la maduración del sistema de pagos y la infraestructura de ANPR. Podría adelantarse si hay demanda específica de clientes empresariales.

### ML para predicción de demanda

El motor de machine learning para predecir la ocupación y demanda de espacios de estacionamiento es uno de los diferenciadores clave de ParkCore en la Fase 3. Se anticipa que el modelo utilizará las siguientes fuentes de datos:
- Históricos de ingreso/egreso por franja horaria
- Calendario: día de la semana, feriados, eventos programados en la ciudad
- Variables meteorológicas: temperatura, lluvia, índice de calidad del aire
- Datos de tráfico circundante (si están disponibles via APIs públicas)
- Estacionalidad: mes del año, período vacacional

**Estado:** Backlog técnico. Requiere suficiente volumen de datos históricos (mínimo 6 meses de operación) antes de que el modelo sea confiable. La Fase 0 y Fase 1 deben completarse primero para generar estos datos.

---

## Notas sobre el roadmap

**Reevaluación periódica:** Este roadmap se revisará al final de cada fase (gate review) para ajustar prioridades, reestimar esfuerzos y incorporar aprendizajes. El equipo de proyecto es responsable de mantener este documento actualizado y reflejar el estado real vs. el planeado.

**Dependencias críticas:** Varias fases dependen de la finalización exitosa de sus predecesoras. En particular:
- La Fase 1 no puede iniciar hasta que el MVP demuestre viabilidad técnica.
- La Fase 2 requiere que la Fase 1 haya estabilizado la arquitectura multi-sede.
- La Fase 3 necesita que la Fase 2 haya generado suficientes datos históricos y validado el modelo de negocio B2B.

**Flexibilidad de alcance:** Dentro de cada fase, los objetivos marcados como "deseables" pueden moverse a la siguiente fase si el equipo lo considera necesario para cumplir con los objetivos "obligatorios" dentro del tiempo estimado.

**Supuestos declarados:** Este roadmap asume que el equipo de desarrollo se mantiene estable durante los 18 meses, que el presupuesto está disponible según lo planeado, y que no existen cambios regulatorios mayores que obliguen a repriorizar el desarrollo.
