FROM python:3.11-slim
WORKDIR /service
COPY . .
RUN pip install --no-cache-dir -e .
RUN python -m app.ingest
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

