# SWIFT Banking CLI - Makefile
# ============================
#
# Usage:
#   make build          - Build Docker image
#   make install        - Install locally via pip
#   make install-dev    - Install in development mode with dev dependencies
#   make help           - Show CLI help
#   make validate-bic BIC=BNPAFRPPXXX
#   make validate-iban IBAN="FR7630006000011234567890189"
#   make generate-pain001 CONFIG=data/sample_payment.json
#   make batch-validate FILE=data/sample_accounts.txt TYPE=iban

.PHONY: all build install install-dev help validate-bic validate-iban generate-pain001 generate-mt103 \
        batch-validate watch stop logs clean shell test format lint

# Variables
COMPOSE := docker compose
IMAGE_NAME := swift-banking-cli:latest

# Default target
all: help

# Install locally via pip
install:
	@echo "Installing swift-cli locally..."
	pip install .
	@echo "✓ Installation complete. Run 'swift-cli --help' to get started."

# Install in development mode with dev dependencies
install-dev:
	@echo "Installing swift-cli in development mode..."
	pip install -e ".[dev]"
	@echo "✓ Development installation complete."

# Build the Docker image
build:
	@echo "Building SWIFT CLI Docker image..."
	$(COMPOSE) build
	@echo "✓ Build complete"

# Show CLI help
help:
	$(COMPOSE) run --rm swift --help

# Validate BIC code
# Usage: make validate-bic BIC=BNPAFRPPXXX
validate-bic:
ifndef BIC
	@echo "Error: BIC is required. Usage: make validate-bic BIC=BNPAFRPPXXX"
	@exit 1
endif
	$(COMPOSE) run --rm swift validate-bic $(BIC)

# Validate IBAN
# Usage: make validate-iban IBAN="FR7630006000011234567890189"
validate-iban:
ifndef IBAN
	@echo "Error: IBAN is required. Usage: make validate-iban IBAN=\"FR7630006000011234567890189\""
	@exit 1
endif
	$(COMPOSE) run --rm swift validate-iban "$(IBAN)"

# Generate pain.001 message
# Usage: make generate-pain001 CONFIG=data/sample_payment.json OUTPUT=output/message.xml
generate-pain001:
ifndef CONFIG
	@echo "Error: CONFIG is required. Usage: make generate-pain001 CONFIG=data/sample_payment.json"
	@exit 1
endif
	@mkdir -p output
	$(COMPOSE) run --rm swift generate-pain001 --config /data/$(notdir $(CONFIG)) $(if $(OUTPUT),--output /app/output/$(notdir $(OUTPUT)))

# Generate MT103 message
# Usage: make generate-mt103 CONFIG=data/sample_payment.json
generate-mt103:
ifndef CONFIG
	@echo "Error: CONFIG is required. Usage: make generate-mt103 CONFIG=data/sample_payment.json"
	@exit 1
endif
	@mkdir -p output
	$(COMPOSE) run --rm swift generate-mt103 --config /data/$(notdir $(CONFIG)) $(if $(OUTPUT),--output /app/output/$(notdir $(OUTPUT)))

# Batch validate file
# Usage: make batch-validate FILE=data/sample_accounts.txt TYPE=iban
batch-validate:
ifndef FILE
	@echo "Error: FILE is required. Usage: make batch-validate FILE=data/sample_accounts.txt TYPE=iban"
	@exit 1
endif
ifndef TYPE
	@echo "Error: TYPE is required (bic or iban). Usage: make batch-validate FILE=data/sample_accounts.txt TYPE=iban"
	@exit 1
endif
	@mkdir -p output
	$(COMPOSE) run --rm swift batch-validate --file /data/$(notdir $(FILE)) --type $(TYPE) $(if $(OUTPUT),--output /app/output/$(notdir $(OUTPUT)))

# Start watcher service
watch:
	@mkdir -p output
	$(COMPOSE) --profile watch up -d swift-watcher
	@echo "Watcher started. Use 'make logs' to view output."

# Stop all services
stop:
	$(COMPOSE) --profile watch down

# Show logs
logs:
	$(COMPOSE) --profile watch logs -f

# Open shell in container
shell:
	$(COMPOSE) run --rm --entrypoint /bin/sh swift

# Run tests (in local Python environment)
test:
	@echo "Running tests..."
	pytest tests/ -v --tb=short || echo "pytest not installed. Run: pip install pytest"

# Format code with Black
format:
	@echo "Formatting code with Black..."
	black swift_cli/ tests/ --line-length 120
	@echo "✓ Code formatted"

# Lint code with flake8
lint:
	@echo "Linting code with flake8..."
	flake8 swift_cli/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 swift_cli/ --count --exit-zero --max-complexity=10 --max-line-length=120 --statistics

# Clean up
clean:
	$(COMPOSE) --profile watch down -v 2>/dev/null || true
	rm -rf output/*
	docker rmi $(IMAGE_NAME) 2>/dev/null || true
	@echo "✓ Cleanup complete"

# Quick examples
examples:
	@echo "╔══════════════════════════════════════════════════════════════╗"
	@echo "║                    SWIFT CLI Examples                        ║"
	@echo "╚══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "=== Installation ==="
	@echo "   make install         # Install via pip"
	@echo "   make install-dev     # Install with dev dependencies"
	@echo ""
	@echo "=== After pip install, use swift-cli directly ==="
	@echo "   swift-cli --help"
	@echo "   swift-cli validate-bic BNPAFRPPXXX"
	@echo "   swift-cli validate-iban FR7630006000011234567890189"
	@echo ""
	@echo "=== Docker commands (via make) ==="
	@echo "   make validate-bic BIC=BNPAFRPPXXX"
	@echo "   make validate-iban IBAN=\"FR7630006000011234567890189\""
	@echo "   make generate-pain001 CONFIG=data/sample_payment.json OUTPUT=message.xml"
	@echo "   make batch-validate FILE=data/sample_accounts.txt TYPE=iban OUTPUT=report.json"
	@echo "   make generate-mt103 CONFIG=data/sample_payment.json OUTPUT=mt103.txt"
	@echo ""
	@echo "=== Development ==="
	@echo "   make test            # Run tests"
	@echo "   make format          # Format code with Black"
	@echo "   make lint            # Lint code with flake8"
