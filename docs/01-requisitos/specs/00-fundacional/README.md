# SPECS Fundacionales — Índice Maestro

> **Propósito**: Este directorio (`00-fundacional/`) contiene los specs de los **componentes arquitectónicos fundamentales** sobre los cuales se construyen los 180 requerimientos funcionales (RF-001 a RF-180).

---

## Qué son los specs fundacionales

Cada **COMP-###** es un documento de diseño de un componente del sistema. Define:

- **Qué es** el componente y por qué existe
- **Cómo se comunica** (API, eventos, consumers)
- **Qué datos gestiona** (modelo de datos)
- **Cómo se despliega** y monitorea
- **Qué puede fallar** y cómo se maneja

Los RFs (requerimientos funcionales) dependen de estos componentes — son la capa que "hace" el requerimiento.

---

## Catálogo de Componentes Fundacionales

| # | Componente | Tipo | Puerto/Path | Descripción |
|---|-----------|------|-------------|-------------|
| COMP-001 | API Gateway | Infraestructura | / | Kong + Lua: auth, routing, rate limit |
| COMP-002 | Auth Service | Microservicio | 8001 | JWT, sessions, MFA, RBAC |
| COMP-003 | PostgreSQL | Base de datos | — | RDBMS principal por schema |
| COMP-004 | Kafka | Message broker | 9092 | Event bus (topics definidos) |
| COMP-005 | Redis | Cache / Sesiones | 6379 | Rate limiting, sesiones, queue |
| COMP-006 | S3 Object Storage | Storage | — | Imágenes, archivos, logs |
| COMP-007 | Observability Stack | Monitoring | — | Prometheus + Grafana + Loki + Tempo |
| COMP-008 | Vault | Secrets | — | KV, PKI, Database dynamic creds |
| COMP-009 | Tenant Service | Microservicio | 8002 | CRUD tenants, planes, lifecycle |
| COMP-010 | Sedes Service | Microservicio | 8003 | Sedes, zonas, espacios, dispositivos |
| COMP-011 | IoT Service | Microservicio | 8004 | Talanqueras, sensores, MQTT |
| COMP-012 | Payments Service | Microservicio | 8005 | Pagos, billing, wallets |
| COMP-013 | ANPR Service | Microservicio | 8006 | OCR placas, fallback manual |
| COMP-014 | Notification Service | Microservicio | 8007 | Push, SMS, email, webhooks |
| COMP-015 | Reports Service | Microservicio | 8015 | Reportes, BI connectors |
| COMP-016 | Support Service | Microservicio | 8016 | Tickets, chat, SLA, NPS |
| COMP-017 | Billing Service | Microservicio | 8017 | Tarifas, DIAN, morosos |
| COMP-018 | Monitoring Service | Microservicio | 8018 | Health checks, uptime |
| COMP-019 | Mobile Apps | App | — | Operator App + Client App |
| COMP-020 | Admin Panel | Web app | — | Angular 21 + PrimeNG |
| COMP-021 | Kafka Topics + Schemas | Mensajería | — | Catálogo de eventos |
| COMP-022 | CI/CD + IaC | DevOps | — | GitHub Actions + Terraform + Helm |

---

## Mapa: RFs → Componentes

### Grupo 1: Disponibilidad y Gestión de Sedes (RF-001 a RF-004)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-001 | COMP-010 (Sedes Service) | COMP-001 (Gateway), COMP-003 (PostgreSQL) |
| RF-002 | COMP-010 (Sedes Service) | COMP-003 (PostgreSQL) |
| RF-003 | COMP-010 (Sedes Service) | COMP-003 (PostgreSQL) |
| RF-004 | COMP-010 (Sedes Service) | COMP-003 (PostgreSQL) |

### Grupo 2: ANPR (RF-005 a RF-009)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-005 | COMP-013 (ANPR Service) | COMP-011 (IoT Service), COMP-006 (S3), COMP-004 (Kafka) |
| RF-006 | COMP-013 (ANPR Service) | COMP-012 (Payments), COMP-010 (Sedes) |
| RF-007 | COMP-013 (ANPR Service) | COMP-019 (Mobile Apps - Operator) |
| RF-008 | COMP-013 (ANPR Service) | COMP-004 (Kafka), COMP-005 (Redis) |
| RF-009 | COMP-013 (ANPR Service) | COMP-006 (S3), COMP-002 (Auth) |

