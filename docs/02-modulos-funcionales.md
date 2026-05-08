# 02 — Módulos Funcionales

## 1. Módulo de Disponibilidad y Gestión de Sedes

El módulo de disponibilidad y gestión de sedes constituye el núcleo operativo de la plataforma, proporcionando una visión integral y en tiempo real del estado de cada parqueadero dentro de la red. Este componente fue diseñado bajo una arquitectura distributed system que permite escalar horizontalmente conforme crece el número de sedes, manteniendo consistencia eventual de datos a través de un broker de mensajes MQTT y una base de datos TimescaleDB optimizada para series temporales.

### Dashboard centralizado por sede

Cada sede dispone de un dashboard operativo personalizado que presenta de manera sintetizada los indicadores más relevantes: total de espacios, espacios disponibles, porcentaje de ocupación actual, ingresos del día y estado de la talanquera. El dashboard se actualiza mediante WebSocket con una latencia menor a 200 ms, garantizando que el operador visualice información vigente sin necesidad de refrescar la página. La interfaz está diseñada con un enfoque mobile-first, adaptándose fluidamente a tablets y monitores de pared típicos en cabinas de control.

### Contador de espacios totales vs. disponibles en tiempo real

El sistema mantiene un contador dinámico que resta de manera atómica cada vez que un vehículo ingresa y suma cuando egresa. Este contador se calcula a partir de los eventos generados por los sensores IoT instalados en cada plaza de estacionamiento, complementados con la lógica de validación del módulo ANPR. La diferencia entre el total de espacios configurados por sede y el conteo en tiempo real se muestra como un número prominente en el dashboard, junto con una barra de progreso visual que cambia de color según el nivel de ocupación: verde (0-70%), amarillo (70-90%) y rojo (90-100%).

### Mapa de calor por zonas del parqueadero

La plataforma incorpora un visualizador de mapa de calor (heatmap) generado a partir de la agregación de datos de ocupación por zona durante ventanas de tiempo configurables. Este mapa permite identificar patrones espaciales de demanda: zonas con alta rotación, áreas congestionadas y espacios subutilizados. El heatmap se renderiza sobre un plano arquitectónico SVG del parqueadero, cargado dinámicamente desde la configuración de cada sede, y se actualiza cada 5 minutos con datos agregados. El administrador puede seleccionar diferentes capas de visualización: ocupación actual, promedio histórico, y variación respecto a días anteriores.

### Historial de ocupación por hora/día/semana/mes

Todo evento de ingreso y egreso se almacena con marca de tiempo de alta precisión (timestamp ISO 8601 con timezone), permitiendo reconstruir la curva de ocupación de cualquier periodo. El módulo ofrece vistas preconfiguradas de historial: ocupación por hora (útil para detectar horas pico), ocupación diaria (para análisis de tendencias diarias), ocupación semanal (para planificación de turnos y recursos) y ocupación mensual (para reportes executive y facturación). Los datos se agregan en buckets temporales de 15 minutos para graficación eficiente, y se retienen durante 36 meses en línea caliente antes de archivarse a almacenamiento frío.

### Alertas de capacidad (lleno al 90%, etc.)

El sistema de alertas configurable permite definir umbrales de ocupación que, al ser superados, generan notificaciones push al operador de turno y al administrador de la sede. Los umbrales se expresan como porcentaje del total de espacios y son editables por sede. Cuando la ocupación alcanza el 90%, el sistema envía una alerta prioritaria; al llegar al 100%, una segunda alerta indica capacidad llena. Adicionalmente, el administrador puede activar alertas por subocupación (por ejemplo, menos del 20% en horarios pico), lo que podría indicar una falla en sensores o un evento anómalo. Las alertas se registran en un log de auditoría con Acknowledge para seguimiento.

### Estados: abierto/cerrado/mantenimiento

Cada sede puede encontrarse en uno de tres estados operativos: **Abierto** (operación normal, aceptando ingresos y cobros), **Cerrado** (sin operación, barrera bloqueada, solo permite egresos de vehículos con ticket activo) y **Mantenimiento** (indicación de trabajos en la infraestructura, sensores temporalmente fuera de servicio, con generación automática de reporte al equipo de soporte). La transición entre estados se realiza desde el dashboard con autenticación de doble factor y genera un evento en el log de auditoría. En estado de mantenimiento, el sistema puede seguir funcionando parcialmente con operación manual asistida.

### Sensores IoT: tipos (lidar, ultrasonido, cámara con AI), cómo se integran

La plataforma soporta múltiples tecnologías de sensor para la detección de presencia vehicular, adaptándose a las condiciones físicas y presupuesto de cada sede:

- **Sensor LIDAR**: Utiliza tecnología de escaneo láser en 2D para detectar la presencia de un objeto en una plaza con precisión milimétrica. Ideal para instalaciones indoor donde el polvo y la humedad son controlables. Se comunica vía protocolo Modbus TCP/IP.

