# Changelog

## Introducción

Este documento registra todos los cambios significativos realizados en el proyecto ParkCore a lo largo de su ciclo de vida, organizados por versión siguiendo el formato [Semantic Versioning (SemVer)](https://semver.org/). Cada entrada de versión incluye la fecha de publicación, el tipo de cambio y una descripción de las modificaciones, adiciones o correcciones realizadas.

El objetivo de mantener este changelog es proporcionar un historial completo y rastreable del evolución del proyecto, que permita a los miembros del equipo, stakeholders e integradores entender qué cambió entre versiones, qué se agregó, qué se depreció y qué problemas fueron resueltos.

**Convenciones de formato:**
- Cada versión incluye: número de versión, fecha y lista de cambios
- Los tipos de cambios se clasifican en: `Added` (nuevo), `Changed` (cambio), `Deprecated` (deprecado), `Removed` (eliminado), `Fixed` (corrección), `Security` (seguridad)
- Los cambios se ordenan del más reciente al más antiguo
- Se usa el formato `YYYY-MM-DD` para las fechas

---

## Formato de tabla de versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| [0.1.0](#010---mes-1) | Mes 1 | Esqueleto del proyecto, estructura de carpetas docs/ con business proposal |
| [0.0.1](#001---inicial) | Inicial | Documentación Business Proposal (5 secciones: resumen ejecutivo, módulos funcionales, arquitectura técnica, monetización/ROI, riesgos/compliance) |

---

## 0.1.0 - Mes 1

**Fecha:** Mes 1 del proyecto (en desarrollo)  
**Tipo de release:** Minor release — Evolución del MVP  
**Estado:** ⏳ En desarrollo

### Cambios realizados

#### Added — Nuevas funcionalidades y módulos

- **Estructura de carpetas del proyecto:** Creación de la organización completa de directorios del proyecto bajo la raíz `parqueaderos/`, incluyendo la carpeta `docs/` con subcarpetas por sección temática (`00-general/`, `01-resumen-ejecutivo/`, `02-modulos-funcionales/`, `03-arquitectura-tecnica/`, `04-monetizacion-roi/`, `05-riesgos-compliance/`). Esta estructura sigue una convención de numeración que permite mantener un orden lógico de lectura de la documentación.

- **Documentación del Business Proposal existente:** La documentación inicial del Business Proposal (versión 0.0.1) ha sido integrada dentro de la estructura de carpetas, garantizando que los cinco documentos existentes permanezcan accesibles y formen parte del set de documentación base del proyecto.

- **Carpeta `00-general/` creada:** Se ha creado el directorio que albergará la documentación general del proyecto —README, roadmap, changelog y licencia— proporcionando un punto de entrada natural para cualquier persona nueva en el proyecto.

- **Archivo README.md:** Documento de visión general del proyecto que describe qué es ParkCore, para quién está diseñado, qué problemas resuelve, cuál es el stack tecnológico tentativo y cómo navegar la documentación. Este archivo sirve como portada lógica de toda la documentación.

- **Archivo roadmap.md:** Hoja de ruta completa del proyecto dividida en cuatro fases principales (MVP, V1, V2, Escalamiento) más un backlog de funcionalidades por definir. Incluye objetivos, alcance, entregables y fechas estimadas para cada fase.

- **Archivo changelog.md:** Este documento, que registra el historial de cambios del proyecto desde su origen y establece las convenciones de versionado SemVer que rigirán el desarrollo.

### Notas de la versión 0.1.0

Esta versión marca la transición de una colección de documentos de propuesta de negocio a un proyecto con estructura formal de documentación y una hoja de ruta definida. Los cambios introducidos en esta versión son principalmente organizativos y de documentación; no se ha modificado aún ningún código fuente ni se han tomado decisiones técnicas irreversibles.

El hecho de que esta versión sea la primera en incluir un changelog formal significa que las versiones anteriores (0.0.x) se consideran protodocumentación interna. A partir de la versión 0.1.0, todo cambio significativo en el proyecto (código, documentación, arquitectura) debe reflejarse en este changelog siguiendo el formato descrito.

---

## 0.0.1 - Inicial

**Fecha:** Documentación inicial del proyecto  
**Tipo de release:** Initial release — Genesis del proyecto  
**Estado:** ✅ Completado

### Descripción

Versión inicial del proyecto ParkCore, correspondiente a la elaboración completa del **Business Proposal** o Propuesta de Negocio. Esta versión constituye el punto de partida del proyecto y contiene toda la documentación fundacional sobre la que se construirán las fases posteriores de desarrollo.

### Documentación del Business Proposal

El Business Proposal de ParkCore fue estructurado en cinco secciones principales, cada una abordando un aspecto crítico del proyecto:

#### Sección 1: Resumen Ejecutivo

Documento que presenta de manera concisa la propuesta de valor de ParkCore, el problema que resuelve, la solución propuesta, el modelo de negocio, las proyecciones financieras resumidas y el equipo requerido. Esta sección está diseñada para que un lector ejecutivo pueda entender en menos de cinco minutos de qué se trata el proyecto y por qué vale la pena invertir tiempo y recursos en él.

#### Sección 2: Módulos Funcionales

Descripción detallada de cada uno de los módulos que compone la plataforma:
- **Módulo de disponibilidad en tiempo real:** Sistema de conteo y publicación de espacios disponibles por sede.
- **Módulo ANPR:** Motor de reconocimiento automático de placas vehiculares mediante visión artificial.
- **Módulo de pagos y cobros (CRM):** Gestión integral de tarifas, clientes, transacciones y facturación.
- **Módulo de control de talanquera (IoT):** Comunicación con relés y barreras físicas para apertura/cierre automatizado.
- **Módulo de Dashboard BI:** Panel de visualización de métricas operativas y financieras.
- **Módulos de aplicaciones:** App para operador en sitio y app para cliente final.

Cada módulo incluye descripción funcional, flujos de usuario, datos de entrada/salida y dependencias con otros módulos.

#### Sección 3: Arquitectura Técnica

Visión general de la arquitectura del sistema, incluyendo:
- Diagrama de componentes de alto nivel
- Selección tentativa de tecnologías por capa (backend, frontend, base de datos, IoT, ANPR)
- Consideraciones de escalabilidad, disponibilidad y seguridad
- Modelo de datos conceptual
- Integraciones externas previstas

#### Sección 4: Monetización y ROI

Análisis del modelo de monetización propuesto para ParkCore:
- **Modelo SaaS por sede:** Suscripción mensual fija por sede conectada a la plataforma.
- **Modelo por transacción:** Tarifa variable por cada transacción procesada.
- **Modelo híbrido:** Combinación de suscripción fija más variable por volumen.
- **Modelo B2B por flota:** Facturación consolidada mensual a empresas con vehículos en la plataforma.
- Proyecciones de ingresos a 3 años basadas en supuestos de adopción.
- Análisis de punto de equilibrio y retorno de inversión.
- Comparativa de pricing con soluciones existentes en el mercado.

#### Sección 5: Riesgos y Compliance

Identificación y análisis de los principales riesgos del proyecto:
- **Riesgos técnicos:** Falla de integración ANPR, latencia en apertura de talanquera, escalabilidad de la plataforma.
- **Riesgos de negocio:** Adopción lenta, competencia de incumbentes, regulación de parqueaderos.
- **Riesgos legales:** Legislación de protección de datos, regulaciones de tránsito, responsabilidad civil.
- **Riesgos financieros:** Dependencia de inversión inicial, burn rate, time-to-revenue.
- Plan de mitigación para cada riesgo identificado.
- Consideraciones de compliance: RGPD (protección de datos), norms PCI-DSS (si se procesan pagos con tarjeta), regulaciones locales de vigilancia.

### Notas de la versión 0.0.1

La versión 0.0.1 representa la documentación fundacional del proyecto. Fue elaborada sin haber escrito una sola línea de código, lo cual es intencional: el objetivo fue primero validar la coherencia del modelo de negocio, la viabilidad de los módulos funcionales y la solidez del análisis financiero antes de invertir recursos en desarrollo técnico.

Esta versión ha sido superada en términos de documentación por la versión 0.1.0, pero permanece como referencia histórica del origen del proyecto y como base sobre la cual se construyó toda la planificación posterior. Los documentos originales del Business Proposal siguen disponibles en las carpetas correspondientes (`01-resumen-ejecutivo/` a `05-riesgos-compliance/`).

---

## Política de versionado

### Semantic Versioning (SemVer)

ParkCore utiliza **Semantic Versioning** como convención de versionado oficial. El formato de versión es:

```
MAJOR.MINOR.PATCH
```

Donde:
- **MAJOR** (mayor): Incrementa cuando hay cambios incompatibles en la API pública, cambios arquitecturales que rompen compatibilidad hacia atrás, o removido definitivo de funcionalidadesDeprecated.
- **MINOR** (menor): Incrementa cuando se añaden funcionalidades de manera backwards-compatible, o cuando se añade funcionalidad pública que ha sido previously Deprecated.
- **PATCH** (parche): Incrementa cuando se corrigen errores de manera backwards-compatible.

### Ramas y releases

- La rama principal `main` contiene siempre el código y documentación de la última versión estable.
- Las ramas `feature/*` se crean para desarrollar nuevas funcionalidades que eventualente harán merge a `main`.
- Las ramas `hotfix/*` se utilizan para correcciones urgentes en producción que requieren un patch inmediato.
- Cada release formal genera un tag en Git con el número de versión.

### Changelog por milestone

Este changelog se actualiza **por milestone**. Cada vez que se completa una fase del roadmap (MVP, V1, V2, Escalamiento) o se libera una versión stable del software, se debe agregar una entrada en este documento documentando todos los cambios desde la última versión releaseada.

**Formato obligatorio para cada entrada:**
```markdown
## X.Y.Z - Fecha

### Added
- Descripción de la nueva funcionalidad

### Changed
- Descripción del cambio en funcionalidad existente

### Deprecated
- Funcionalidad que será removida en futuras versiones

### Removed
- Funcionalidad removida definitivamente

### Fixed
- Corrección de error

### Security
- Actualización de seguridad
```

---

*Este changelog es mantenido por el equipo de desarrollo de ParkCore. Para reportar errores o sugerir cambios a este documento, usar el sistema de issues del proyecto.*
