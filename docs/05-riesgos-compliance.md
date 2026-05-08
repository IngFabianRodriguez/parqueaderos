# SECCIÓN 5: RIESGOS, COMPLIANCE Y CONCLUSIONES

---

## 5.1 ANÁLISIS DE RIESGOS

La operación de una plataforma de gestión de parqueaderos como ParkCore involucra múltiples vectores de riesgo que deben ser identificados, evaluados y mitigados de manera proactiva. A continuación se presenta el análisis estructurado por categoría de riesgo, junto con las estrategias de mitigación definidas y una matriz de probabilidad versus impacto para cada riesgo identificado.

### 5.1.1 Riesgos Técnicos

**Falla de conectividad en sede**

La dependencia de conexión a internet en cada punto de estacionamiento es el riesgo técnico más crítico. Una caída de link interrumpe la operación completa del parqueadero, dejando el sistema sin capacidad de leer placas, validar pagos ni abrir la talanquera de forma automática.

- *Probabilidad:* Alta
- *Impacto:* Alto
- *Mitigación:* Despliegue de enlace 4G/LTE como backup automático con failover en menos de 30 segundos. Implementación de edge computing local (Raspberry Pi o mini PC industriales) que mantienen la operación en modo offline, almacenando eventos localmente y sincronizando con la nube al restaurarse la conectividad. El modo offline permite hasta 72 horas de operación autónoma con lectura local de placas y apertura de talanquera mediante validación de listas blancas cacheadas.

**Error de lectura ANPR con placas atípicas**

El sistema de reconocimiento automático de placas (ANPR) puede fallar con vehículos que tengan placas en condiciones atípicas: placas en posición no estándar, vehículos con letras fuera del patrón establecido, placas parcialmente obstruidas por suciedad o adornos, o vehículos extranjeros con formatos diferentes.

- *Probabilidad:* Media
- *Impacto:* Medio
- *Mitigación:* Motor de fallback que, tras dos intentos fallidos de lectura en un intervalo de 5 segundos, activa el modo de registro manual con captura fotográfica del vehículo (frontal y trasera). El operador en punto puede ingresar la placa manualmente o asociar el ingreso a un ticket provisional. La imagen queda vinculada al evento para auditoría posterior. Adicionalmente, el modelo de ML se reentrena mensualmente con placas del parque automotor colombiano.

**Deadlock en apertura de talanquera**

Un bloqueo en el ciclo de apertura o cierre de la talanquera (boom barrier) puede generar colas extensas, incidents con clientes e incluso daños al vehículo si el brazo desciende sobre un vehículo en movimiento.

- *Probabilidad:* Baja
- *Impacto:* Alto
- *Mitigación:* Mecanismo fail-safe mecánico que, ante ausencia de señal eléctrica durante más de 3 segundos, libera el brazo de la talanquera permitiendo el paso manual. Botón de emergencia pulsador (localizado en el pedestal de la talanquera y en la caseta de control) que corta la alimentación del brazo y lo levanta en modo manual. Protocolo de apertura por software que incluye watchdog de 10 segundos: si la talanquera no completa el ciclo, el sistema fuerza la apertura y genera alerta de mantenimiento.

### 5.1.2 Riesgos Operativos

**Manipulación del sistema por parte del operador**

Un operador en punto con acceso al sistema podría manipular registros de ingreso/egreso para beneficiar a vehículos conocidos, eliminar eventos de salida para evitar cobros, o alterartar tarifas aplicadas.

- *Probabilidad:* Media
- *Impacto:* Alto
- *Mitigación:* Arquitectura de logs inmutables (write-ahead log cifrado en servidor central, no modificable desde la sede). Auditorías mensuales de eventos por muestra aleatoria del 5% de los registros. Sistema de doble validación: para descuentos o ajustes manuales se requiere confirmación por parte de un segundo rol (supervisor de sede o administrador regional). Dashboards de anomalías que detectan patrones sospechosos como eventos de entrada sin salida asociados a determinada placa en horario extraordinario.

**Cliente que no paga**

Los parqueaderos que operan bajo modelo de crédito comercial (abonados mensuales, empresas con cuentas corporativas) enfrentan riesgo de cartera vencida. Un cliente moroso puede continuar usando el parqueadero mientras acumula deuda.