### Grupo 3: CRM y Pagos (RF-010 a RF-017)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-010 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-002 (Auth) |
| RF-011 | COMP-012 (Payments Service) | COMP-003 (PostgreSQL), COMP-004 (Kafka) |
| RF-012 | COMP-017 (Billing Service) | COMP-006 (S3), COMP-003 (PostgreSQL) |
| RF-013 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-007 (Observability) |
| RF-014 | COMP-014 (Notification Service) | COMP-004 (Kafka), COMP-005 (Redis) |
| RF-015 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-004 (Kafka) |
| RF-016 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-012 (Payments) |
| RF-017 | COMP-012 (Payments Service) | COMP-003 (PostgreSQL), COMP-005 (Redis) |

### Grupo 4: Talanquera IoT (RF-018 a RF-022)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-018 | COMP-011 (IoT Service) | COMP-004 (Kafka), COMP-012 (Payments) |
| RF-019 | COMP-011 (IoT Service) | COMP-002 (Auth), COMP-021 (Kafka) |
| RF-020 | COMP-011 (IoT Service) | COMP-018 (Monitoring Service), COMP-004 (Kafka) |
| RF-021 | COMP-011 (IoT Service) | COMP-021 (Kafka), COMP-018 (Monitoring) |
| RF-022 | COMP-011 (IoT Service) | COMP-014 (Notification), COMP-018 (Monitoring) |

### Grupo 5: BI y Reportes (RF-023 a RF-025)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-023 | COMP-015 (Reports Service) | COMP-003 (PostgreSQL), COMP-007 (Observability) |
| RF-024 | COMP-015 (Reports Service) | COMP-006 (S3), COMP-022 (CI/CD) |
| RF-025 | COMP-015 (Reports Service) | COMP-009 (Tenant Service), COMP-003 (PostgreSQL) |

### Grupo 6: Seguridad y Acceso (RF-026 a RF-028)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-026 | COMP-002 (Auth Service) | COMP-001 (Gateway), COMP-003 (PostgreSQL) |
| RF-027 | COMP-002 (Auth Service) | COMP-008 (Vault), COMP-007 (Observability) |
| RF-028 | COMP-002 (Auth Service) | COMP-003 (PostgreSQL), COMP-001 (Gateway) |

### Grupo 7: SaaS Multi-Tenant (RF-029 a RF-082)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-029 a RF-036 | COMP-009 (Tenant Service) | COMP-002 (Auth), COMP-003 (PostgreSQL), COMP-004 (Kafka) |
| RF-037 a RF-045 | COMP-009 (Tenant Service) + COMP-012 (Payments) | COMP-004 (Kafka), COMP-003 (PostgreSQL), COMP-022 (CI/CD) |
| RF-046 a RF-050 | COMP-009 (Tenant Service) | COMP-020 (Admin Panel), COMP-019 (Mobile) |
| RF-051 a RF-055 | COMP-009 (Tenant Service) | COMP-001 (Gateway), COMP-003 (PostgreSQL), COMP-005 (Redis) |
| RF-056 a RF-058 | COMP-009 (Tenant Service) | COMP-002 (Auth), COMP-001 (Gateway) |
| RF-059 a RF-062 | COMP-009 (Tenant Service) | COMP-014 (Notification), COMP-019 (Mobile) |
| RF-063 a RF-066 | COMP-009 (Tenant Service) | COMP-004 (Kafka), COMP-007 (Observability) |
| RF-067 a RF-069 | COMP-002 (Auth Service) | COMP-008 (Vault), COMP-003 (PostgreSQL) |
| RF-070 a RF-074 | COMP-002 (Auth Service) | COMP-003 (PostgreSQL), COMP-009 (Tenant) |
| RF-075 a RF-078 | COMP-015 (Reports Service) | COMP-003 (PostgreSQL), COMP-007 (Observability) |
| RF-079 a RF-082 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-009 (Tenant) |

