# COMP-022 — CI/CD Pipeline & Infrastructure as Code

## Metadata

- **Nombre**: CI/CD Pipeline + IaC
- **Tipo**: DevOps / Infrastructure
- **Prioridad**: Crítica
- **Servicios afectados**: Todos los servicios

---

## Objetivo

Automatizar el build, test y deploy de todos los microservicios y aplicaciones (frontend, backend, mobile) usando GitHub Actions. Toda la infraestructura se define como código (Terraform + Helm) para ser reproducible en cualquier ambiente.

---

## Repositorio Structure

```
parkcore/
├── .github/
│   └── workflows/
│       ├── api-ci.yml          # Backend microservicios
│       ├── frontend-ci.yml     # Admin Panel (Angular)
│       ├── mobile-ci.yml       # Apps (Flutter)
│       ├── deploy-staging.yml   # Deploy a staging
│       └── deploy-prod.yml     # Deploy a producción
├── infra/
│   ├── terraform/
│   │   ├── modules/
│   │   │   ├── cluster/
│   │   │   ├── postgres/
│   │   │   ├── redis/
│   │   │   ├── kafka/
│   │   │   └── s3/
│   │   ├── environments/
│   │   │   ├── staging/
│   │   │   └── production/
│   │   └── main.tf
│   └── helm/
│       └── charts/
│           ├── auth-service/
│           ├── sedes-service/
│           ├── iot-service/
│           ├── pagos-service/
│           └── ... (uno por servicio)
├── auth-service/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── src/
│   └── tests/
└── ... (un directorio por microservicio)
```

---

## GitHub Actions Workflows

### API CI (`api-ci.yml`)

**Trigger**: Push a `main` o `release/*` en `*-service/` directorios

**Flujo**:
```
1. Checkout código
2. Setup Python 3.11
3. Instalar dependencias (poetry)
4. Lint: black + ruff + mypy
5. Tests: pytest (unit + integration)
6. Build Docker image
7. Push a Docker Hub (tag: commit SHA)
8. Run contract tests (Pact)
9. Scan vulnerabilities (Trivy)
10. Notification: Slack success/failure
```

**Secrets necesarios**:
- `DOCKERHUB_TOKEN`
- `SLACK_WEBHOOK`

### Frontend CI (`frontend-ci.yml`)

**Trigger**: Push a `main` en `admin-panel/`

**Flujo**:
```
1. Checkout
2. Setup Node 20
3. npm ci
4. Lint: ESLint
5. Tests: Jest + Playwright e2e
6. Build Angular (prod)
7. SonarCloud scan
8. Deploy to Firebase Hosting (staging)
9. Notification: Slack
```

### Mobile CI (`mobile-ci.yml`)

**Trigger**: Push a `main` o PR a `main` (Flutter apps)

**Flujo**:
```
1. Checkout
2. Setup Flutter 3.x
3. flutter pub get
4. flutter analyze
5. flutter test
6. Build iOS (Codemagic trigger)
7. Build Android (GitHub Actions)
8. Beta Firebase App Distribution (staging)
9. Play Store internal track (prod tag)
```

---

## Docker Image Strategy

```dockerfile
# Dockerfile (multi-stage)
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml poetry.lock* ./
RUN pip install poetry && poetry install --no-dev

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"
COPY ./src /app/src
EXPOSE 8001
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8001"]

# Tags:
#   parkcore/auth-service:latest      — latest from main
#   parkcore/auth-service:1.2.3       — semver tag
#   parkcore/auth-service:abc1234     — commit SHA
```

---

## Helm Charts Structure

```yaml
# infra/helm/charts/auth-service/values.yaml
replicaCount: 2

image:
  repository: parkcore/auth-service
  tag: "1.2.3"  # overridden by CI

service:
  port: 8001
  type: ClusterIP

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: auth.parkcore.io
      paths: [{ path: /, pathType: Prefix }]
  tls:
    - secretName: auth-tls
      hosts: [auth.parkcore.io]

resources:
  requests: { cpu: "100m", memory: "128Mi" }
  limits:   { cpu: "500m", memory: "512Mi" }

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

probes:
  liveness:
    path: /health/live
    initialDelaySeconds: 15
  readiness:
    path: /health/ready
    initialDelaySeconds: 5

env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: auth-service-secrets
        key: database-url
```

---

## Terraform Modules

