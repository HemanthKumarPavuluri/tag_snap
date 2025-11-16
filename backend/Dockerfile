FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install runtime Python deps from requirements file
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code (files will be at /app/)
COPY . .

EXPOSE 8080
ENV PORT=8080

# Add /app to Python path so backend module can be imported
ENV PYTHONPATH=/app

# Cloud Run expects the server to listen on $PORT. Use uvicorn to serve the FastAPI app.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
