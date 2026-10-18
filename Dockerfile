FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias Python
RUN pip install --no-cache-dir fastapi uvicorn databases sqlalchemy reportlab crccheck google-genai pyserial

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