- *Probabilidad:* Media
- *Impacto:* Medio
- *Mitigación:* Bloqueo automático de placa en el sistema: al alcanzar 15 días de mora, la placa queda en lista de restricción y el sistema rechaza la apertura automática de talanquera a la entrada. Lista de morosos compartida entre todas las sedes del operador (base de datos centralizada) para evitar que un deudor se traslade a otra sede. Proceso de cobranza reactiva con notificaciones automáticas por SMS y email a los 7, 15 y 30 días de mora.

### 5.1.3 Riesgos de Mercado

**Adopción lenta por parte de parqueaderos tradicionales**

El mercado objetivo incluye operatoros que llevan décadas funcionando con cuadernos y tahocesadoras mecánicas. La resistencia al cambio, la percepción de complejidad y el costo de migración son barreras reales.

- *Probabilidad:* Media
- *Impacto:* Medio
- *Mitigación:* Estrategia de onboarding progresivo con período de prueba de 30 días sin costo en modalidad beta. Equipo de implementación dedicado que realiza la instalación y entrenamiento en sitio durante los primeros 3 días. Pricing diferenciado con plan de entrada bajo que no exige inversión de hardware, permitiendo evaluar el valor antes de escalar. Contenido educativo: webinars mensuales y casos de éxito documentados.

**Entrada de competidores grandes**

Grandes empresas de tecnología o fabricantes internacionales de hardware para parqueaderos podrían lanzar plataformas competidoras con mayor capital de marketing y reconocimiento de marca.

- *Probabilidad:* Baja
- *Impacto:* Alto
- *Mitigación:* Enfoque regional con presencia local, soporte en español, cumplimiento normativo colombiano adaptado y relaciones directas con operatoros nacionales. Personalización profunda por cliente: configuración de tarifas, reglas de negocio y flujos de operación que los productos genéricos internacionales no ofrecen. Construcción de switching costs mediante integración profunda con sistemas del cliente (facturación, CRM, sistemas de edificio).

### 5.1.4 Riesgos Regulatorios

**Cambios en regulaciones de datos personales**

Colombia cuenta con Ley 1581 de 2012 y Decreto 1377 de 2013, pero la interpretación y los requisitos de implementación pueden evolucionar con nueva jurisprudencia o ajustes regulatorios de la SIC.

- *Probabilidad:* Baja
- *Impacto:* Medio
- *Mitigación:* Monitoreo legal activo a través de firma de abogados especializada en protección de datos. Participation en mesas sectoriales de la ANDPB (Asociación Nacional de Protección de Datos). Compliance team interno dedicado que revisa trimestralmente las políticas de privacidad y los avisos de consentimiento. Arquitectura de datos diseñada para facilitar el ejercicio del derecho de supresión (derecho al olvido).

**Normativa de facturación electrónica**

La DIAN exige facturación electrónica para todas las operaciones comerciales. Un parqueadero que no emita comprobantes válidos pierde legitimidad fiscal y puede recibir sanciones.

- *Probabilidad:* Alta (de cumplimiento obligatorio)
- *Impacto:* Medio
- *Mitigación:* Módulo de facturación electrónica integrado desde el día 1 del MVP, conectado directamente a la DIAN mediante el webservice de facturación electrónica. El módulo se actualiza automáticamente ante cambios en resoluciones y esquemas de validación de la DIAN. Para operatoros que ya usan otros sistemas de facturación, se ofrece API de integración con sus soluciones existentes.

### 5.1.5 Riesgos Financieros

**Fluctuación de costos de hosting**

Los costos de infraestructura en la nube pueden incrementarse por cambios en precios de los proveedores, fluctuación cambiaria (si los recursos se facturan en USD) o crecimiento del consumo más allá de lo proyectado.

- *Probabilidad:* Media
- *Impacto:* Bajo
- *Mitigación:* Arquitectura cloud-agnostic que permite migración entre proveedores (AWS, GCP, Azure) según conveniencia de costos. Uso de instancias reservadas para la carga base, con escalamiento on-demand solo para峰值. Monitoreo de costos mensual con alertas automáticas al alcanzar el 80% del presupuesto asignado.

**Adopción menor a la proyectada**

Si el mercado no responde según las proyecciones del modelo financiero, los ingresos serán insuficientes para cubrir costos operativos y de desarrollo.