- **Sensor ultrasonido**: Emite pulsos acústicos y mide el tiempo de retorno para determinar si un espacio está ocupado o libre. Es la opción más económica y se 安装 commonly en techo. Comunica por protocolo RS485 con conversión a MQTT mediante un gateway edge.

- **Cámara con inteligencia artificial**: Cámaras IP con algoritmos de deep learning que detectan no solo ocupación sino también tipo de vehículo, condiciones de riesgo (objeto abandonado, vehículo mal estacionado) y vandalismo. Las cámaras con AI procesan el análisis en el borde (edge computing) y solo transmiten eventos, reduciendo ancho de banda.

Todos los sensores se conectan a un **gateway IoT edge** por sede que actúa como concentrador, normaliza los datos y los transmite al backend vía MQTT sobre TLS. El gateway mantiene un buffer local de 24 horas en caso de pérdida de conectividad con la nube.

### App móvil para operadores en piso

La aplicación móvil ParqOperator está disponible para Android y iOS, y permite al operador de piso realizar las siguientes funciones sin estar atado a una cabina: consultar la ocupación en tiempo real de cualquier zona, abrir y cerrar talanqueras manualmente, reportar incidencias con fotografías integradas, recibir alertas de capacidad y solicitudes de soporte, y visualizar el historial de transacciones de la última hora. La app sincroniza datos en background y funciona en modo offline limitado, guardando las acciones localmente para subirlas cuando haya conectividad.

---

## 2. Módulo de Lectura de Placas (ANPR)

### ¿Qué es ANPR y cómo funciona en el contexto de parqueaderos?

ANPR (Automatic Number Plate Recognition) o LPR (License Plate Recognition) es un sistema de visión artificial que permite capturar, interpretar y almacenar automáticamente los caracteres de una matrícula vehicular a partir de imágenes digitales. En el contexto de parqueaderos, el ANPR funciona como el identificador único de cada vehículo que ingresa al sistema, reemplazando o complementando el ticket físico. El flujo típico opera en dos fases: en la entrada, una cámara especializada captura la placa del vehículo, se procesa la imagen mediante un algoritmo de OCR (Optical Character Recognition) optimizado para matrículas, y se asocia un timestamp de ingreso junto con la identificación de la cámara y la zona. En la salida, se repite la captura, se compara con la base de datos de vehículos activos, se calcula la duración de estadía, se aplica la tarifa correspondiente y se genera el cobro o se valida un abono previo. El sistema de ANPR de la plataforma alcanza una precisión superior al 98% bajo condiciones controladas de iluminación y velocidad vehicular, y utiliza un modelo de deep learning (basado en arquitectura YOLO optimizada) entrenado con un dataset de más de 50.000 matrículas colombianas incluyendo formatos de varios departamentos.

### Cámaras recomendadas: tipos (fija, domo, LPR dedicada), ángulo de instalación, iluminación IR

La selección de la cámara ANPR depende de la configuración física del punto de control y las condiciones ambientales:

- **Cámara fija tipo LPR dedicada**: Son cámaras diseñadas específicamente para lectura de placas, con óptica especializada de alta velocidad de obturación (1/10000s mínimo), filtro IR-pass para operación nocturna y lente varifocal de 9-22 mm que permite ajustar el campo de visión según la distancia del punto de captura. Se recomiendan para puntos de entrada/salida con un solo carril y donde el vehículo se detiene completamente.

- **Cámara domo varifocal**: Cámaras de tipo domo para 安装 en techo o pared, con resolución mínima de 5 MP, WDR (Wide Dynamic Range) de 120 dB para compensar contraluz, y capacidad de lectura de placas en vehículos en movimiento hasta 40 km/h. Ideales para patios de rotación donde el vehículo no se detiene.

- **Cámara fija con iluminador IR externo**: Para entornos con iluminación variable, se recomienda una cámara IP de 4 MP con lente motorizada acompañada de un iluminador IR de LEDs con longitud de onda 850 nm, colocado en ángulo de 30 grados respecto al eje de la placa para evitar reflejos. El iluminador se activa automáticamente mediante sensor crepuscular.

El **ángulo de instalación** recomendado es de 30 a 45 grados respecto a la horizontal, con la cámara montada a una altura de 2.5 a 4 metros sobre el nivel de la calzada, apuntando hacia la zona donde se ubicará la placa del vehículo cuando este se detenga en el punto de control. Es fundamental que el campo de visión no incluya simultáneamente la placa del vehículo en espera y la del vehículo en circulación en carriles adyacentes, para evitar lecturas cruzadas. Se recomienda realizar una calibración in situ con el vehículo de pruebas de la instalación, ajustando el enfoque y la exposición antes de poner en producción.

### Flujo de entrada: detección de vehículo → captura de placa → almacenamiento timestamp

