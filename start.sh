#!/bin/bash

# Audio Scraping Service - Startup Script
# This script starts the backend API service

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Audio Scraping Service Startup${NC}"
echo -e "${BLUE}  (Backend API)${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if virtual environment exists
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}Please run: ./install.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment verified${NC}"

# Activate virtual environment
source .venv/bin/activate
python -V  # Should show 3.10.x

echo -e "${GREEN}✓ Using Python: $(python -V)${NC}"

# Update yt-dlp
echo -e "\n${BLUE}Updating yt-dlp to latest version...${NC}"
python -m pip install --upgrade yt-dlp
echo -e "${GREEN}✓ yt-dlp updated${NC}"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "\n${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo -e "${YELLOW}The service may not work correctly without proper configuration${NC}\n"
else
    echo -e "${GREEN}✓ Configuration file found${NC}"
fi

# Create log directory if it doesn't exist
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Function to cleanup background processes on exit
CLEANUP_DONE=0
cleanup() {
    if [ $CLEANUP_DONE -eq 1 ]; then
        return
    fi
    CLEANUP_DONE=1
    
    echo -e "\n${YELLOW}Shutting down service...${NC}"
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
        wait $SERVER_PID 2>/dev/null || true
    fi
    
    # Deactivate virtual environment if still active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate
    fi
    
    echo -e "${GREEN}Service stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start the server
echo -e "\n${BLUE}Starting backend API server...${NC}"
cd "$SCRIPT_DIR"

# Determine mode
if [ "$1" = "--prod" ]; then
    echo -e "${YELLOW}Running in production mode${NC}\n"
    MODE_FLAG=""
else
    echo -e "${YELLOW}Running in development mode (with auto-reload)${NC}\n"
    MODE_FLAG="--reload"
fi

echo -e "${GREEN}✓ Backend API service started${NC}\n"
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Backend API Service${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}API Base URL:${NC}           http://localhost:8000"
echo -e "${GREEN}API Documentation:${NC}      http://localhost:8000/docs"
echo -e "${GREEN}ReDoc:${NC}                  http://localhost:8000/redoc"
echo -e "${GREEN}Health Check:${NC}           http://localhost:8000/health"
echo -e "${GREEN}Server logs:${NC}            $LOG_DIR/server.log"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}Note: This service handles audio scraping${NC}"
echo -e "${YELLOW}and processing from YouTube sources.${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop the service${NC}\n"

# Run uvicorn with live output
if [ "$1" = "--prod" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level info 2>&1 | tee "$LOG_DIR/server.log" &
else
    uvicorn app.main:app $MODE_FLAG --host 0.0.0.0 --port 8000 --log-level info 2>&1 | tee "$LOG_DIR/server.log" &
fi
SERVER_PID=$!

# Wait for the process
wait $SERVER_PID
