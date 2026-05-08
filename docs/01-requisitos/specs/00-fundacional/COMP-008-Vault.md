# COMP-008 — Vault (Secrets Management)

## Metadata

- **Nombre**: vault-service
- **Tipo**: Microservicio / Infraestructura
- **Prioridad**: Crítica
- **Puerto**: 8200 (HTTP), 8201 (HA)
- **Servicios afectados**: Todos los microservicios
- **Componentes relacionados**: auth-service, todos los servicios internos

---

## Objetivo

Centralizar la gestión de secretos (contraseñas, API keys, certificados, tokens) del sistema usando HashiCorp Vault. Todos los servicios deben obtener sus secretos de Vault, nunca hardcodeados ni en variables de entorno inseguras.

---

## Tecnología

- **Engine**: HashiCorp Vault (Enterprise o HCP)
- **Storage Backend**: PostgreSQL (para HA) o RAFT (para single-node)
- **Secrets Engines**: KV v2, PKI, AWS, Database
- **Auth Methods**: Kubernetes, AppRole, JWT/OIDC
- **Auto-unseal**: AWS KMS / Azure Key Vault / GCP KMS

---

## Secrets Engines

### KV v2 — Secretos estáticos

Almacena secretos estructurados por servicio y ambiente:

```
secret/
├── data/
│   ├── services/
│   │   ├── auth-service/
│   │   │   ├── prod/
│   │   │   │   └── { jwt_private_key, db_password, redis_password }
│   │   │   └── staging/
│   │   ├── tenant-service/
│   │   │   └── prod/
│   │   └── ...
│   ├── tenants/
│   │   └── {tenant_id}/
│   │       └── { api_key, webhook_secret }
│   └── global/
│       └── { dian_api_key, smtp_password, sms_api_key }
```

### PKI — Certificados automáticos

```
pki/
├── roles/
│   └── parkcore-internal/   (allow_subdomains: true, ttl: 24h)
├── certs/
│   └── *.parkcore.io
```

Certificados internos se rotan automáticamente cada 24h.

### Database — Dynamic Credentials

Genera credenciales temporales para PostgreSQL:

```
database/roles/parkcore-readonly
database/roles/parkcore-write
```

TTL: 1h para roles readonly, 15min para write.

---

## Auth Methods

### Kubernetes Auth (para pods)

```yaml
# Cada pod tiene ServiceAccount con annotation
# vault.hashicorp.com/auth-method: "kubernetes"
# vault.hashicorp.com/role: "auth-service"
```

Policy por rol:
```
path "secret/data/services/auth-service/*"
  capabilities = ["read"]
```

### AppRole (para servicios legacy)

```yaml
# AppRole con role_id y secret_id
vault write auth/approle/role/auth-service \
  token_ttl=1h \
  token_policies=auth-service
```

### JWT/OIDC (para CLI y automatización)

```yaml
# Auth vía GitHub OIDC o JWT de Google Cloud
vault write auth/jwt/role/ci-deploy \
  bound_audiences="parkcore-ci" \
  token_policies=deploy-bot
```

---

## API Endpoints

### Secret Management (interno)

```
POST /internal/v1/secrets/:service/:path
GET  /internal/v1/secrets/:service/:path
LIST /internal/v1/secrets/:service/
DELETE /internal/v1/secrets/:service/:path
```

### Certificate Management

```
POST /internal/v1/certs/issue/:role
GET  /internal/v1/certs/ca chain
```

### Dynamic Credentials

```
POST /internal/v1/db/creds/:role
POST /internal/v1/db/creds/readonly
POST /internal/v1/db/creds/write
```

---

## Estructura de Policies

### policy-auth-service.hcl
```hcl
path "secret/data/services/auth-service/*" {
  capabilities = ["read"]
}
path "database/creds/parkcore-readonly" {
  capabilities = ["read"]
}
path "pki/issue/parkcore-internal" {
  capabilities = ["create", "read"]
}
```

### policy-tenant-service.hcl
```hcl
path "secret/data/services/tenant-service/*" {
  capabilities = ["read"]
}
path "secret/data/tenants/*" {
  capabilities = ["read", "list"]
}
path "database/creds/parkcore-readonly" {
  capabilities = ["read"]
}
```

---

## Sincronización con Kubernetes Secrets

```yaml
# annotations en pod para sync automático
vault.hashicorp.com/vault-secret-name: "auth-service-secrets"
vault.hashicorp.com/vault-secret-template: "secret/data/services/auth-service/prod"
```

Vault Agent Injector monta secrets como archivos:
```
/vault/secrets/
├── db_password
├── jwt_private_key
└── redis_password
```

---

## Rotación de Secretos

### Manual
```bash
# Rotar secreto específico
vault write -f secret/data/services/auth-service/prod/db_password

# Rotar certificado
vault write -f pki/issue/parkcore-internal common_name="auth-service.parkcore.io"
```

### Automático
- DB creds: 1h TTL con lease renewal
- Certs internos: 24h auto-renew (30min antes de expiry)
- API keys: No auto-rotate (manual process)

---

## Monitoreo

### Métricas Vault

```
vault.core.active (gauge)
vault.core.replicationactive (gauge)
vault.identity.entity.active (gauge)
vault.secret.kv.v2.count (gauge)
vault.token.count (gauge)
vault.runtime.allocations (gauge)
vault.runtime.heap_objects (gauge)
```

### Alerts

| Alerta | Condición |
|--------|-----------|
| VaultUnsealed | vault_status != sealed |
| LeaseExpiration | lease expiring in < 1h |
| PolicyViolation | failed auth attempts > 10 |
| StorageBackendDown | raft peer unreachable |

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|---------------|-------------|
| `VAULT_ADDR` | https://vault.parkcore.io | Dirección del Vault |
| `VAULT_AUTH_METHOD` | kubernetes | Método de autenticación |
| `VAULT_K8S_ROLE` | auto | Rol desde annotation SA |
| `VAULT_MOUNT_PATH` | secret | Path base para KV |
| `VAULT_MAX_LEASE_TTL` | 768h | Max TTL para leases |
| `VAULT_DEFAULT_LEASE_TTL` | 1h | TTL por defecto |

---

## Dependencias

- **Infraestructura**: HashiCorp Vault (3 nodes para HA)
- **Cloud**: AWS KMS / Azure Key Vault / GCP KMS para auto-unseal
- **Kubernetes**: Vault Agent Injector, ServiceAccount annotations
- **DB**: PostgreSQL como storage backend (HA mode)

---

## Métricas de Éxito

- Disponibilidad Vault: 99.99% (zero downtime para secret access)
- Tiempo de entrega de secreto: < 100ms
- Renewals exitosos: > 99.5%
- Cero secretos hardcoded en código: 100%

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|----------------|
| Vault sealed | Servicios con credenciales en cache sobreviven 1h |
| Lease expirado sin renew | App recibe error, debe pedir nuevo secret |
| K8s auth falla | Fallback a AppRole con retry + backoff |
| Network partition | Secret cache local (1h TTL) permite operación |
| Audit log full | Vault entra en read-only mode |

---

## Seguridad

### Auditoría

Todos los accesos a secretos se registran en audit log:
```json
{
  "time": "2026-01-15T10:30:00Z",
  "type": "read",
  "client_token": {
    " accessor": "xxx",
    " policy": "auth-service"
  },
  "path": "secret/data/services/auth-service/prod",
  "mount_type": "kv",
  "namespace": "default"
}
```

### Encryption

- Datos en tránsito: TLS 1.3 obligatorio
- Datos en disco: AES-256-GCM (Vault encryption)
- Keys de unseal: Managed servicio cloud (never on disk)

### Compliance

- PCI-DSS: Secretos nunca en logs, memoria limpia
- SOC 2: Audit logsRetention 1 año
- GDPR: No PII en secretos

---

## Notas

- Vault está en namespace separado de apps
- Solo ops-team tiene acceso a UI de Vault
- Secrets nunca se muestran en logs (***redacted***)
- Emergency unseal: 3 de 5 keys necessary
- Migration: Soporte para移行 from env vars a Vault gradual

---

## Alternativas Open Source

| Opción | Ventajas | Notes |
|--------|----------|-------|
| **HashiCorp Vault** (elegido) | Maduro, KV v2, PKI, Database dynamic secrets, Kubernetes auth | Para equipos con experiencia en Vault |
| **ESOPS Secrets Operator** |-native Kubernetes, injection directa en pods | Más simple si solo necesitas secretos en K8s |
| **External Secrets Operator** | Sincroniza desde AWS SM / GCP SM / Vault | Ideal si ya usas cloud managed secrets |
| **CyberArk Conjur** | Enterprise-grade, PCI-DSS nativo | Si hay requisitos regulatorios estrictos |
| **Sealed Secrets** | Cifrado con clave pública del cluster, ningún secreto en Git | Bueno para GitOps |
| **Kubernetes Secrets (baseline)** | Nativo de K8s, sin componentes extra | Aceptable para empezar — no para producción |

**Decisión**: **External Secrets Operator + el managed secrets del cloud** (AWS Secrets Manager / GCP Secret Manager) para la mayoría de deployments. Si el cliente quiere 100% on-prem sin cloud, usar **HashiCorp Vault** con auto-unseal via AWS KMS / GCP KMS.

**Ventaja de External Secrets Operator**: los secretos nunca viven en el cluster como texto plano — se sincronizan del cloud provider y el operator los inyecta en los pods via Kubernetes Secrets native.