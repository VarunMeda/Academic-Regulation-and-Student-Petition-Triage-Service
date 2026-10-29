FROM python:3.11-slim
WORKDIR /service
COPY . .
RUN python -m pip install --no-cache-dir --timeout 120 --retries 5 -e ".[runtime]"
RUN python -m app.ingest
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

