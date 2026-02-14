#!/bin/bash
#
# SWIFT Banking CLI - Wrapper Script
# ===================================
#
# Script helper pour exécuter le CLI SWIFT via Docker
#
# Usage:
#   ./swift-cli.sh <command> [options]
#
# Exemples:
#   ./swift-cli.sh validate-bic BNPAFRPPXXX
#   ./swift-cli.sh validate-iban "FR7630006000011234567890189"
#   ./swift-cli.sh generate-pain001 --config data/sample_payment.json
#   ./swift-cli.sh batch-validate --file data/sample_accounts.txt --type iban
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get current user UID/GID for permission handling
CURRENT_UID=$(id -u)
CURRENT_GID=$(id -g)

# Docker compose V2 command (new integrated plugin)
if docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo -e "${RED}Error: Docker Compose V2 is required. Please update Docker.${NC}"
    echo -e "${YELLOW}Install with: sudo apt-get install docker-compose-plugin${NC}"
    exit 1
fi

# Functions
show_help() {
    cat << EOF
${BLUE}╔══════════════════════════════════════════════════════════════╗
║           SWIFT Banking CLI - Docker Helper                   ║
╚══════════════════════════════════════════════════════════════╝${NC}

${GREEN}Usage:${NC}
    $0 <command> [options]

${GREEN}Commands:${NC}
    build                   Build the Docker image
    help                    Show CLI help
    validate-bic <bic>      Validate a BIC/SWIFT code
    validate-iban <iban>    Validate an IBAN
    generate-pain001        Generate ISO 20022 pain.001 message
    generate-mt103          Generate SWIFT MT103 message
    batch-validate          Validate a file of BIC/IBAN codes
    shell                   Open a shell in the container

${GREEN}Script Commands:${NC}
    stop                    Stop all running containers
    clean                   Remove generated files and containers

${GREEN}Examples:${NC}
    $0 build
    $0 validate-bic BNPAFRPPXXX
    $0 validate-iban "FR76 3000 6000 0112 3456 7890 189"
    $0 generate-pain001 --config /data/sample_payment.json --output /app/output/payment.xml
    $0 batch-validate --file /data/sample_accounts.txt --type iban --output /app/output/report.json
    $0 generate-mt103 --amount 1500 --currency EUR --debtor-name "ABC Corp" \\
        --debtor-iban FR7630006000011234567890189 --debtor-bic BNPAFRPPXXX \\
        --creditor-name "XYZ Ltd" --creditor-iban DE89370400440532013000 \\
        --creditor-bic COBADEFFXXX

EOF
}

build_image() {
    echo -e "${BLUE}Building SWIFT CLI Docker image...${NC}"
    $COMPOSE_CMD build
    echo -e "${GREEN}✓ Build complete${NC}"
}

run_command() {
    # Create output directory if it doesn't exist
    mkdir -p "$SCRIPT_DIR/output"
    
    # Run the command with current user UID/GID to avoid permission issues
    $COMPOSE_CMD run --rm --user "${CURRENT_UID}:${CURRENT_GID}" swift "$@"
}

stop_services() {
    echo -e "${BLUE}Stopping all SWIFT services...${NC}"
    $COMPOSE_CMD down 2>/dev/null || true
    echo -e "${GREEN}✓ Services stopped${NC}"
}

clean_all() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    
    # Stop containers
    $COMPOSE_CMD down -v 2>/dev/null || true
    
    # Remove output files
    if [ -d "$SCRIPT_DIR/output" ]; then
        rm -rf "$SCRIPT_DIR/output"/* 2>/dev/null || true
        echo -e "${GREEN}✓ Cleaned output directory${NC}"
    fi
    
    # Remove docker images
    docker rmi swift-banking-cli:latest 2>/dev/null || true
    
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

open_shell() {
    echo -e "${BLUE}Opening shell in SWIFT container...${NC}"
    $COMPOSE_CMD run --rm --user "${CURRENT_UID}:${CURRENT_GID}" --entrypoint /bin/sh swift
}

# Main
case "${1:-}" in
    build)
        build_image
        ;;
    help|--help|-h|"")
        show_help
        ;;
    stop)
        stop_services
        ;;
    clean)
        clean_all
        ;;
    shell)
        open_shell
        ;;
    validate-bic|validate-iban|generate-pain001|generate-mt103|batch-validate)
        # Build image if not exists
        if ! docker images | grep -q "swift-banking-cli"; then
            build_image
        fi
        run_command "$@"
        ;;
    *)
        # Pass through to the container
        if ! docker images | grep -q "swift-banking-cli"; then
            build_image
        fi
        run_command "$@"
        ;;
esac
