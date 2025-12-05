#!/bin/bash

# Audio Scraping Service - Backend Startup Script

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${RED}Virtual environment not found. Run install.sh first.${NC}"
    exit 1
fi

source .venv/bin/activate
python -V  # Should show 3.10.x

echo -e "${GREEN}✓ Using Python: $(python -V)${NC}"

# Start FastAPI
if [ "$1" = "--prod" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
else
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
fi

SERVER_PID=$!
deactivate

echo -e "${GREEN}Server started (PID: $SERVER_PID)${NC}"
wait $SERVER_PID
