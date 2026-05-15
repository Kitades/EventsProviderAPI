FROM ghcr.io/astral-sh/uv:0.1.0-python3.11-slim


WORKDIR /app


ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app


COPY pyproject.toml uv.lock* ./


RUN uv sync --frozen --no-dev


COPY ./app ./app


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser && \
    chown -R appuser:appuser /app

USER appuser


CMD ["uv run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]