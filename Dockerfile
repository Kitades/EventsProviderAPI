FROM ghcr.io/astral-sh/uv:python3.12-alpine


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONPATH=/app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
COPY ./app ./app
COPY --chown=appuser:appuser /app/main.py .

USER appuser

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]