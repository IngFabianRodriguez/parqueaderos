# Documentación Técnica — ParkCore

> Plataforma centralizada de gestión para redes de parqueaderos. ANPR · CRM · Pagos · Control de talanqueras IoT · Dashboard BI · App móvil.

---

## Índice General

### [00-general](./00-general/)
| Documento | Descripción |
|-----------|-------------|
| [README](./00-general/README.md) | Visión general del proyecto, stack tecnológico, navegación de la documentación |
| [roadmap](./00-general/roadmap.md) | Roadmap de producto: 4 fases (MVP → Escalamiento), backlog por definir |
| [changelog](./00-general/changelog.md) | Historial de versiones (SemVer) y política de mantenimiento |

### [01-requisitos](./01-requisitos/)
| Documento | Descripción |
|-----------|-------------|
| [historias-usuario](./01-requisitos/historias-usuario.md) | 12 user stories con criterios de aceptación (Given/When/Then) |
| [funcionales](./01-requisitos/funcionales.md) | 20 requerimientos funcionales (RF-001 a RF-020) por módulo |
| [no-funcionales](./01-requisitos/no-funcionales.md) | Requisitos de rendimiento, SLA, escalabilidad, seguridad, compatibilidad |

### [02-arquitectura](./02-arquitectura/)
| Documento | Descripción |
|-----------|-------------|
| [decisiones-tecnicas](./02-arquitectura/decisiones-tecnicas.md) | 8 ADRs (Architecture Decision Records) |
| [modelo-datos](./02-arquitectura/modelo-datos.md) | 14 entidades, diccionario de datos, índices y particionamiento |
| [seguridad](./02-arquitectura/seguridad.md) | Auth JWT, RBAC (5 roles), cifrado, auditoría, rate limiting, compliance |
| [diagramas-uml](./02-arquitectura/diagramas-uml/) | 9 diagramas Mermaid (código fuente) |

#### Diagramas UML (Mermaid)
| # | Archivo | Tipo | Descripción |
|---|---------|------|-------------|
| 1 | [01-casos-uso.mermaid](./02-arquitectura/diagramas-uml/01-casos-uso.mermaid) | Casos de uso | 5 actores, 12 UC |
| 2 | [02-clases.mermaid](./02-arquitectura/diagramas-uml/02-clases.mermaid) | Clases | 13 clases con atributos, métodos y relaciones |
| 3 | [03-objetos.mermaid](./02-arquitectura/diagramas-uml/03-objetos.mermaid) | Objetos | Escenario concreto de instancias |
| 4 | [04-componentes.mermaid](./02-arquitectura/diagramas-uml/04-componentes.mermaid) | Componentes | Arquitectura por capas |
| 5 | [05-despliegue.mermaid](./02-arquitectura/diagramas-uml/05-despliegue.mermaid) | Despliegue | Infraestructura y nodos |
| 6 | [06-secuencia.mermaid](./02-arquitectura/diagramas-uml/06-secuencia.mermaid) | Secuencia | Flujo entrada → pago → salida |
| 7 | [07-actividades.mermaid](./02-arquitectura/diagramas-uml/07-actividades.mermaid) | Actividades | Flujo completo de proceso |
| 8 | [08-estados.mermaid](./02-arquitectura/diagramas-uml/08-estados.mermaid) | Estados | Ciclo de vida del vehículo |
| 9 | [09-temporal.mermaid](./02-arquitectura/diagramas-uml/09-temporal.mermaid) | Timing | Timing de apertura de talanquera |

### [03-desarrollo](./03-desarrollo/)
| Documento | Descripción |
|-----------|-------------|
| [setup](./03-desarrollo/setup.md) | Guía de instalación local, dependencias, Docker Compose, verificación |
| [estandares](./03-desarrollo/estandares.md) | Convenciones de código, nomenclatura, Conventional Commits, CI |
| [api-reference](./03-desarrollo/api-reference.md) | Referencia completa de APIs REST y WebSocket (9 módulos) |

### [04-qa-testing](./04-qa-testing/)
| Documento | Descripción |
|-----------|-------------|
| [plan-pruebas](./04-qa-testing/plan-pruebas.md) | Estrategia de testing: pirámide, frameworks, cobertura 80%, CI/CD |
| [casos-prueba](./04-qa-testing/casos-prueba.md) | 16 casos de prueba (CP001–CP016) con priorización |

### [05-manuales](./05-manuales/)
| Documento | Descripción |
|-----------|-------------|
| [usuario-final](./05-manuales/usuario-final.md) | Manual para conductores: registro, consulta, pago, salida, FAQ |
| [operaciones](./05-manuales/operaciones.md) | Manual DevOps/SRE: monitoreo, logs, backups, incidentes, health checks |

---

## Documentos de Negocio (docs/ raíz previa)

Estos documentos complementan la documentación técnica con la visión de producto, mercado y monetización.

| Documento | Descripción |
|-----------|-------------|
| [01-resumen-ejecutivo](./01-resumen-ejecutivo.md) | Visión de producto, diagnóstico de mercado, Business Model Canvas |
| [02-modulos-funcionales](./02-modulos-funcionales.md) | Especificación funcional detallada: Disponibilidad, ANPR, CRM, Talanquera, BI |
| [03-arquitectura-tecnica](./03-arquitectura-tecnica.md) | Arquitectura de sistema, stack, modelo de datos, seguridad, integraciones |
| [04-monetizacion-roi](./04-monetizacion-roi.md) | Modelo de monetización, ROI, plan por fases, comparativa competitiva |
| [05-riesgos-compliance](./05-riesgos-compliance.md) | Análisis de riesgos, marco regulatorio, conclusiones |

---

## Estado del Proyecto

| Fase | Estado | Descripción |
|------|--------|-------------|
| Fase 0 MVP | 🟡 En desarrollo | Documentación técnica completa ✓, desarrollo por iniciar |
| Fase 1 V1 | ⬜ Por iniciar | Multi-sede, dashboard, app operador, CRM básico |
| Fase 2 V2 | ⬜ Por iniciar | B2B, facturación DIAN, BI avanzado, APIs abiertas |
| Fase 3 Escalamiento | ⬜ Por definir | Multi-ciudad, ML, dynamic pricing |

## Tecnologías Identificadas

| Capa | Tecnología |
|------|-----------|
| Backend API | Python / FastAPI |
| Frontend | React / Angular + PrimeNG |
| Base de datos | PostgreSQL + TimescaleDB |
| Caché / Real-time | Redis |
| Mensajería IoT | MQTT (RabbitMQ / Mosquitto) |
| ANPR | Plate Recognizer API (o OpenALPR) |
| Despliegue | Docker + Kubernetes |
| Notificaciones | Firebase Cloud Messaging / Twilio |
| Pagos | Wompi / ePayco / Stripe |

---

*Última actualización: Mayo 2026 — Proyecto en fase de documentación técnica MVP*
