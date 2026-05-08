# RESUMEN EJECUTIVO

**ParkCore** es una plataforma integral de gestión de parqueaderos diseñada para операdorów de estacionamientos en Colombia y Latinoamérica que requieren controlcentralizado, trazabilidad en tiempo real y automatización de procesos operativos. La solución combine tecnología de reconocimiento automático de placas (ANPR), plataforma en la nube con disponibilidad por sede, y un módulo de CRM de pagos que permite gestionar la relación con el cliente desde la entrada del vehículo hasta la liquidación final.

ParkCore está dirigido a administradores de parqueaderos comerciales, operatoros de cadenas de estacionamientos, propietarios de edificios corporativos con áreas de estacionamiento y empresas de gestión inmobiliaria que operan múltiples sedes. El producto resuelve el problema fundamental de la operación desarticulada: mientras los parqueaderos más pequeños siguen funcionando con cuadernos y cobros manuales, los operatoros grandes carecen de visibilidad consolidada entre sedes y dependen de sistemas heredados que no se integran entre sí.

La plataforma ofrece lectura ANPR de alta precisión para identificar vehículos a la entrada y salida, lo que elimina la necesidad de ticketes físicos y reduce dramáticamente el fraude por manipulación de tickets. Cada sede transmite su disponibilidad de espacios en tiempo real hacia un panel central, permitiendo que los usuarios finales consulten por aplicación móvil o interfaz web cuántos cupos hay disponibles antes de llegar. El módulo de apertura automática de talanquera (boom barrier) se activa tras la validación del pago o la verificación de placa autorizada, eliminando la intervención del personal de punto en el ciclo nominal de ingreso y salida.

El impacto en eficiencia operacional es inmediato y medible. Los operatoros que implementan ParkCore reportan una reducción promedio del 30% en tiempo de rotación por espacio disponible, dado que el proceso de entrada y salida no depende de la digitación manual ni del conteo visual de capacidad. La automatización de talanquera reduce el personal requerido en horarios de baja demanda y elimina errores humanos en la gestión de tarifas. Además, el módulo de CRM de pagos permite identificar patrones de consumo, gestionar abonados y generar estrategias de cobranza reactiva que reducen la cartera vencida en parqueaderos que operan bajo modelo de crédito comercial.

En materia de escalabilidad, ParkCore está diseñado sobredocker y microservicios desplegados en infraestructura cloud-agnostic, lo que permite agregar nuevas sedes sin intervención en la arquitectura existente. Un nuevo punto de estacionamiento se configura en menos de 48 horas incluyendo el provisionamiento de cámaras ANPR, registro del sitio en consola administrativa y entrenamiento del modelo de lectura de placas para el patrón vehicular local. La plataforma soporta desde operaciones de una sola sede hasta cadenas con más de 50 puntos, con niveles de servicio y redundancia diferenciados por tier de suscripción.

---

# DIAGNÓSTICO DE MERCADO

## Panorama del sector de estacionamientos en Latinoamérica y Colombia

El sector de estacionamientos en Colombia y América Latina presenta una realidad dual: por un lado, existe una demanda creciente impulsada por la urbanización acelerada, el aumento del parque automotor y la consolidación de ciudades inteligentes; por otro, la mayoría de los operatoros de parqueaderos siguen operando con modelos de gestión que no han evolucionado significativamente en la última década. En ciudades como Bogotá, Medellín, Cali y Barranquilla, el déficit de espacios de estacionamiento estructurados supera el 40% según estimaciones de gremlias nacionales de movilidad, lo que genera informalidad, caos en vía pública y oportunidades perdidas de ingresos para los propietarios de predios.

El mercado global de soluciones de *parking management* se valora en el rango de USD $9.000 a $11.000 millones para el período 2024-2028, con una tasa de crecimiento anual compuesto (CAGR) estimada entre el 8% y el 12%. Este crecimiento está siendo impulsado principalmente por la adopción de tecnologías de *smart city*, la integración de sistemas IoT en infraestructura urbana y la demanda de soluciones de movilidad que reduzcan la congestión y las emisiones asociadas a la búsqueda de estacionamiento. Latinoamérica representa una porción emergente de este mercado, con un crecimiento proyectado superior al promedio global en los próximos cinco años debido al rezago en adopción tecnológica y a la expansión de normativas de urbanismo que exigen cupos de estacionamiento en desarrollos comerciales y residenciales.