### Grupo 8: Configuración (RF-083 a RF-099)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-083 a RF-099 | COMP-009 (Tenant Service) | COMP-010 (Sedes), COMP-003 (PostgreSQL), COMP-020 (Admin Panel) |

### Grupo 9: Observabilidad (RF-100 a RF-115)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-100 a RF-105 | COMP-018 (Monitoring Service) | COMP-007 (Observability), COMP-003 (PostgreSQL) |
| RF-106 a RF-108 | COMP-018 (Monitoring Service) | COMP-014 (Notification), COMP-008 (Vault) |
| RF-109 a RF-111 | COMP-011 (IoT Service) | COMP-018 (Monitoring), COMP-004 (Kafka) |
| RF-112 a RF-113 | COMP-007 (Observability) | COMP-001 (Gateway), COMP-004 (Kafka) |
| RF-114 a RF-115 | COMP-018 (Monitoring Service) | COMP-007 (Observability), COMP-003 (PostgreSQL) |

### Grupo 10: Informes (RF-116 a RF-130)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-116 a RF-123 | COMP-015 (Reports Service) | COMP-003 (PostgreSQL), COMP-007 (Observability) |
| RF-124 a RF-125 | COMP-015 (Reports Service) | COMP-002 (Auth), COMP-017 (Billing) |
| RF-126 a RF-127 | COMP-015 (Reports Service) | COMP-017 (Billing), COMP-009 (Tenant) |
| RF-128 a RF-130 | COMP-015 (Reports Service) | COMP-006 (S3), COMP-014 (Notification), COMP-004 (Kafka) |

### Grupo 11: App Operador (RF-131 a RF-141)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-131 a RF-132 | COMP-019 (Mobile Apps) | COMP-010 (Sedes), COMP-001 (Gateway) |
| RF-133 a RF-135 | COMP-019 (Mobile Apps) | COMP-010 (Sedes), COMP-012 (Payments), COMP-003 (PostgreSQL) |
| RF-136 a RF-137 | COMP-019 (Mobile Apps) | COMP-011 (IoT Service), COMP-004 (Kafka), COMP-005 (Redis) |
| RF-138 a RF-139 | COMP-019 (Mobile Apps) | COMP-014 (Notification), COMP-018 (Monitoring) |
| RF-140 a RF-141 | COMP-019 (Mobile Apps) | COMP-017 (Billing), COMP-003 (PostgreSQL) |

### Grupo 12: App Cliente (RF-142 a RF-150)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-142 | COMP-019 (Mobile Apps) | COMP-010 (Sedes), COMP-001 (Gateway) |
| RF-143 a RF-144 | COMP-019 (Mobile Apps) | COMP-012 (Payments), COMP-004 (Kafka), COMP-014 (Notification) |
| RF-145 a RF-146 | COMP-019 (Mobile Apps) | COMP-017 (Billing), COMP-003 (PostgreSQL) |
| RF-147 a RF-148 | COMP-019 (Mobile Apps) | COMP-015 (Reports), COMP-017 (Billing), COMP-006 (S3) |
| RF-149 a RF-150 | COMP-019 (Mobile Apps) | COMP-014 (Notification), COMP-017 (Billing) |

### Grupo 13: Admin Panel (RF-151 a RF-168)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-151 a RF-153 | COMP-020 (Admin Panel) | COMP-002 (Auth), COMP-003 (PostgreSQL) |
| RF-154 a RF-156 | COMP-020 (Admin Panel) | COMP-009 (Tenant), COMP-012 (Payments) |
| RF-157 a RF-158 | COMP-020 (Admin Panel) | COMP-011 (IoT), COMP-018 (Monitoring) |
| RF-159 a RF-160 | COMP-020 (Admin Panel) | COMP-010 (Sedes), COMP-003 (PostgreSQL) |
| RF-161 a RF-163 | COMP-020 (Admin Panel) | COMP-017 (Billing), COMP-015 (Reports) |
| RF-164 a RF-165 | COMP-020 (Admin Panel) | COMP-014 (Notification), COMP-003 (PostgreSQL) |
| RF-166 | COMP-020 (Admin Panel) | COMP-018 (Monitoring), COMP-007 (Observability) |
| RF-167 a RF-168 | COMP-020 (Admin Panel) | COMP-002 (Auth), COMP-007 (Observability) |

