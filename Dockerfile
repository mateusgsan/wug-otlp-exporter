# WhatsUp Gold OTLP Exporter - Dockerfile
FROM python:3.11-slim

# Metadados
LABEL maintainer="Your Organization"
LABEL description="WhatsUp Gold OTLP Exporter for Grafana Cloud"
LABEL version="1.0"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Criar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements_otlp.txt .

# Instalar dependências Python
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements_otlp.txt

# Copiar código da aplicação
COPY wug_otlp_exporter.py .

# Criar usuário não-root
RUN useradd -m -u 1000 exporter && \
    chown -R exporter:exporter /app

# Trocar para usuário não-root
USER exporter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)" || exit 1

# Executar aplicação
CMD ["python", "wug_otlp_exporter.py"]
