# Используем официальный микро-образ со встроенным uv и python 3.11
FROM ghcr.io/astral-sh/uv:python3.11-slim

WORKDIR /app


ENV UV_COMPILE_BYTECODE=1


COPY requirements.txt .


RUN uv pip install --system --no-cache -r requirements.txt


COPY ./app ./app


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser && \
    chown -R appuser:appuser /app

USER appuser


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]