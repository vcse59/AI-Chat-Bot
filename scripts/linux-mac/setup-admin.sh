#!/bin/bash
# Setup Admin User Script (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "============================================"
echo "Admin User Setup"
echo "============================================"
echo

# Check if auth-service venv exists
if [ ! -f "$PROJECT_ROOT/auth-service/venv/bin/python" ]; then
    echo "ERROR: Auth service virtual environment not found!"
    echo "Please run setup-venv.sh first"
    echo
    exit 1
fi

# Run the setup script using auth-service venv
"$PROJECT_ROOT/auth-service/venv/bin/python" "$PROJECT_ROOT/scripts/linux-mac/setup-admin.py" "$@"

echo
