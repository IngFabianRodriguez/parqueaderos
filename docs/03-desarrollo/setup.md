# Guía de Instalación y Configuración Local

## Requisitos del Sistema

- Python 3.11+
- Node.js 18+
- Docker y Docker Compose
- PostgreSQL 15+
- Redis 7+

## Pasos de Instalación

1. Clonar el repositorio
2. Configurar variables de entorno (crear .env desde .env.example con: DATABASE_URL, REDIS_URL, JWT_SECRET, API_KEY_ANPR, PASARELA_PAGO_KEY)
3. Instalar dependencias backend: `uv sync` o `pip install -r requirements.txt`
4. Instalar dependencias frontend: `npm install`
5. Ejecutar migraciones de BD: `alembic upgrade head`
6. Iniciar servicios con Docker Compose: `docker-compose up -d` (PostgreSQL, Redis, MQTT broker)
7. Ejecutar servidor de desarrollo: `uv run uvicorn src.api.main:app --reload`
8. Ejecutar frontend: `npm run dev`

## Estructura de Carpetas del Proyecto

```
proyecto/
├── src/
│   ├── api/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── middleware/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── db/
├── tests/
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── alembic/
├── docs/
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## Puertos y Servicios

| Puerto  | Servicio          |
|---------|-------------------|
| 8000    | API               |
| 3000    | Frontend dev      |
| 5432    | PostgreSQL        |
| 6379    | Redis             |
| 1883    | MQTT              |

## Cómo Ejecutar los Tests

- Backend: `pytest`
- Frontend: `npm run test`

## Verificación de Instalación

```bash
curl http://localhost:8000/health
```