El flujo de entrada opera de la siguiente manera: un sensor de presencia (lazo inductivo virtual mediante análisis de vídeo o sensor de presencia externo) detecta que un vehículo ha ingresado a la zona de captura. Inmediatamente la cámara ANPR toma una ráfaga de 3 a 5 imágenes en un intervalo de 100 ms. El software de procesamiento selecciona la imagen con mayor nitidez de la placa y ejecuta el OCR. El resultado se normaliza (eliminación de espacios, conversión a mayúsculas, remoción de caracteres especiales no válidos según el formato colombiano) y se almacena en la base de datos como un nuevo registro de ingreso con los siguientes campos: placa, timestamp de entrada, id_camara, id_sede, id_zona_asignada (si aplica), tipo_veiculo, y un hash único de sesión. El sistema luego envía una instrucción a la talanquera de entrada para que se abra y registra el evento de apertura con éxito o fallo. Todo el proceso, desde la detección hasta la apertura de la barrera, se ejecuta en menos de 800 ms en condiciones normales.

### Flujo de salida: captura de placa → búsqueda en BD → cálculo de duración → tarifa → pago o validación

En la salida, el conductor se aproxima al punto de control y el sistema ejecuta el mismo proceso de captura de placa. Una vez obtenu la placa, el sistema busca en la base de datos de vehículos activos la coincidencia exacta más reciente con estado "en parqueadero". Si se encuentra, se calcula la duración restando el timestamp de entrada del timestamp actual. El sistema aplica la tarifa configurada para esa sede según el plan asociado (por minuto, por hora, etc.) y muestra el valor a cobrar en el totem o pantalla de salida. Si el vehículo tiene un plan prepago activo (mensual, empresarial), el sistema valida la cobertura y permite el egreso sin cobro adicional. Si el vehículo es de un cliente con saldo abonado, se descuenta del saldo disponible y se permite el egreso. Si no hay coincidencia o la placa es ilegible, el sistema transfiere la atención a un operador para validación manual. El registro de egreso incluye timestamp de salida, valor cobrado, método de pago utilizado, y referencia de transacción.

### Integración con barrera/talanquera de entrada y salida

La apertura de la talanquera está estrictamente condicionada a la validación positiva del sistema. Tras un ingreso exitoso, el módulo ANPR envía una señal digital al controlador de la talanquera (via relay o protocolo MQTT) únicamente después de que el registro de ingreso haya sido confirmado en la base de datos. Esto previene aperturas no autorizadas. En la salida, la talanquera se abre únicamente cuando el módulo de pagos confirma que elvehículo tiene sus obligaciones al día (pago confirmado, plan válido, o saldo suficiente). La señal de apertura es un pulso de 500 ms en el relay de la talanquera, y el sistema registra el tiempo de respuesta de la barrera para monitoreo de SLA. Si la talanquera no se abre en 3 segundos después de la instrucción, el sistema genera una alerta de falla y registra el incidente.

### Manejo de placas repetidas, vehículos no registrados, placas rotas/ilegibles

Dado que en Colombia es común que circulen vehículos con placas en mal estado, con sustrato reflectivo deteriorado, o con placas adaptadas (por ejemplo, motorcycles con placas de moto en posición incorrecta), el sistema implementa un protocolo de contingencia: si el OCR no logra una lectura confiable (confianza inferior al 70%), el sistema automáticamente toma una foto en alta resolución y la envía al dashboard del operador junto con los datos crudos del OCR (incluyendo los caracteres sospechosos). El operador puede corregir la placa manualmente o marcar el vehículo como "lectura fallida" para permitir el ingreso con ticket manual. En el caso de vehículos con placas repetidas (dos vehículos con la misma placa en el sistema de manera simultánea — situación rara pero posible por clonación de placas), el sistema detecta el conflicto y genera una alerta de seguridad, reteniendo al vehículo en cuestión para verificación. Los vehículos sin registro previo en la base de datos se treat como "visitante ocasional" y se les genera un ticket temporal.

### Validación de pago: verificación en tiempo real con módulo CRM

Una vez que el usuario ejecuta el pago (a través del totem de pago, la app móvil, o un cajero automático), el módulo de pagos envía una confirmación al módulo CRM, que actualiza el estado del vehículo a "pagado" en la base de datos con timestamp de pago, valor, método y referencia. Cuando el vehículo se acerca a la salida, el módulo ANPR envía la placa al módulo CRM para validación. El CRM responde en menos de 100 ms con el estado: "pagado", "pendiente", "plan_valido_hasta", "bloqueado" o "desconocido". La talanquera se abre únicamente si el estado es "pagado" o "plan_valido". Esta verificación en tiempo real garantiza que no se permita el egreso a vehículos con pagos pendientes, salvo autorización manual del operador.

### Tiempos de respuesta esperados (<500ms)

