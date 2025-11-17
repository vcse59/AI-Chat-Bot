#!/bin/bash
# Run Tests (Mac/Linux)

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT/tests"

echo "============================================"
echo "Running Test Suite"
echo "============================================"
echo

source venv/bin/activate
pytest -v

echo
echo "============================================"
echo "✅ Tests complete"
echo "============================================"
echo
