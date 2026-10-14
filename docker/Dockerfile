# ==============================================================================
# Dockerfile — Minimal Hardened Application Container
# Project: Automated Local DevSecOps — Secret Scanner & Image Guard
# Module: Member 2 — Container Security (Docker + Trivy)
# ==============================================================================
# Design Choices:
# 1. Pinned Base Image: python:3.12.9-alpine3.21 ensures reproducibility and minimal attack surface.
# 2. Non-Root Execution: Runs as dedicated 'appuser' (UID 10001) instead of root.
# 3. Least Privilege: Only the application file is copied into /app with restricted permissions.
# 4. No Build Secrets or Dev Tools: Keeps final image lean and free of extraneous packages.
# ==============================================================================

FROM python:3.12.9-alpine3.21

# Set environment variables for Python in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_PORT=8080

# Update OS packages to apply latest security patches
RUN apk update && apk upgrade --no-cache

# Create a non-root group and user with specific UID/GID
RUN addgroup -g 10001 -S appgroup && \
    adduser -u 10001 -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy application source code with correct ownership
COPY --chown=appuser:appgroup docker/app.py /app/app.py

# Switch to non-root user
USER 10001:10001

# Expose microservice port
EXPOSE 8080

# Container healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Launch microservice
CMD ["python", "/app/app.py"]