La plataforma está diseñada para que el tiempo total de ciclo — desde que la placa es capturada por la cámara hasta que se recibe la respuesta de validación del sistema — no exceda los 500 ms en el percentil P95. Para lograr esto se implementan las siguientes optimizaciones: el servicio de OCR corre en un servidor dedicado cercano al edge (on-premise) para minimizar latencia de red, la base de datos de vehículos activos se mantiene en memoria cache (Redis cluster) con sincronización asíncrona cada 5 segundos, y las llamadas entre módulos internos utilizan gRPC con protobuf para máxima eficiencia de serialización. El SLA de disponibilidad del servicio ANPR es de 99.5% medido mensualmente.

### Offline mode: qué pasa si se cae la conexión

En escenarios de pérdida de conectividad entre la sede y el datacenter central, el gateway edge de cada sede entra en modo offline y continúa operando de manera autónoma. El gateway mantiene una base de datos SQLite local con la lista de vehículos autorizados (planes activos, flotas, morosos actualizados hace menos de 24 horas). El sistema sigue capturando placas y comparándolas contra la base local, permitiendo ingresos y egresos normales. Cada transacción offline se marca con un flag "offline_sync" en el registro. Cuando la conectividad se restaura, el gateway sincroniza bidireccionalmente las transacciones pendientes con el servidor central mediante un protocolo de reconciliación que resuelve conflictos (por ejemplo, si un pago se registró offline pero el usuario también pagó online, prevalece el pago online y se genera nota de crédito). El operador recibe una notificación push cuando el sistema entra y sale del modo offline, junto con un reporte de transacciones pendientes por sincronizar.

---

## 3. Módulo CRM de Pagos y Cobros

### Registro de clientes: personas naturales y empresas/flotas

El módulo CRM de la plataforma gestiona dos perfiles principales de cliente: personas naturales y empresas o flotas. Para personas naturales, el registro incluye datos básicos: nombre completo, número de documento de identidad, correo electrónico, número de celular, y la relación uno a muchos con los vehículos que posee (placa, marca, modelo, color, tipo de vehículo). La verificación de identidad se realiza mediante envío de código OTP al celular registrado. Para empresas y flotas, el registro es más robusto e incluye: razón social, NIT, dirección, nombre del contacto financiero, contratos asociados, y un listado ilimitado de vehículos de la flota con sus placas y категории (empleado, visitante, contractor). Cada perfil empresarial puede tener múltiples subcuentas con límites de gasto y permisos diferenciados. La plataforma soporta la creación de grupos de facturación consolidados para empresas con múltiples sedes de parqueadero.

### Historial de uso por placa/propietario

Cada placa registrada en el sistema tiene un historial completo de uso que incluye: fecha y hora de cada ingreso, fecha y hora de cada egreso, duración de cada estadía, zona del parqueadero utilizada, valor cobrado, método de pago, y referencia de la transacción. Este historial es consultable por el propietario desde la app móvil o el portal web, filtrable por rango de fechas. Para empresas, el historial consolidado muestra los movimientos de toda la flota con desglose por vehículo, permitiendo exportar reportes para auditoría de gastos de movilidad de sus empleados. El historial se mantiene indefinidamente para clientes activos y durante 12 meses para clientes inactivos antes de archivarse.

### Planes: por minuto, por hora, diario, mensual, empresas (B2B)

La plataforma soporta un sistema flexible de tarifación con los siguientes planes estándar:

- **Plan por minuto**: Tarifa base aplicada proporcionalmente al tiempo de estadía, facturada al segundo. Mínimo de cobro equivalente a 15 minutos.

- **Plan por hora**: Tarifa plana por cada hora completa o fracción dentro de un rango horario predefinido (por ejemplo, de 6:00 a 22:00). Comúnmente usado en parqueaderos de centros comerciales.

- **Plan diario**: Tarifa única por día calendario (24 horas desde el ingreso), independientemente del tiempo exacto de estadía.

- **Plan mensual**: Suscripción recurrente con acceso ilimitado durante el mes calendario. El sistema genera facturación automática el primer día de cada mes y aplica descuentos por pago anticipado.

- **Plan empresarial (B2B)**: Contrato personalizado por volumen con tarifas negociadas, límites de consumo, facturación consolidada mensual, y posibilidad de saldo prepago que se descuenta automáticamente por cada uso. Los planes B2B pueden incluir cláusulas de SLA de disponibilidad y soporte dedicado.

Los planes son configurables por sede, lo que permite que una misma red de parqueaderos tenga tarifación diferente según ubicación y target de mercado.

### Métodos de pago: efectivo (cajero), PSE, tarjeta débito/crédito, apps (Nequi, Daviplata), transferencia

El módulo de pagos integra múltiples canales de cobro para maximizar la conveniencia del usuario:

- **Efectivo a través de cajero automático (CAM)**: Totems de pago con reconocimiento de billete y cambio, installed en la salida o en puntos estratégicos del parqueadero. El cajero se comunica con el backend mediante protocolo HTTPS cifrado. El cambio se entrega en billetes y monedas, y el sistema registra la transacción con serial del cajero.

