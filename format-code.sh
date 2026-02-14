#!/bin/bash
# ===========================================
# Script pour formater le code avec Black
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📝 Formatting Python code with Black..."

# Check if black is installed
if ! command -v black &> /dev/null; then
    echo "⚠️  Black not found. Installing..."
    pip install black
fi

# Format code
black swift_cli/ tests/ --line-length 120

echo "✅ Code formatted successfully!"
echo ""
echo "Run 'git diff' to see the changes."