En Colombia específicamente, el marco normativo ha evolucionado para exigir sistemas electrónicos de control en edificios nuevos y centros comerciales de escala mayor, lo que crea una masa crítica de operatoros que necesitan modernizar su operación. La entrada en vigor de regulaciones de facturación electrónica y la digitalización de trámites urbanos han generado un entorno favorable para plataformas que ofrezcan trazabilidad y cumplimiento normativo como valor agregado.

## Dolencias del mercado

El modelo de operación predominante en la región presenta cuatro dolencias estructurales que ParkCore busca resolver.

La **fragmentación** del mercado es la primera y más visible. Existe una atomización extrema de pequeños operatoros que gestionan entre 20 y 100 espacios con sistemas manuales, y que representan más del 70% del mercado según estimaciones del sector. Esta fragmentación impide la negociación colectiva con proveedores tecnológicos, diluye la capacidad de inversión en innovación y perpetúa prácticas operativas ineficientes.

Los **cobros manuales** constituyen la segunda dolencia. La dependencia de收回 efectivo en punto, la digitación de tarifas en tahocesadoras mecánicas y la ausencia de controls de rotación generan pérdidas sistemáticas por error humano, robo de efectivo y fugas en la cadena de recaudación. Estudios del sector estiman que hasta un 15% de los ingresos potenciales se pierden en operación manual por concepto de fugas, ineficiencia en rotación y ausentismo del personal.

La **falta de trazabilidad** es la tercera. Sin un registro digital del movimiento de vehículos, los operatoros no pueden generar reportes confiables de ocupación,峰值 de demanda, duración promedio de estancia ni patrones de ingreso por hora. Esta opacidad operativa impide la toma de decisiones basada en datos y dificulta la obtención de financiamiento o la valorización comercial de los activos de estacionamiento.

Las **fugas de dinero** relacionadas con la manipulación de tickets, la evasión en zonas de cobro por porcentaje, y la ausencia de controles antifraude automáticoss, representan pérdidas que pueden oscilar entre el 8% y el 20% de la facturación teórica dependiendo del modelo de operación. En un negocio de márgen operativo estrecho (típicamente entre el 15% y el 25% de margen neto), estas fugas marcan la diferencia entre rentabilidad y pérdida.

## Tendencias habilitantes

Cuatro tendencias tecnológicas convergentes están creando el entorno perfecto para una solución como ParkCore.

La tecnología **ANPR (Automatic Number Plate Recognition)** ha alcanzado madurez suficiente para operar en condiciones ambientales adversas, con vehículos a velocidades de hasta 40 km/h y con precisión superior al 95% incluso con placas dañadas o sucias. El costo de cámaras especializadas en ANPR ha caído más del 60% en los últimos cinco años, lo que hace la inversión accesible para operatoros de cualquier tamaño.

La adopción de **pagos digitales** en Colombia se ha acelerado significativamente, con transacciones digitales que superan el 60% del total de pagos según reportes del Banco de la República. La penetración de billeteras digitales, transferencia bancaria en tiempo real y códigos QR como medio de pago en parqueaderos elimina la fricción del efectivo y habilita modelos de suscripción y prepago que antes eran inviables.

El ecosistema **IoT (Internet of Things)** ha madurado lo suficiente para ofrecer hardware de talanquera, sensores de ocupación y cámaras conectadas a costos que permiten un ROI atractivo. Los protocolos MQTT y APIs RESTful permiten integración directa con plataformas en la nube sin necesidad de middleware propietario.

Finalmente, el concepto de **Smart Cities** ha dejado de ser un ejercicio teórico para convertirse en política pública. Las alcaldías de las principales ciudades colombianas están requiriendo cada vez más integración de datos de movilidad, cupos disponibles y tarifas dinámicas en sus plataformas de gestión urbana, lo que crea una demanda institucional por sistemas de parqueo digitalizados.

## Por qué ahora es el momento

