# COMP-006 — S3

## Metadata

- **Nombre**: S3 — ParkCore Object Storage
- **Tipo**: Infraestructura (Object Storage)
- **Prioridad**: Alta
- **Servicios afectados**: ANPR-service, pagos-service, reports-service, notif-service
- **Componentes relacionados**: Todos los servicios que almacenan archivos

---

## Objetivo

Proveer almacenamiento de objetos para archivos estáticos, multimedia y backups. S3 es usado para: imágenes de vehículos (ANPR), Comprobantes de pago (PDF), reportes exportados, stickers de notificación (images), y backups de bases de datos.

---

## Arquitectura

```
[Microservicios] → [S3 Compatible API] → [MinIO / AWS S3]
                                    ↓
                            [Lifecycle Policies]
                                    ↓
                            [Glacier / Deep Archive]
```

### Configuración de Storage

| Bucket | Versión | Cifrado | Uso |
|--------|---------|---------|-----|
| parkcore-anpr-images | Enabled | AES-256 | Imágenes de reconocimiento de placas |
| parkcore-payment-docs | Enabled | AES-256 | PDFs de comprobantes de pago |
| parkcore-reports | Enabled | AES-256 | Reportes exportados (CSV, Excel, PDF) |
| parkcore-notifications | Enabled | AES-256 | Assets de notificaciones (logos, stickers) |
| parkcore-backups | Enabled | AES-256 | Backups de base de datos (DB dumps) |
| parkcore-logs-archive | Enabled | AES-256 | Logs archivados para compliance |

---

## Datos de Configuración

| Parámetro | Valor default | Descripción |
|-----------|--------------|-------------|
| S3_PROVIDER | minio | minio o aws |
| S3_ENDPOINT | http://minio:9000 | Endpoint del bucket |
| S3_REGION | us-east-1 | Región (para AWS) |
| S3_ACCESS_KEY | env var | Access key |
| S3_SECRET_KEY | env var | Secret key |
| S3_BUCKET_PREFIX | parkcore- | Prefijo para buckets |
| MAX_UPLOAD_SIZE | 100MB | Tamaño máximo de upload |
| PRESIGNED_URL_TTL | 3600 | TTL para URLs firmadas (seg) |
| MULTIPART_THRESHOLD | 50MB | Umbral para multipart upload |

---

## Características de Objetos

### ANPR Images

```
Bucket: parkcore-anpr-images
Key pattern: {tenant_id}/{sede_id}/{YYYY}/{MM}/{DD}/{timestamp}_{plate}_{camera_id}.jpg
Size: típicamente 100KB - 500KB por imagen
Retention: 30 días (hot), luego transition to Glacier
```

### Payment Documents

```
Bucket: parkcore-payment-docs
Key pattern: {tenant_id}/{YYYY}/{MM}/{transaction_id}.pdf
Size: hasta 10MB por comprobante
Retention: 7 años (compliance financiera)
Metadata: transaction_id, tenant_id, amount, timestamp
```

### Reports

```
Bucket: parkcore-reports
Key pattern: {tenant_id}/reports/{YYYY}/{MM}/{report_id}_{type}.{ext}
Types: csv, xlsx, pdf
Retention: 90 días
```

### Notification Assets

```
Bucket: parkcore-notifications
Key pattern: assets/{type}/{name}.{ext}
Types: logo.png, sticker.webp, icon.svg
Retention: No expira (versionado para updates)
```

### Database Backups

```
Bucket: parkcore-backups
Key pattern: {service}/{YYYY}/{MM}/{DD}/{timestamp}_{service}.dump.gz.enc
Encryption: AES-256 antes de upload
Retention: 30 días hot, luego archivado
```

---

## Seguridad

