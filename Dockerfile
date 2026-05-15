FROM python:3.11-slim


WORKDIR /code

COPY requirements.txt .


RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY ./app ./app


RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser && \
    chown -R appuser:appuser /code

USER appuser


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]