- *Probabilidad:* Baja
- *Impacto:* Alto
- *Mitigación:* Modelo de suscripción mensual con entry barrier bajo, que permite validar demanda con inversión inicial limitada. KPIs de adopción medidos mensualmente con ajuste de estrategia comercial si el funnel se desacelera. Diversificación de segmentos: no depender de un solo vertical de mercado.

### 5.1.6 Matriz de Riesgos: Probabilidad vs. Impacto

| Riesgo | Probabilidad | Impacto | Nivel de Riesgo |
|--------|-------------|---------|----------------|
| Falla de conectividad en sede | Alta | Alto | **Crítico** |
| Error de lectura ANPR (placas atípicas) | Media | Medio | **Medio** |
| Deadlock en apertura de talanquera | Baja | Alto | **Medio** |
| Manipulación por operador | Media | Alto | **Alto** |
| Cliente moroso | Media | Medio | **Medio** |
| Adopción lenta del mercado | Media | Medio | **Medio** |
| Entrada de competidores grandes | Baja | Alto | **Medio** |
| Cambios en regulación de datos personales | Baja | Medio | **Bajo** |
| Incumplimiento de facturación electrónica | Alta (obligatoriedad) | Medio | **Alto** |
| Fluctuación de costos de hosting | Media | Bajo | **Bajo** |
| Adopción menor a la proyectada | Baja | Alto | **Medio** |

**Interpretación:**
- **Crítico (rojo):** Requiere plan de mitigación activo y monitoreo diario.
- **Alto (naranja):** Requiere controles preventivos y revisión mensual.
- **Medio (amarillo):** Monitoreo periódico y plan de respuesta definido.
- **Bajo (verde):** Aceptación informada con seguimiento trimestral.

---

## 5.2 MARCO REGULATORIO Y COMPLIANCE

El desarrollo y operación de ParkCore en Colombia está sujeto a un ecosistema normativo amplio que abarca la protección de datos personales, la facturación electrónica, la regulación de dispositivos IoT, las normas de tránsito, los servicios financieros y la responsabilidad civil. A continuación se detallan los marcos aplicables y las estrategias de cumplimiento.

### 5.2.1 Protección de Datos Personales

**Régimen legal aplicable**

En Colombia, la protección de datos personales se rige principalmente por la Ley 1581 de 2012 (ley de habeas data) y el Decreto 1377 de 2013, que la reglamenta parcialmente. La Superintendencia de Industria y Comercio (SIC) es la autoridad de protección de datos.

**Datum crítico: la placa de vehículo como dato personal**

Un principio fundamental para el diseño de ParkCore es que las placas de vehículos constituyen datos personales en Colombia. La placa identifica directamente a una persona natural o jurídica: a través de ella es posible establecer la identidad del dueño del vehículo, su comportamiento de movilidad y, en últimos, trazar perfiles individuales. Este reconocimiento tiene implicaciones directas sobre:

- La obligación de obtener **consentimiento informado** del titular de los datos (conductor/usuario) antes de capturar y procesar su placa. El aviso de privacidad debe ser visible en punto de ingreso, en la aplicación móvil y en la página web, con lenguaje claro y accesible.
- La implementación del **derecho de supresión** (derecho al olvido): el usuario puede solicitar la eliminación de sus datos personales, lo cual implica que ParkCore debe poder borrar registros de placa asociados a solicitudes válidas dentro de los plazos legales.
- La obligación de implementar **medidas de seguridad** técnicas y organizativas que protejan los datos contra acceso no autorizado, pérdida o alteración. Esto incluye cifrado en tránsito y en reposo, controles de acceso basados en roles, y registros de auditoría.
- El **registro en el RNBD** (Registro Nacional de Bases de Datos) ante la SIC: ParkCore, en calidad de responsable del tratamiento, debe registrar sus bases de datos que contengan datos personales.
- La existencia de un **canal de atención** a titulares de datos para ejercer sus derechos de acceso, corrección, actualización y supresión.

### 5.2.2 Facturación Electrónica

**Obligatoriedad para empresas**

Desde la implementación progresiva de la facturación electrónica en Colombia, todas las personas naturales y jurídicas que desarrollen actividades económicas están obligadas a expedir documentos equivalentes a factura electrónica conforme a la normativa de la DIAN. La Resolución 0042 de 2020 y sus normas complementarias establecen los esquemas técnicos y operativos.