- **PSE (Pagos Seguros en Línea)**: Integración directa con la pasarela de pagos ACH de PSE, que permite al usuario seleccionar su banco y realizar el pago desde su cuenta corriente o de ahorros en tiempo real.

- **Tarjeta débito y crédito**: Integración con procesador de pagos PCI-DSS compliant (actualmente se soporta Kushki como procesador principal) para captura de datos de tarjeta en el totem o en la app. Se soportan tarjetas Visa, Mastercard, y American Express.

- **Apps de pago móvil**: Integración con Nequi y Daviplata mediante APIs oficiales, permitiendo al usuario escanear un código QR en el totem o confirmar el pago desde la app del parqueadero. Estas интеграции son especialmente populares en el mercado colombiano por su adopción masiva.

- **Transferencia bancaria**: Disponible para clientes empresariales B2B con facturación consolidada mensual. El sistema genera una referencia de pago única por cada transacción para conciliación bancaria automática.

- **Saldo prepago en billetera virtual**: El usuario puede cargar saldo en su cuenta del parqueadero desde la app o la web, y este saldo se descuenta automáticamente en cada uso. Se aplica un programa de "bono por recarga" (por ejemplo, 5% extra por recargas superiores a $50.000 COP).

### Estados de pago: pendiente, confirmado, fallido, reembolsado

Cada transacción de pago atraviesa un ciclo de estados que se registran en la base de datos con timestamp y motivo:

- **Pendiente**: El pago fue solicitado pero aún no ha sido capturado o confirmado por el procesador. El vehículo permanece con status "pendiente" y no puede egresar hasta que el pago sea confirmado o cancelado. Las transacciones pendientes que no se resuelven en 15 minutos se marcan automáticamente como canceladas.

- **Confirmado**: El procesador de pagos confirmó la transacción. El sistema actualiza el estado del vehículo a "pagado" y habilita el egreso. Se genera comprobante de pago (PDF o email según preferencia del cliente).

- **Fallido**: La transacción fue intentada pero rechazada por el procesador (fondos insuficientes, tarjeta vencida, banco rechazar, etc.). El sistema registra el código de error del procesador y permite al usuario reintentar con otro método de pago. Se genera notificación push con el motivo del fallo.

- **Reembolsado**: El pago fue confirmado pero el administrador o el sistema automatizado (por ejemplo, en caso de doble cobro) ejecutó un reembolso. El reembolso se procesa por el mismo canal del pago original y se registra con motivo, valor, y fecha. Los reembolsos requieren autenticación del administrador.

### Facturación electrónica integrada

La plataforma cuenta con integración nativa con la DIAN (Dirección de Impuestos y Aduanas Nacionales) para la emisión de documentos tributarios electrónicos (Factura Electrónica de Venta, Nota Débito, Nota Crédito) según la normativa colombiana vigente (Resolución 000001 de 2021 y sus modificaciones). La integración se realiza a través de un proveedor tecnológico (PT) certificado que maneja la firma digital y la comunicación con la DIAN. Cada transacción de pago genera automáticamente un documento pre-validado que se valida en línea con la DIAN; si la validación es exitosa, el documento se entrega al correo del cliente de manera automática. Si el cliente no tiene correo registrado, se archiva en la zona pública de documentos para consulta. La plataforma también soporta la generación de facturas consolidateadas mensuales para clientes empresariales B2B, agrupando todas las transacciones del periodo en un solo documento tributario con detalle por vehículo y por sede.

### Notificaciones: SMS, push, email al entrar/salir/pagos

El sistema de notificaciones es multicanal y configurable por el usuario:

- **Notificación push (app móvil)**: Se envía inmediatamente al confirmar el pago y al abrir la talanquera de salida. Requiere que el usuario tenga la app instalada y haya aceptado notificaciones.

- **SMS**: Para usuarios sin smartphone o con preferencias de SMS, se envía un SMS al número registrado con el resumen de la transacción (placa, hora, valor). El costo del SMS se puede cargar al parqueadero o al usuario según el modelo de negocio.

- **Email**: Comprobante de pago en formato PDF adjunto, además de notificaciones de renovación de plan, alertas de saldo bajo en billetera, y ofertas de fidelización. El email se procesa en cola asíncrona para no bloquear el flujo de pago.

Las plantillas de notificación son editables por el administrador y soportan variables dinámicas como {{nombre_cliente}}, {{placa}}, {{valor}}, {{fecha}}, {{nombre_sede}}.

### Descuentos, cupones, programas de lealtad

La plataforma incluye un motor de promociones flexible que permite crear:

- **Descuentos porcentuales o en valor fijo**: Aplicables por periodo, por sede, por tipo de vehículo, o por método de pago.

- **Cupones canjeables**: Generados por el administrador para campañas específicas (descuento del 20% en inauguration de sede, etc.). El usuario ingresa el código del cupón en la app o en el totem antes de pagar.

