# Microservices - Parqueaderos SaaS

## Índice de Microservicios

Este directorio contiene los microservicios del proyecto Parqueaderos SaaS.

### Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| [tenant-service](./tenant-service/) | 8002 | Gestión de tenants (tenants, usuarios, configuración) |
| [sedes-service](./sedes-service/) | 8003 | Gestión de sedes y espacios de parqueadero |

## Estructura común

Cada microservicio sigue la estructura:

```
<service>/
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/v1/router.py
│   ├── core/
│   │   ├── security.py
│   │   └── tracing.py
│   ├── db/
│   │   ├── session.py
│   │   └── models.py
│   ├── schemas/
│   │   └── *.py
│   └── services/
│       └── *_service.py
├── tests/
│   └── test_*.py
└── migrations/
    └── versions/
```

## Desarrollo

```bash
# Construir imagen
docker build -t tenant-service:latest ./tenant-service

# Ejecutar con docker-compose
docker-compose -f tenant-service/docker-compose.yml up

# Ejecutar tests
cd tenant-service && pytest
```

## Variables de Entorno

Ver `app/config.py` para configuración completa.

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka broker address
- `OTEL_EXPORTER_OTLP_ENDPOINT`: OpenTelemetry collector endpoint