ParkCore incluye como feature crítico y obligatorio un **módulo de facturación electrónica** que:

- Genera documentos XML en el formato establecido por la DIAN.
- Se conecta directamente al webservice de la DIAN para la validación y aceptación de documentos.
- Soporta los diferentes tipos de documento: factura electrónica de venta, nota crédito y nota débito.
- Maneja el prefijo y la numeración consecutiva autorizada.
- Almacena el CUFE (Código Único de Facturación Electrónica) generado por la DIAN.
- Envía el documento al correo electrónico del comprador de forma automática.

Este módulo es parte del core de la plataforma desde el día 1 del MVP, no como un add-on posterior.

### 5.2.3 Dispositivos IoT y Equipos de Telecomunicación

Si ParkCore utiliza cámaras con capacidad de transmisión wireless (Wi-Fi, Zigbee, LoRa) o dispositivos de telecomunicación en las sedes del parqueadero, estos equipos deben cumplir con la regulación de equipos de telecomunicación establecida por la Comisión de Regulación de Comunicaciones (CRC) y la Aeronáutica Civil (si hay componentes que usen espectro radioeléctrico).

- Las **cámaras ANPR** que se conecten mediante cables Ethernet (estándar en la mayoría de instalaciones) no requieren homologación especial, pero deben cumplir con las normas de seguridad eléctrica aplicables.
- Si se utilizan **dispositivos con transmisión wireless**, es necesario verificar que operen en bandas de frecuencia разрешенных para uso industrial, científico, médico (banda ISM) o conforme a los permisos establecidos por la CRC.
- La **homologación de equipos** ante la CRC aplica únicamente para equipos terminales de telecomunicación que se comercialicen en Colombia. Para equipos instalados en las sedes del parqueadero (cámaras, barreras, sensores) como parte de una solución integral, la responsabilidad de certificación recae en el fabricante o importador del equipo, no en ParkCore como desarrollador de software.
- Se recomienda trabajar con proveedores de hardware que puedan entregar declaración de conformidad con las normas técnicas colombianas aplicables.

### 5.2.4 Normativa de Tránsito y Seguridad en Talanqueras

Las talanqueras (boom barriers) instaladas en parqueaderos están sujetas a regulaciones de seguridad vial establecidas en la Ley 769 de 2002 (Código Nacional de Tránsito) y sus modificaciones, así como a normatividad municipal complementaria.

Requisitos aplicables:

- La talanquera **no debe obstruir la vía pública** en ningún momento. La instalación debe garantizar que, en posición abierta o cerrada, no invada el espacio de la calzada o andén público.
- Debe existir **señalización adecuada** en el área de influencia de la talanquera: advertencia de barrera, indicadores luminosos de apertura/cierre, y reflectores si opera en horario nocturno.
- Los equipos de talanquera deben contar con certificaciones de fabricante que avalen su funcionamiento en las condiciones de temperatura, humedad y voltaje del entorno de instalación.
- En algunos municipios se requiere **permiso de instalación** de elementos en áreas comunes de edificios o en predios con acceso a espacio público. El operador del parqueadero es responsable de gestionar estos permisos.
- Los brazos de talanquera deben contar con **dispositivos de seguridad** (fotoceldas, sensores de presión) que inviertan el sentido de marcha si detectan un obstáculo durante el descenso.

### 5.2.5 Servicios Financieros y Pagos con Tarjeta

Si ParkCore procesa pagos con tarjeta de crédito o débito directamente (es decir, si la plataforma captura datos de tarjeta), se activa el régimen de **PCI-DSS (Payment Card Industry Data Security Standard)**. El cumplimiento de PCI-DSS es obligatorio para cualquier entidad que almacene, procese o transmita datos de titulares de tarjetas.

Estrategia de mitigación recomendada:

- Utilizar **pasarelas de pago externas** (Wompi, PayU, Mercado Pago) que ya tienen certificación PCI-DSS, de modo que ParkCore no almacene ni procese datos de tarjeta directamente. Esto elimina la necesidad de cumplir con los requisitos más estrictos de PCI-DSS para el propio software.
- Si se implementa **monedero digital** o saldo prepago dentro de la plataforma, esto puede constituir la provisión de un servicio de pago, lo cual podría requerir autorización de la Superintendencia Financiera de Colombia conforme a las normas del Estatuto Orgánico del Sistema Financiero. Se recomienda asesoría legal especializada antes de lanzar esta funcionalidad.