### Políticas de Bucket

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyIncorrectEncryptionHeader",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::parkcore-*/*",
      "Condition": {
        "StringNotEquals": {
          "s3:x-amz-server-side-encryption": "AES256"
        }
      }
    },
    {
      "Sid": "DenyUnEncryptedObjectUploads",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::parkcore-*/*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    }
  ]
}
```

### Access Control

- IAM policies por servicio
- No bucket público
- Todos los uploads deben estar encriptados (AES-256)

---

## Lifecycle Policies

| Bucket | Transición a Cold | Expiración |
|--------|------------------|-----------|
| anpr-images | 30 días → Glacier | 90 días |
| payment-docs | 365 días → Deep Archive | 7 años |
| reports | 30 días → Glacier | 90 días |
| notifications | No aplicar | No expira |
| backups | 7 días → Glacier | 30 días |
| logs-archive | 30 días → Glacier | 7 años |

---

## API Endpoints

### Operaciones Comunes

```bash
# Upload (desde servicio)
aws s3 cp local-file.jpg s3://parkcore-anpr-images/tenant1/sede1/2024/01/15/img.jpg

# Download (presigned URL)
aws s3 presign s3://parkcore-payment-docs/tenant1/2024/01/tx123.pdf --expires-in 3600

# List objects
aws s3 ls s3://parkcore-anpr-images/tenant1/sede1/2024/01/15/

# Delete (por lifecycle o manual)
aws s3 rm s3://parkcore-backups/2023/12/

# Sync local a bucket
aws s3 sync ./local-dir s3://parkcore-reports/tenant1/reports/
```

### SDK Usage

```python
# Python (boto3)
import boto3
s3 = boto3.client('s3', endpoint_url=os.getenv('S3_ENDPOINT'))
s3.put_object(
    Bucket='parkcore-anpr-images',
    Key=key,
    Body=image_bytes,
    ContentType='image/jpeg',
    Metadata={'plate': plate, 'tenant_id': tenant_id},
    ServerSideEncryption='AES256'
)
```

---

## Comandos de Gestión

```bash
# Ver tamaño de bucket
aws s3 ls s3://parkcore-anpr-images/ --recursive --summarize

# Head object (metadata)
aws s3api head-object --bucket parkcore-anpr-images --key "path/to/file.jpg"

# Copy entre buckets
aws s3 cp s3://source-bucket/path s3://dest-bucket/path

# Restore desde Glacier (si aplicando lifecycle)
aws s3 restore-object --bucket bucket --key key --restore-request 'Days=7'

# Versioning
aws s3api list-object-versions --bucket bucket-name

# Tags
aws s3api get-object-tagging --bucket bucket-name --key path/to/file
```

---

## Monitoreo

### Métricas CloudWatch / Prometheus

- `BucketSizeBytes` — tamaño total del bucket
- `NumberOfObjects` — cantidad de objetos
- `AllStorageTypesBytes` — storage por tipo (Standard, Glacier)
- `Requests` — total de requests (GET, PUT, DELETE)
- `4xxErrors` / `5xxErrors` — errores por código

### Alertas

| Condición | Severidad |
|-----------|-----------|
| Bucket size > 80% de quota | WARNING |
| Bucket size > 95% de quota | CRITICAL |
| 5xx errors rate > 1% | WARNING |
| 5xx errors rate > 5% | CRITICAL |

---

## Dependencias

- **Infraestructura**: MinIO (on-prem) o AWS S3 (cloud)
- **Secretos**: `S3_ACCESS_KEY`, `S3_SECRET_KEY` via Vault
- **Servicios**: ANPR, pagos, reports, notif, backup scripts

---

## Métricas de Éxito

- Upload成功率: > 99.9%
- Download latency P99: < 200ms
- Presigned URL generation: < 50ms
- Data durability: 99.999999999% (11 9s)

---

## Casos de Borde

| Escenario | Comportamiento |
|-----------|---------------|
| Upload > 100MB | Multipart upload automático |
| Network failure | Retry con exponential backoff (max 5 retries) |
| Glacier restore | Usar presigned URL con restore ya hecho, o esperar |
| Key conflict | Object versioning preserva ambos |
| Storage quota exceeded | Retornar 403, alertar, no subir |

---

## Notas

- Todos los objetos deben tener metadata mínima: tenant_id, created_at
- Usar pre-signed URLs para downloads del frontend (no exponer credenciales)
- Multipart para archivos > 50MB
- La idempotencia se logra con la key (no con ETag) — key única por objeto
- Para backups, comprimir + encryptar localmente antes de subir

---

## Alternativas Open Source

| Opción | Ventajas | Notes |
|--------|----------|-------|
| **MinIO** (elegido) | S3-compatible, Apache 2.0, el estándar de facto para on-prem | Mismo API que AWS S3, migration trivial |
| **Ceph RGW** | Más completo (RADOS + Block + Object), pero complejo | Si ya usas Ceph en infra |
| **OpenStack Swift** | Compatible con API Swift, no S3 | Solo si ya tienes OpenStack |

**Decisión**: **MinIO** para storage on-prem. Compatible 100% con el SDK de AWS S3 que ya usamos en los servicios — solo cambiar el endpoint, credenciales y region.

**Si usas cloud**: AWS S3 / GCS / Azure Blob Store siguen siendo opciones válidas si el cliente quiere managed.