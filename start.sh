#!/bin/bash

# Audio Scraping Service - Startup Script
# This script starts both the client and server concurrently

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$SCRIPT_DIR/client"
SERVER_DIR="$SCRIPT_DIR/server"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Audio Scraping Service Startup${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists node; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}\n"

# Check if client dependencies are installed
echo -e "${YELLOW}Checking client dependencies...${NC}"
if [ ! -d "$CLIENT_DIR/node_modules" ]; then
    echo -e "${YELLOW}Installing client dependencies...${NC}"
    cd "$CLIENT_DIR"
    npm install
    echo -e "${GREEN}✓ Client dependencies installed${NC}\n"
else
    echo -e "${GREEN}✓ Client dependencies already installed${NC}\n"
fi

# Check if server virtual environment exists
if [ ! -d "$SERVER_DIR/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd "$SERVER_DIR"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Check if server dependencies are installed
echo -e "${YELLOW}Checking server dependencies...${NC}"
cd "$SERVER_DIR"
source .venv/bin/activate

# Check if a marker file exists indicating successful installation
# and if requirements.txt hasn't been modified since then
REQUIREMENTS_INSTALLED_MARKER=".venv/.requirements_installed"

if [ -f "$REQUIREMENTS_INSTALLED_MARKER" ] && \
   [ "$REQUIREMENTS_INSTALLED_MARKER" -nt "requirements.txt" ]; then
    echo -e "${GREEN}✓ Server dependencies already installed${NC}\n"
else
    echo -e "${YELLOW}Installing server dependencies...${NC}"
    pip install -r requirements.txt
    # Create marker file to indicate successful installation
    touch "$REQUIREMENTS_INSTALLED_MARKER"
    echo -e "${GREEN}✓ Server dependencies installed${NC}\n"
fi

deactivate

# Create log directory if it doesn't exist
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    kill $CLIENT_PID $SERVER_PID 2>/dev/null
    wait $CLIENT_PID $SERVER_PID 2>/dev/null
    echo -e "${GREEN}Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start the server
echo -e "${BLUE}Starting FastAPI server...${NC}"
cd "$SERVER_DIR"
source .venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > "$LOG_DIR/server.log" 2>&1 &
SERVER_PID=$!
deactivate
echo -e "${GREEN}✓ Server started (PID: $SERVER_PID)${NC}"
echo -e "  Server running at: ${BLUE}http://localhost:8000${NC}"
echo -e "  Server logs: ${BLUE}$LOG_DIR/server.log${NC}\n"

# Wait a bit for the server to start
sleep 2

# Start the client
echo -e "${BLUE}Starting Vite development server...${NC}"
cd "$CLIENT_DIR"
npm run dev > "$LOG_DIR/client.log" 2>&1 &
CLIENT_PID=$!
echo -e "${GREEN}✓ Client started (PID: $CLIENT_PID)${NC}"
echo -e "  Client running at: ${BLUE}http://localhost:5173${NC}"
echo -e "  Client logs: ${BLUE}$LOG_DIR/client.log${NC}\n"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Both services are now running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop both services${NC}\n"

# Wait for both processes
wait $CLIENT_PID $SERVER_PID