El momento para construir y desplegar ParkCore es ahora por tres razones convergentes. Primero, la infraestructura de conectividad en zonas urbanas de Colombia ha alcanzado niveles de disponibilidad y confiabilidad que hacían inviable una solución en la nube hace apenas tres años. Segundo, la base de usuarios finales está lista para adoptar pagos digitales de estacionamiento a través de aplicación móvil o web, sin necesidad de efectivo ni interacción presencial. Tercero, los márgenes de los operatoros están bajo presión creciente debido al incremento en costos de vigilancia, mantenimiento y seguros, lo que hace que la eficiencia operativa ya no sea un lujo sino una necesidad de supervivencia.

---

# MODELO DE NEGOCIO CANVAS

## Segmento de clientes

- Operatoros de parqueaderos comerciales independientes con más de 30 cupos en ciudades principales de Colombia
- Cadenas de estacionamientos con múltiples sedes que requieren gestión centralizada
- Administradoras de edificios corporativos y centros comerciales con áreas de estacionamiento propias
- Empresas de gestión inmobiliaria que operan portafolios de activos con componente de estacionamiento
- Operadores de eventos y recintos masivos con necesidad de gestión temporal decupos

## Propuesta de valor

1. **Trazabilidad total de operación**: Registro digital de cada vehículo que ingresa y sale, con hora, fecha, placa, tipo de tarifa y método de pago, eliminando la opacidad operativa y habilitando reportes de ocupación, peak hours y duración promedio de estancia.

2. **Eliminación de fugas de dinero**: Automatización del ciclo de cobro que remueve el efectivo del proceso, reduce el fraude por manipulación de tickets y elimina errores de digitación en tarifas, protegiendo entre el 8% y el 20% de la facturación teórica que actualmente se pierde.

3. **Disponibilidad en tiempo real**: Panel centralizado que muestra el estado de ocupación de cada sede en tiempo real, permitiendo decisiones operativas informadas, redirección de flujo vehicular y optimización de capacidad instalada.

4. **Apertura automática de talanquera**: Validación de placa o comprobante de pago para apertura de barreras sin intervención de personal, reduciendo costos de operación y mejorando la experiencia del usuario final.

5. **CRM de pagos integrado**: Gestión de abonados, facturación electrónica, seguimiento de cartera y estrategias de cobranza desde una misma plataforma, fortaleciendo la relación con el cliente recurrente y reduciendo la rotación de clientes.

6. **Escalabilidad sin fricción**: Agregado de nuevas sedes en menos de 48 horas sin necesidad de cambios en la arquitectura de software, soportando desde 1 hasta más de 50 puntos de operación bajo el mismo modelo de gestión.

7. **Cumplimiento normativo**: Generación automática de reportes para facturación electrónica DIAN, soporte para tarifas reguladas por типо de vehículo, y auditoría completa de movimientos para requerimientos legales o tributarios.

## Canales de distribución

- Venta directa por equipo comercial propio enfocado en el segmento empresarial
- Canal digital: landing page, demos en video y pruebas gratuitas de 30 días
- Alianzas con distribuidores e integradores de sistemas de seguridad y automatización
- Recomendaciones y referencias de clientes existentes (programa de referidos)
- Ferias del sector inmobiliario, conferencias de movilidad urbana y eventos de *PropTech*

## Relaciones con clientes

- Onboarding estructurado con ingeniero de implementación dedicado durante los primeros 30 días
- Soporte técnico via chat en tiempo real, correo electrónico y línea telefónica durante horario laboral y de guardia
- Capacitación virtual y en sitio para operadores de punto y administradores de sede
- Revisiones mensuales de KPIs operacionales como parte del modelo de éxito del cliente
- Comunidad de usuarios con acceso a canal privado de actualizaciones y mejores prácticas

## Fuentes de ingresos

1. **Suscripción SaaS por sede**: Plan mensual o anual por punto de estacionamiento conectado, con tiers de funcionalidad diferenciados (Básico, Profesional, Enterprise). Ingreso recurrente predecible.

2. **Licencia de hardware ANPR**: Venta o arrendamiento de cámaras, talanqueras y sensores de ocupación como parte del paquete de implementación. Ingreso por evento de alta.

3. **Transacciones procesadas**: Tarifa por cada transacción de pago procesada a través de la plataforma, aplicada sobre el valor total recolectado. Modelo variable ligado al uso.

4. **Módulo de abonados**: Cargo adicional por gestión de cartera de clientes recurrentes, facturación electronica yCRM de pagos, facturado como porcentaje de la cartera administrada o valor fijo por abonado activo.

