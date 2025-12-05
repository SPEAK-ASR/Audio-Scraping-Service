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

# Setup cleanup function and trap BEFORE starting server
CLEANUP_DONE=0
cleanup() {
    if [ $CLEANUP_DONE -eq 1 ]; then
        return
    fi
    CLEANUP_DONE=1
    
    echo -e "\n${YELLOW}Shutting down server...${NC}"
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
    
    # Deactivate virtual environment if still active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    echo -e "${GREEN}Server stopped${NC}"
}
trap cleanup SIGINT SIGTERM EXIT

# Start FastAPI
if [ "$1" = "--prod" ]; then
    echo -e "${BLUE}Starting server in production mode...${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo -e "${BLUE}Starting server in development mode (with auto-reload)...${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi
