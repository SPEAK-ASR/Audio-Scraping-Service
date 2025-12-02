#!/bin/bash

# Audio Scraping Service - Backend Installation Script
# This script installs all dependencies for the backend API service

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
echo -e "${BLUE}  Audio Scraping Service Installation${NC}"
echo -e "${BLUE}  (Backend API)${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo -e "${YELLOW}Please install Python 3.8 or higher${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

if ! command_exists pip3; then
    echo -e "${RED}Error: pip is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip detected${NC}\n"

# Create Python virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    cd "$SCRIPT_DIR"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}\n"
fi

# Install server dependencies
echo -e "${YELLOW}Installing server dependencies...${NC}"
cd "$SCRIPT_DIR"
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
echo -e "${GREEN}✓ Server dependencies installed${NC}\n"

# Create necessary directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p "$SCRIPT_DIR/output/completed"
echo -e "${GREEN}✓ Directories created${NC}\n"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo -e "${YELLOW}   Please create a .env file with required configuration:${NC}"
    echo -e "   - DATABASE_URL"
    echo -e "   - GCS_BUCKET_NAME"
    echo -e "   - SERVICE_ACCOUNT_B64 (optional)"
    echo -e "   - ALLOWED_ORIGINS (optional, defaults to *)${NC}\n"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Installation Complete!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "Next steps:"
echo -e "  1. Configure .env file"
echo -e "  2. Set up PostgreSQL database"
echo -e "  3. Configure Google Cloud Storage credentials"
echo -e "  4. Run './start.sh' to start the API server\n"