- **Programa de lealtad**: Por cada $10.000 COP facturados, el usuario acumula 1 punto. Cada 100 puntos equivalen a $5.000 COP de descuento canjeable en el siguiente parqueo. El sistema calcula y muestra el saldo de puntos en la app y en el dashboard del cliente.

- **Descuentos por volumen (B2B)**: Para empresas con planes de flota, se configuran descuentos por número de vehículos registrados o por volumen mensual de Usage.

### Gestión de morosos (bloqueo de placas)

El módulo CRM mantiene una lista de vehículos bloqueados actualizada en tiempo real. Un vehículo se bloquea cuando: tiene facturas pendientes de pago vencidas mayor a 30 días, fue reportado como smm, o el administrador lo marcó manualmente por decisión comercial. Cuando un vehículo bloqueado intenta ingresar, el sistema muestra una alerta en el dashboard del operador con los motivos del bloqueo. El operador puede decidir si permite el ingreso con acuerdo de pago o si niega el acceso. En la salida, si el vehículo está bloqueado, la talanquera no se abre automáticamente y el sistema transfiere la gestión al operador. La plataforma también soporta el bloqueo temporal (por ejemplo, mientras el usuario realiza un pago pendiente vía transferencia) que se libera automáticamente 15 minutos después de confirmar el pago.

---

## 4. Módulo de Control de Talanquera (IoT)

### Tipos de talanquera: barrera vehicular, pivotante, semicircular

La plataforma es agnóstica respecto al fabricante de la talanquera y soporta los tres tipos más comunes en el mercado colombiano:

- **Barrera vehicular (boom barrier)**: Es el tipo más utilizado en parqueaderos. Consiste en una barra horizontal de 3 a 6 metros de largo que gira sobre un eje vertical para permitir o bloquear el paso. Se clasifica additionally según velocidad: estándar (3-6 segundos de apertura), rápida (1-3 segundos), y ultra-rápida (<1 segundo para plazas de alto tráfico). Las barreras se fabrican en acero galvanizado con capa de pintura electroestática, y la barra puede incluir luces LED de señalización y banda reflectiva para visibilidad nocturna.

- **Talanquera pivotante (swing barrier)**: Compuesta por dos hojas que se abren lateralmente pivotando sobre un eje vertical. Se utiliza en zonas donde se requiere un paso peatonal simultáneo al vehicular, o donde el espacio para la oscilación de una barrera no está disponible. Común en estacionamientos de oficinas corporativas.

- **Talanquera semicircular (folding barrier)**: La barra se pliega sobre sí misma en lugar de girar completamente, ocupando menos espacio longitudinal. Ideal para rampas y accesos con pendiente donde la apertura completa de una barrera convencional interferiría con el tráfico adyacente.

### Comunicación: GPIO, relay, RS485, MQTT

La comunicación entre el software de gestión y el hardware de la talanquera se realiza a través de múltiples protocolos según la arquitectura de cada sede:

- **GPIO (General Purpose Input/Output)**: Para sedes con controladores locales (Arduino, Raspberry Pi, o PLC compacto), la plataforma puede enviar señales digitales de 3.3V o 5V directamente a través de un pin GPIO para activar la apertura. Es la opción de menor costo para instalaciones pequeñas.

- **Relay (rele)**: El método más común. El sistema envía una señal a un módulo de relés que funciona como interruptor electrónico, cerrando el circuito de apertura de la talanquera. Se utiliza un relay de estado sólido (SSR) para evitar desgaste mecánico. El relay se acciona con un pulso de 500 ms.

- **RS485 (Serial)**: Para instalaciones que requieren mayor robustez y distancia (hasta 1.200 metros), la comunicación se realiza por bus RS485 con protocolo Modbus RTU. El gateway IoT funciona como master Modbus y envía comandos de apertura/cierre a los nodos de talanquera.

- **MQTT**: Para arquitectura basada en IoT, la plataforma publica mensajes en topics MQTT (por ejemplo, `sede/{id}/talanquera/{id}/comando` con payload `{"accion":"abrir","placa":"ABC123"}`). Un suscriptor en el controlador de la talanquera recibe el mensaje y ejecuta la acción. MQTT sobre TLS es el método preferido para integraciones en la nube por su ligereza y soporte de QoS.

### Protocolos: apertura por placa validada, apertura manual por operador, apertura de emergencia

La talanquera responde a tres tipos de comando:

- **Apertura por placa validada**: Es el flujo automático. Cuando el módulo ANPR valida una placa con pago confirmado o plan activo, envía el comando de apertura al módulo de talanquera. El sistema registra en el log: placa, timestamp, resultado (éxito/fallo), y tiempo de respuesta de la barrera.

- **Apertura manual por operador**: El operador puede abrir la talanquera desde el dashboard web, la app móvil, o el totem de pago, sin necesidad de validación de placa. Se utiliza para vehículos especiales (dueños del parqueadero, emergencias, vehículos con placa ilegible). Toda apertura manual queda registrada con el ID del operador que la autorizó y el motivo seleccionado de una lista predefinida (mantenimiento, emergencia, visitante VIP, otro).