### Grupo 14: Conciliación (RF-169 a RF-174)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-169 a RF-174 | COMP-017 (Billing Service) | COMP-003 (PostgreSQL), COMP-015 (Reports), COMP-002 (Auth) |

### Grupo 15: Soporte (RF-175 a RF-180)

| RF | Componentes principales | Componentes secundarios |
|----|----------------------|------------------------|
| RF-175 a RF-177 | COMP-016 (Support Service) | COMP-003 (PostgreSQL), COMP-014 (Notification) |
| RF-178 | COMP-016 (Support Service) | COMP-004 (Kafka), COMP-019 (Mobile Apps) |
| RF-179 a RF-180 | COMP-016 (Support Service) | COMP-015 (Reports), COMP-003 (PostgreSQL) |

---

## Resumen de Componentes por Servicio

| Componente | RFs que dependen de él | Count |
|------------|------------------------|-------|
| COMP-001 (API Gateway) | 001, 005, 026, 051, 131, 142 | 6 directas + todas indirectamente |
| COMP-002 (Auth Service) | 026-028, 029-036, 067-074, 141, 151, 168 | ~40 |
| COMP-003 (PostgreSQL) | Todos | 180 |
| COMP-004 (Kafka) | 005-009, 011-017, 021, 029-045, 100-115 | ~80 |
| COMP-005 (Redis) | 007-008, 014, 051-055, 131-137 | ~30 |
| COMP-006 (S3) | 005, 009, 012, 024, 128, 148 | 6 |
| COMP-007 (Observability) | 023-025, 027, 100-115, 167-168 | ~50 |
| COMP-008 (Vault) | 027, 067-069 | 5 |
| COMP-009 (Tenant Service) | 029-066, 083-099, 154-156, 167 | ~80 |
| COMP-010 (Sedes Service) | 001-004, 018, 131-132, 142, 159-160 | ~20 |
| COMP-011 (IoT Service) | 005, 018-022, 109-111, 136-137, 157-158 | ~20 |
| COMP-012 (Payments Service) | 011, 015-017, 018, 143-144, 154 | ~15 |
| COMP-013 (ANPR Service) | 005-009 | 5 |
| COMP-014 (Notification Service) | 014, 022, 106-108, 138-139, 149-150, 164-165, 175-177 | ~20 |
| COMP-015 (Reports Service) | 023-025, 075-078, 116-130, 147-148, 162-163, 179-180 | ~40 |
| COMP-016 (Support Service) | 175-180 | 6 |
| COMP-017 (Billing Service) | 010, 012-013, 015-016, 079-082, 140, 145-146, 169-174 | ~25 |
| COMP-018 (Monitoring Service) | 020-022, 100-108, 109-111, 114-115, 138-139, 166 | ~25 |
| COMP-019 (Mobile Apps) | 131-150 | 20 |
| COMP-020 (Admin Panel) | 046-050, 083-099, 151-168 | ~50 |
| COMP-021 (Kafka Topics) | Dependendia de todos los publishers/consumers | 180 |
| COMP-022 (CI/CD) | Ningún RF directo — infraestructura de deployment | — |

---

## Cómo usar este directorio

1. **Antes de leer un RF** → consultar este índice para saber qué componentes tocar
2. **Al diseñar un nuevo feature** → verificar que exista COMP para cada dependencia
3. **Al hacer code review** → el diff debe tocar los componentes listados, no saltar capas
4. **Al hacer troubleshooting** → localizar el componente y leer su spec para entender límites

---

## Convention: Cómo referenciar desde los RFs

En cada spec RF-###, agregar una sección **Componentes** al final:

```markdown
## Componentes

- **COMP-001** — API Gateway (this spec depends on it for auth + routing)
- **COMP-010** — Sedes Service (CRUD de espacios)
- **COMP-003** — PostgreSQL (persistencia)
```

Esto crea el mapeo bidireccional: RFs → COMPs y COMPs → RFs.

---

*Última actualización: Mayo 2026*
*Total: 22 specs fundacionales cubriendo todos los 180 RFs*