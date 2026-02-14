# SWIFT Banking System - Docker Image

FROM python:3.12-slim

# Labels
LABEL maintainer="Livinus Tuyisenge "
LABEL description="SWIFT Banking System CLI - ISO 20022 & MT103 Message Generator"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    APP_HOME=/app

# Create app directory
WORKDIR ${APP_HOME}

# Copy application code
COPY code/ ${APP_HOME}/

# Set permissions
RUN chmod +x ${APP_HOME}/main.py && \
    mkdir -p ${APP_HOME}/output

# Default command - show help
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]