```hcl
# infra/terraform/modules/postgres/main.tf
resource "aws_rds_cluster" "main" {
  cluster_identifier = var.cluster_name
  engine             = "postgres"
  engine_version     = "15.3"
  database_name      = var.database_name
  master_username    = var.master_username
  master_password    = var.master_password
  
  # Multi-AZ para producción
  multi_az               = var.is_production ? true : false
  db_subnet_group_name   = var.db_subnet_group_id
  vpc_security_group_ids = [var.security_group_id]
  
  backup_retention_period = var.is_production ? 30 : 7
  storage_encrypted      = true
  kms_key_id             = var.kms_key_id
  
  # Performance Insights para producción
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
}

resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.cluster_name}/db-password"
}
```

---

## Environments

| Environment | Trigger | URL | Notas |
|-------------|---------|-----|-------|
| `dev` | Push a cualquier branch | dev.parkcore.io | Localmente con Docker Compose |
| `staging` | Push a `main` | staging.parkcore.io | Auto-deploy, datos anonimizados |
| `production` | Tag `v*.*.*` | app.parkcore.io | Blue-green deploy, approval requerida |

---

##Secrets Management

```yaml
# GitHub Actions secrets (Settings > Secrets)
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
SLACK_WEBHOOK
TF_STATE_BUCKET      # S3 bucket para Terraform state
TF_STATE_KMS_KEY     # KMS key para encryptar state
VAULT_ADDR           # HashiCorp Vault address
VAULT_TOKEN          # Token de AppRole (no usar root token)
SONAR_TOKEN
FIREBASE_TOKEN       # Firebase CLI token para hosting
CODEMAGIC_API_KEY    # Para trigger builds iOS
```

---

## Database Migrations

```yaml
# En cada microservicio: src/migrations/
# Usar Alembic (Python) o Flyway (JVM)

# CI automatically runs:
# 1. docker-compose exec auth-service alembic upgrade head
# 2. Verificar que el schema es el esperado
# 3. Si falla, rollback y notificar
```

---

## Rollback Strategy

1. **Docker images** son inmutables — si el deploy falla, el anterior sigue disponible
2. **Helm rollback**: `helm rollback auth-service` — revierte a release anterior
3. **Database migrations** — cada migración debe ser reversible (downgrade)
4. **Feature flags** — deshabilitar feature sin hacer rollback de código

---

## Monitoreo de Deploys

```yaml
# Post-deploy smoke tests (GitHub Actions)
- name: Run smoke tests
  run: |
    curl -f https://staging.parkcore.io/health || exit 1
    curl -f https://staging.parkcore.io/api/v1/auth/validate \
      -H "Authorization: Bearer ${{ secrets.TEST_TOKEN }}" || exit 1

# Si falla → Slack alert + auto-rollback en producción
```

---

## Dependencias

- **Docker Hub**: Registry para imágenes
- **GitHub Actions**: CI/CD (ya tiene runners Ubuntu)
- **Terraform**: IaC (AWS, GCP o Azure)
- **Helm**: Package manager para Kubernetes
- **Vault**: Secrets (via GitHub Actions OIDC)
- **SonarCloud**: Code quality scan
- **Trivy**: Vulnerabilidad scanning

---

## Métricas

- **Deployment frequency**: > 5 deploys/semana a producción
- **Lead time**: < 30 min desde commit hasta producción
- **MTTR**: < 15 min para rollback
- **Change failure rate**: < 5% de deploys requieren rollback

---

## Alternativas Open Source

| Opción | Ventajas | Notes |
|--------|----------|-------|
| **Jenkins** (elegido) | Open source, plugins riches, control total | Infra propia, mayor mantenimiento |
| **GitLab CI** | Integrado con GitLab, YAML declarativo, muy usado | Si mueves el repo a GitLab |
| **Drone.io** | Docker-based, simple, open source | Bueno para equipos pequeños |
| **Apache Buildstream** | Builds reproducibles, más complejo | Solo si necesitas builds muy controlados |
| **GitHub Actions** | Runner gratuito para open source,SaaS | Proprietary pero gratis para pública |

**Decisión**: **Jenkins** como default para CI/CD auto-hostado. Si el cliente ya usa GitLab, migrar a GitLab CI es trivial (solo cambiar el repo y reescribir los YAMLs). El workflow YAML es casi idéntico.

**Runner self-hosted**: Configurar 2-3 agentes Jenkins on VM para empezar. Escalar añadiendo nodos según demanda de builds.