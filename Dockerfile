# Multi-stage production Dockerfile for Bytecode VM & Evaluator API
# -------------------------------------------------------------
# Stage 1: Build virtualenv and install production dependencies
# -------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /build

# Install compilation tools if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create isolated Python virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------------------
# Stage 2: Final lightweight, secure non-root runtime image
# -------------------------------------------------------------
FROM python:3.12-slim AS runner

WORKDIR /app

# Set production environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    PORT=8000

# Copy pre-built virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create a non-privileged user and group
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

# Copy application source code
COPY --chown=appuser:appuser core/ /app/core/
COPY --chown=appuser:appuser api/ /app/api/
COPY --chown=appuser:appuser frontend/ /app/frontend/
COPY --chown=appuser:appuser repl.py /app/repl.py

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:' + str(__import__('os').environ.get('PORT', 8000)) + '/health')" || exit 1

EXPOSE 8000

# Start production server
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