### 5.2.6 Responsabilidad Civil y Daños a Vehículos

Un escenario de riesgo jurídico relevante es el daño a un vehículo que se encuentra dentro de las instalaciones del parqueadero. La Ley 1480 de 2011 (Estatuto del Consumidor) establece presunción de responsabilidad del parqueadero por daño o pérdida de bienes del consumidor. Sin embargo, esta responsabilidad puede ser modular mediante condiciones contractuales claras.

Recomendaciones de ParkCore para sus operadores:

- Incluir en los **términos y condiciones** del parqueadero (aceptados por el usuario al momento de ingreso) **cláusulas de limitación de responsabilidad** que exoneren al operador por daños a vehículos que no sean consecuencia directa de negligencia del personal.
- Exigir al operador la contratación de **seguro de responsabilidad civil** que cubra daños a terceros y a vehículos en guarda. Este seguro debe ser presentado como requisito contractual antes de activar la integración con ParkCore.
- Implementar dentro de la plataforma un módulo de **registro de daños** donde el usuario pueda reportar novedades al momento del ingreso (antes de que el vehículo se aparque) o al momento de la salida. Las fotos capturadas por el sistema ANPR constituyen evidencia valioso.
- Establecer un **protocolo de contingencia** ante robo o daño grave: el sistema genera un informe oficial del evento con timestamps, datos del vehículo y registros de acceso que pueden ser utilisés como prueba en procesos legales.

---

## 5.3 CONCLUSIONES Y PRÓXIMOS PASOS

### 5.3.1 Resumen del valor de la plataforma

ParkCore representa una solución integral que transforma la operación fragmentada y manual de los parqueaderos en Colombia en un ecosistema digital controlado, trazable y escalable. La plataforma reduce las pérdidas por fraude y error humano, incrementa la rotación de espacios disponibles, y habilita nuevos modelos de negocio como la gestión de abonados, el prepago digital y la integración con ecosistemas de smart city.

El valor diferenciado de ParkCore reside en la combinación de tecnología ANPR de alta precisión, una arquitectura cloud-agnostic diseñada para оператор multi-sede, y un stack de compliance normativo colombiano integrado desde el diseño (facturación electrónica DIAN, protección de datos Ley 1581, PCI-DSS en procesamiento de pagos). Esto reduce la barrera de adopción para operatoros que enfrentan presión regulatoria y, al mismo tiempo, mejora su eficiencia operativa de forma inmediata.

### 5.3.2 Viabilidad en el mercado colombiano y latinoamericano

El momento es favorable. El parque automotor colombiano crece a tasas superiores al 5% anual, el déficit de espacios de estacionamiento estructurados supera el 40% en las principales ciudades, y la digitalización de trámites comerciales (facturación electrónica, datos en línea) crea un entorno donde la informalidad operativa se vuelve cada vez más costosa. La penetración de pagos digitales superior al 60% elimina la dependencia del efectivo que históricamente fue un obstacle para la automatización. Además, las tendencias de smart city en Bogotá, Medellín y Cali generan demanda institucional por datos de movilidad que solo una plataforma digital puede supplying.

La expansión latinamericana es viable a mediano plazo: países como México, Perú, Ecuador y Chile presentan marcos regulatorios similares en materia de facturación electrónica y protección de datos, lo que permite reutilizar gran parte del compliance stack con adaptaciones menores.

### 5.3.3 Trayectoria propuesta: de MVP a escala nacional

| Fase | Alcance | Duración estimada | Indicadores de éxito |
|------|---------|-------------------|----------------------|
| **MVP** | 3-5 sedes piloto en Bogotá | Meses 1-6 | Lectura ANPR >95% accuracy, tiempo de setup <48h, 0 incidentes críticos |
| **Validación** | 10-20 sedes en Bogotá + 1 ciudad adicional | Meses 7-12 | Ocupación media >70%, reducción de fuga >15%, NPS >50 |
| **Escala inicial** | 50 sedes en 3-4 ciudades | Meses 13-24 | MRR >USD $30K, churn <5% mensual, ROI positivo por sede |
| **Consolidación** | 150+ sedes a nivel nacional | Meses 25-36 | Participación de mercado significativa, equipo de 30+ personas, Series A |