- **Apertura de emergencia**: En caso de evacuación, falla de sistema, o emergencia médica, un botón físico de emergencia wired directamente al circuito de la talanquera abre la barrera instantáneamente, independientemente del software. Esta apertura de emergencia se registra con timestamp en el log y genera una alerta al supervisor.

### Flujo: pago confirmado → señal a PLC/relé → levanta talanquera → log de evento

El flujo completo de apertura automática es el siguiente:

1. El módulo CRM confirma el pago de la placa "XYZ123".
2. El servicio de validación envía un mensaje al broker MQTT con topic `talanquera/cmd` y payload `{"placa":"XYZ123","sede":1,"accion":"abrir_entrada"}`.
3. El gateway edge recibe el mensaje, valida que la placa corresponde a un evento activo en la sede, y envía la señal al relay (cierre de contacto por 500 ms).
4. El relay activa el mecanismo de apertura de la talanquera.
5. Un sensor de posición (microswitch o encoder) detecta que la barrera se abrió completamente y envía una señal de confirmación al gateway.
6. El gateway publica el evento de confirmación en el topic `talanquera/evt` con payload `{"placa":"XYZ123","estado":"abierta","timestamp":"2026-05-07T23:45:00Z"}`.
7. El backend recibe el evento, lo registra en la base de datos como "talanquera abierta" con duración del ciclo de apertura, y actualiza el dashboard en tiempo real.
8. Transcurridos 5 segundos (configurable) sin que el sensor detecte el paso del vehículo, el sistema envía el comando de cierre.

### Tiempos de apertura: objetivo <1 segundo

El SLA para el tiempo total de apertura de la talanquera (desde la recepción del comando hasta que la barrera está completamente levantada) es de menos de 1 segundo para barreras rápidas y menos de 3 segundos para barreras estándar. Este tiempo se mide y se registra en cada evento de apertura. Si el tiempo excede el umbral, se genera una alerta de mantenimiento preventivo. La plataforma acumula estadísticas de tiempo de apertura por talanquera y por día, permitiendo identificar tendencias de degradación mecánica antes de que se presente una falla.

### Fail-safe: qué pasa si falla el sistema

El diseño fail-safe garantiza que ninguna falla de software deje la talanquera en un estado inseguro:

- **Falla del software**: Si el sistema de gestión deja de enviar señales de control, la talanquera permanece en su último estado conocido (cerrada por defecto). No hay apertura automática sin instrucción explícita.

- **Falla del relay/controlador**: Un watchdog de hardware verifica cada 5 segundos que el controlador esté respondiendo. Si no hay respuesta, el controlador abre la talanquera por defecto para evitar vehículos atrapados.

- **Batería de respaldo (UPS)**: Cada controlador de talanquera cuenta con un UPS local que mantiene la operación durante cortes de energía por hasta 4 horas. El sistema envía alerta cuando el UPS activa y cuando el nivel de batería baja del 20%.

- **Botón físico de apertura manual**: Un botón en la cabina del operador, conectado directamente al circuito de la talanquera, permite la apertura manual en cualquier circumstance. Es obligatorio según la normatividad colombiana de parqueaderos.

- **Falla del sensor de posición**: Si el sistema no recibe confirmación de que la barrera se abrió (timeout de 5 segundos), cierra el circuito de retorno y genera una alerta de falla mecánica para revisión in situ.

### Monitoreo de estado (abierta/cerrada/error) en tiempo real

El dashboard muestra el estado actual de cada talanquera de cada sede con un indicador visual de color: verde para "abierta", rojo para "cerrada", y naranja con animación para "en movimiento". Si la talanquera está en estado de error (sensor defectuoso, barrera atascada, UPS activo), el indicador cambia a rojo con un ícono de alerta y aparece en la sección de alertas activas del dashboard. Cada cambio de estado se registra en el log con timestamp, placa asociada (si la hay), tipo de comando (automático, manual, emergencia), y resultado. El historial de estados es consultable para auditorías y para generación de reportes de disponibilidad (MTBF, MTTR) por talanquera.

### Integración con CCTV para grabación de eventos

Cada evento de apertura y cierre de talanquera genera automáticamente un clip de vídeo de 10 segundos (5 segundos antes y 5 segundos después del evento) extraído del sistema de CCTV de la sede. Los clips se almacenan en el NVR local con overwrite policy de 30 días y se indexan en la plataforma con metadatos: sede, talanquera, placa, timestamp, tipo de evento. El operador puede acceder a los clips directamente desde el dashboard haciendo clic en el evento, sin necesidad de abrir el software del NVR por separado. Para sedes donde el NVR no tiene capacidad de generar clips automatizados, la plataforma proporciona un API para que el NVR consulte los eventos y genere los clips de manera programada. Los clips están protegidos contra eliminación por 30 días y requieren autorización de un administrador para ser eliminados antes de ese periodo.

