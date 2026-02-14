# SWIFT Banking System - Docker Image

FROM python:3.12-slim

# Labels
LABEL maintainer="Livinus Tuyisenge"
LABEL description="SWIFT Banking System CLI - ISO 20022 & MT103 Message Generator"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    APP_HOME=/app

# Create app directory
WORKDIR ${APP_HOME}

# Copy project files
COPY pyproject.toml README.md ${APP_HOME}/
COPY swift_cli/ ${APP_HOME}/swift_cli/

# Install the package
RUN pip install --no-cache-dir . && \
    mkdir -p ${APP_HOME}/output

# Default command - show help
ENTRYPOINT ["swift-cli"]
CMD ["--help"]
