#!/bin/bash

# Audio Scraping Service - Backend Startup Script
# This script starts the FastAPI development server
# Note: Run install.sh first if you haven't installed dependencies

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
echo -e "${BLUE}  Audio Scraping Service - Backend${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Quick checks for required installations
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}Please run: ./install.sh${NC}"
    exit 1
fi

if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo -e "${YELLOW}   Server will use default settings${NC}\n"
fi

echo -e "${GREEN}✓ Dependencies verified${NC}\n"

# Function to cleanup background process on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down server...${NC}"
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null
    echo -e "${GREEN}Server stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start the server
echo -e "${BLUE}Starting FastAPI server...${NC}"
cd "$SCRIPT_DIR"
source .venv/bin/activate

# Check if running in production mode
if [ "$1" = "--prod" ]; then
    echo -e "${YELLOW}Running in production mode${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
else
    echo -e "${YELLOW}Running in development mode (use --prod for production)${NC}"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
fi

SERVER_PID=$!
deactivate

echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo -e "  API running at: ${BLUE}http://localhost:8000${NC}"
echo -e "  API docs at: ${BLUE}http://localhost:8000/docs${NC}\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Backend API is now running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop the server${NC}\n"

# Wait for the process
wait $SERVER_PID