---

## 5. Dashboard BI y Reportes

### KPIs operativos: ocupación %, ingresos por hora, tiempo promedio de estadía

El módulo de Business Intelligence proporciona un panel de control executive con los indicadores clave de rendimiento (KPIs) más relevantes para la operación de parqueaderos:

- **Ocupación (%)**: Porcentaje de espacios ocupados sobre el total disponible, actualizado en tiempo real y como promedio ponderado por hora. Se presenta como serie temporal con línea de tendencia.

- **Ingresos por hora**: Valor total facturado en cada hora del día, con comparativa frente al mismo día de la semana anterior y frente al promedio del mes. Este KPI permite identificar horarios de máxima generación de ingresos.

- **Tiempo promedio de estadía**: Duración media de estacionamiento de los vehículos que egresaron en el periodo seleccionado, desglosado por tipo de vehículo (carro, moto, bicicleta) y por zona del parqueadero. Un tiempo promedio alto puede indicar subutilización o, por el contrario, un parqueadero con clientela de larga estadía.

- **Vehículos diarios**: Total de ingresos y egresos por día, con distinción de第一次 visitantes versus clientes recurrentes.

- **Ticket promedio**: Valor promedio por transacción, útil para entender el mix de planes (por minuto vs. mensual) y la efectividad de las promociones.

- **Tasa de conversión de pago**: Porcentaje de transacciones completadas versus abandonadas (vehículos que salieron sin pagar, identificadas por el conteo de talanquera).

### Reportes diarios/semanales/mensuales por sede y consolidados por red

La plataforma genera reportes automatizados en tres niveles de agregación temporal y dos niveles de geografía:

- **Por sede**: Reportes detallados para cada parqueadero individual, incluyendo todos los KPIs desglosados por hora, turno, y zona. Generados en formato PDF y enviados por email al administrador de sede al final de cada día.

- **Por red**: Reportes consolidados que agregan datos de todas las sedes de la red, permitiendo comparativas de desempeño entre ubicaciones, identificación de la sede con mayor ocupación, y suma total de ingresos de la red. Ideales para la dirección executive.

- **Programación de reportes**: El administrador programa la frecuencia de cada reporte (diaria, semanal, mensual) y la lista de destinatarios. Los reportes se generan automáticamente los días y horas configurados y se entregan en la bandeja de entrada del portal web o por email en formato PDF y Excel simultáneamente.

### Alertas en tiempo real

El sistema de alertas opera como un flujo continuo de notificaciones que aparecen en el panel lateral del dashboard sin necesidad de refrescar la página. Las alertas se clasifican en cuatro niveles de severidad:

- **INFO**: Informativa, no requiere acción inmediata (ej: "Sede Centro ha alcanzado 80% de ocupación").

- **WARNING**: Requiere atención del operador (ej: "Talanquera de entrada #2 tarda 4 segundos en abrir — acima del umbral").

- **ERROR**: Falla que afecta la operación (ej: "Sensor de zona C-12 sin conexión — modo manual activo").

- **CRITICAL**: Falla sistémica que requiere intervención inmediata (ej: "Pérdida de conexión con sede Norte — modo offline activo desde hace 15 minutos").

Cada alerta incluye descripción, sede afectada, timestamp, y acciones sugeridas. El operador puede hacer clic en "Ver detalle" para navegar directamente al componente afectado. Las alertas se pueden configurar también para envío por email y SMS a destinatarios específicos según nivel de severidad.

### Exportación a Excel/CSV y conexión a Power BI/Google Data Studio

Todos los datos visibles en los dashboards y reportes son exportables en los siguientes formatos:

- **Excel (.xlsx)**: Exportación con formato condicional, columnas auto-ajustadas, y sheets separados para cada vista del reporte. Disponible para cualquier tabla o gráfico del dashboard.

- **CSV**: Exportación plana de datos crudos sin formato, ideal para procesamiento adicional en Python, R, o herramientas de analytics. El delimiter y el encoding (UTF-8) son configurables.

- **API REST de datos**: La plataforma expone un API RESTful documentado en Swagger/OpenAPI que permite a cualquier herramienta de BI conectarse directamente a los datos. El API soporta autenticación con API key y OAuth 2.0, y ofrece endpoints para cada entidad (ocupación, transacciones, ingresos, alertas, vehículos).

- **Conector nativo para Power BI**: Plantilla de Power BI (.pbit) disponible para descarga que incluye un modelo de datosstar schemaoptimizado paraレポート y visualizaciones preconfiguradas (mapas de ocupación, gráficos de ingresos, KPIs de ocupación).

- **Conector para Google Data Studio (Looker Studio)**: Plantilla de Data Studio con gráficos y tablas preconfigurados, conectada al API REST de la plataforma para actualización en tiempo real. El usuario puede clonar la plantilla y personalizarla con sus propias métricas y filtros.
