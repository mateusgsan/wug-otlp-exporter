# WhatsUp Gold OTLP Exporter - Dockerfile
#
# Base image selection rationale (verified on Docker Hub, 2026-03-16):
#
#   python:3.14-slim-bookworm  → 0 CRITICAL | 0 HIGH | 1 MEDIUM | 16 LOW  ✓ CHOSEN
#   python:3.14-slim (trixie)  → 0 CRITICAL | 3 HIGH | 1 MEDIUM | 24 LOW  ✗ rejected
#   python:3.11-slim (former)  → 0 CRITICAL | 3 HIGH | 1 MEDIUM | 24 LOW  ✗ rejected
#
# python:3.14-slim-bookworm is the most recent Python version available on
# Debian Bookworm (stable), with zero HIGH/CRITICAL CVEs at build time.
# The apt-get upgrade step below ensures OS packages remain patched on
# every rebuild, covering any future CVEs disclosed after image publication.
#
FROM python:3.14-slim-bookworm

# Metadata
LABEL maintainer="Your Organization"
LABEL description="WhatsUp Gold OTLP Exporter for Grafana Cloud"
LABEL version="1.2"

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Security hardening ---
# Apply all available OS-level patches on every build to stay ahead of
# newly disclosed CVEs in Debian Bookworm packages.
RUN apt-get update && \
    apt-get upgrade -y --no-install-recommends \
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