### 5.3.4 Qué se necesita para empezar

Para iniciar la fase de MVP se requieren tres elementos fundamentales:

**1. Decisión del sponsor ejecutivo:** Un sponsor interno con autoridad para asignar presupuesto, tomar decisiones de procurement de hardware y validar la priorización del equipo de desarrollo. Sin este sponsor, el proyecto carece de la línea de decisión necesaria para avanzar con agilidad.

**2. Equipo mínimo viable (EMV):**
- 1 Product Owner / Project Manager con experiencia en proyectos de IoT o hardware
- 2 desarrolladores backend (Node.js o Python, experiencia en microservicios y APIs)
- 1 desarrollador frontend (React o Vue, experiencia en dashboards)
- 1 especialista en ML/ANPR (puede ser tercero con contrato por entregable)
- 1 ingeniero de infraestructura (AWS/GCP, experiencia con Docker/Kubernetes)
- Equipo de implementación en campo: 1 técnico de redes y hardware por cada 5 sedes

**3. Presupuesto inicial estimado para MVP:**
- Desarrollo de software (6 meses): $80M - $120M COP
- Hardware (cámaras, talanqueras, edge devices, instalación): $40M - $60M COP por sede piloto
- Infraestructura cloud y servicios: $5M - $10M COP mensuales
- Licencias de software de terceros (ANPR, pasarela de pagos): $10M - $15M COP mensuales
- **Total estimado MVP:** $180M - $250M COP (aproximadamente USD $45.000 - $65.000)

### 5.3.5 Llamado a la acción: ¿Qué sigue?

La siguiente étape es una **sesión de alineación técnica con el equipo** para priorizar el backlog de desarrollo del MVP. En esta sesión se definirán:

- Los features mínimos del MVP (lectura ANPR, apertura de talanquera, panel de administración, módulo de pagos, facturación electrónica DIAN).
- El stack tecnológico definitivo (lenguaje de programación, framework web, base de datos, proveedor cloud, hardware ANPR).
- El protocolo de instalación en sedes piloto y el plan de acompañamiento.
- Los KPIs técnicos y de negocio que se medirán desde el día 1.
- El cronograma de entregas y las ceremonias ágiles del equipo.

Con esta sesión se busca validar que todas las áreas (negocio, tecnología, legal/compliance, operaciones) tengan una comprensión compartida de lo que se construye, por qué se construye en ese orden, y cómo se medirá el éxito del MVP.

**¿Está su equipo listo para agendar la sesión de alineación técnica?**

---

## 5.4 ANEXOS SUGERIDOS

> Los siguientes anexos se proporcionan como referencia documental complementaria y no forman parte del cuerpo principal de esta propuesta. Se recomienda su inclusión en el versión completa del Business Proposal según la necesidad del destinatario.

- **Anexo A:** Wireframes de UI — Mockups de las pantallas principales de la consola administrativa y la aplicación móvil (referencia visual)
- **Anexo B:** Mockups de la app móvil — Diseño detallado de la interfaz de usuario final para conductor (consulta de cupos, pago, apertura de talanquera)
- **Anexo C:** Diagrama de arquitectura técnica — Vista lógica y física de los componentes del sistema, flujo de datos entre módulos y conexión con dispositivos IoT en sede
- **Anexo D:** Glosario de términos técnicos y de negocio — Definiciones de ANPR, OCR, boom barrier, MRR, churn, CUFE, PCI-DSS, y demás terminología utilizada en la propuesta
- **Anexo E:** Stack tecnológico detallado — Lista completa de tecnologías, frameworks, bibliotecas, servicios cloud y herramientas de terceros con versiones y justificación de selección
- **Anexo F:** Referencias normativas citadas — Textos completos o extractos relevantes de la Ley 1581 de 2012, Decreto 1377 de 2013, Resolución DIAN 0042 de 2020, Ley 769 de 2002 y demás normativa referenced

---

*Documento preparado para efectos del Business Proposal de ParkCore — Plataforma de Gestión de Parqueaderos.*
*Versión del documento: 1.0 — Mayo 2026*
