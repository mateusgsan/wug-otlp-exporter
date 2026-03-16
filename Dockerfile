# WhatsUp Gold OTLP Exporter - Dockerfile
#
# Hardened image: mitigates HIGH CVEs found in python:3.11-slim base:
#   - CVE-2024-8176 (libexpat1 < 2.7.0)  → apt-get upgrade libexpat1
#   - CVE-2024-9143 (libssl3/openssl)     → apt-get upgrade openssl libssl3
#   - CVE-2024-28835 (libgnutls30)        → apt-get upgrade libgnutls30
#
FROM python:3.11-slim

# Metadata
LABEL maintainer="Your Organization"
LABEL description="WhatsUp Gold OTLP Exporter for Grafana Cloud"
LABEL version="1.1"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Security hardening ---
# Apply all OS-level security patches, including HIGH CVEs in:
#   libexpat1 (CVE-2024-8176), openssl/libssl3 (CVE-2024-9143),
#   libgnutls30 (CVE-2024-28835)
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends \
        libexpat1 \
        openssl \
        libssl3 \
        libgnutls30 \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements_otlp.txt .
RUN pip install --upgrade pip setuptools wheel && \
    pip install --upgrade -r requirements_otlp.txt

# Copy application code
COPY wug_otlp_exporter.py .

# Create non-root user
RUN useradd -m -u 1000 exporter && \
    chown -R exporter:exporter /app

USER exporter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import wug_otlp_exporter; print('ok')" || exit 1

CMD ["python", "wug_otlp_exporter.py"]
