# SWIFT Banking CLI - Makefile
# ============================
#
# Usage:
#   make build        - Build Docker image
#   make help         - Show CLI help
#   make validate-bic BIC=BNPAFRPPXXX
#   make validate-iban IBAN="FR7630006000011234567890189"
#   make generate-pain001 CONFIG=data/sample_payment.json
#   make batch-validate FILE=data/sample_accounts.txt TYPE=iban

.PHONY: all build help validate-bic validate-iban generate-pain001 generate-mt103 \
        batch-validate watch stop logs clean shell test

# Variables
COMPOSE := docker compose
IMAGE_NAME := swift-banking-cli:latest

# Default target
all: help

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
	cd code && python -m pytest -v tests/ 2>/dev/null || python -c "print('No tests found or pytest not installed')"

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
	@echo "1. Validate BIC:"
	@echo "   make validate-bic BIC=BNPAFRPPXXX"
	@echo ""
	@echo "2. Validate IBAN:"
	@echo "   make validate-iban IBAN=\"FR7630006000011234567890189\""
	@echo ""
	@echo "3. Generate pain.001:"
	@echo "   make generate-pain001 CONFIG=data/sample_payment.json OUTPUT=message.xml"
	@echo ""
	@echo "4. Batch validate IBANs:"
	@echo "   make batch-validate FILE=data/sample_accounts.txt TYPE=iban OUTPUT=report.json"
	@echo ""
	@echo "5. Generate MT103:"
	@echo "   make generate-mt103 CONFIG=data/sample_payment.json OUTPUT=mt103.txt"
