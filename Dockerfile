FROM --platform=linux/x86_64 <http://ghcr.io/astral-sh/uv:python3.11-bookworm-slim|ghcr.io/astral-sh/uv:python3.11-bookworm-slim>
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock
RUN uv sync --frozen


WORKDIR /app


ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app



COPY ./app ./app


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser && \
    chown -R appuser:appuser /app

USER appuser


CMD ["uv run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]