5. **Servicios profesionales**: Implementación personalizada, desarrollo de integraciones a sistemas existentes (ERP, software de administración de edificios) y capacitación avanzada.

## Estructura de costos clave

- **Infraestructura cloud**: Costos de servidores, bases de datos, CDN y servicios administrados (AWS / GCP / Azure) escalados por número de sedes y transacciones
- **Desarrollo de software**: Equipo de ingeniería (backend, frontend, mobile, DevOps), herramientas de desarrollo y licencias de software
- **Hardware**: Cámaras ANPR, talanqueras, sensores de ocupación, equipos de red en sitio para clientes en modelo de arrendamiento
- **Ventas y marketing**: Equipo comercial, campañas digitales, asistencia a ferias y materiales de ventas
- **Soporte y éxito del cliente**: Equipo de soporte, ingeniero de implementaciones y costos de capacitación
- **Infraestructura deatención**: Herramientas de CRM, plataforma de soporte y sistemas de monitoreo de disponibilidad

## Actividades clave

- Desarrollo continuo de la plataforma y lanzamiento de nuevas funcionalidades
- Implementación y configuración de nuevas sedes en sitio
- Mantenimiento y calibración de modelos de reconocimiento de placas (machine learning)
- Gestión de integraciones con pasarelas de pago, sistemas de facturación electrónica y plataformas de movilidad
- Marketing y generación de demanda en el segmento objetivo
- Gestión de relación con clientes y mejora continua del NPS

## Recursos clave

- **Equipo de ingeniería**: Desarrolladores full-stack, ingenieros de machine learning (visión por computadora), especialistas en infraestructura cloud y DevOps
- **Plataforma tecnológica**: Infraestructura cloud con alta disponibilidad, base de datos de eventos de vehículos, motor de reglas de tarifación, módulo de pagos y CRM
- **Base de datos de placas**: Repositorio de patrones de placas colombianas para entrenamiento de modelos ANPR, con datos anonimizados de vehículos
- **Relaciones con clientes**: Portafolio de operatoros activos y pipeline comercial en el segmento objetivo
- **Conocimiento del dominio**: Expertise en regulación de parqueaderos por ciudad, estructuras tarifarias y norms de facturación electrónica en Colombia

## Alianzas clave

- **Fabricantes de hardware ANPR**: Socios estratégicos para provisión de cámaras y equipos de lectura de placas con descuentos por volumen
- **Pasarelas de pago**: Integraciones con PayU, ePayco, Wompi y procesadores de tarjeta para garantizar opciones de pago diversificadas
- **Proveedores de talanqueras**: Integración técnica y comercial con marcas como CAME, Nice y Beder como proveedores certificados de equipos de apertura
- **Integradores de sistemas de seguridad**: Alianzas con empresas de instalación y mantenimiento de sistemas electrónicos de seguridad que puedan revender e implementar ParkCore
- **Plataformas de Smart City**: Integración con plataformas municipales de movilidad para publicación de disponibilidad de cupos en tiempo real

## Métricas principales

### North Star Metric

**Número de transacciones de pago procesadas por mes** a través de la plataforma. Esta métrica captura el volumen de uso real de ParkCore, refleja la confianza del operatoro en el sistema para su operación diaria y es el mejor predictor de ingresos recurrentes. Cada vehículo que paga a través de la plataforma genera una transacción que valida el ciclo completo del producto.

### KPIs de apoyo

**1. Ocupación promedio por sede (%)**: Porcentaje de espacios ocupados sobre capacidad total, promediado por mes y por sede. Este indicador mide qué tan bien está siendo utilizada la capacidad instalada y es el principal conductor de ingresos potenciales del operador. Meta: superar el 65% de ocupación promedio en clientes con más de 6 meses de operación.

**2. Tiempo de implementación hasta go-live (horas)**: Tiempo transcurrido desde la firma del contrato hasta que una nueva sede está operativa transmitiendo datos a la plataforma. Este KPI refleja la eficiencia del proceso de implementación y la escalabilidad operativa del negocio. Meta: inferior a 48 horas por sede.

**3. Net Promoter Score (NPS)**: Calificación de recomendación de la plataforma por parte de los operatoros, medida trimestralmente mediante encuesta breve. El NPS es el indicador más robusto de retención y expansión deRevenue. Meta: superior a 50 puntos, con走势 crescente.
