# ---- Base stage ----
FROM python:3.11-slim AS base

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_VERSION=0.5.24

RUN pip install uv==${UV_VERSION}

# ---- Dependencies stage ----
FROM base AS deps

COPY pyproject.toml uv.lock* ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

# ---- Install stage ----
FROM deps AS install

COPY . .
RUN uv sync --frozen

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=install /app /app
COPY --from=deps /root/.cache/uv /root/.cache/uv

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8004

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
