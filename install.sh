#!/bin/bash

# Audio Scraping Service - Backend Installation Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Checking Python 3.10...${NC}"
if ! command -v python3.10 >/dev/null 2>&1; then
    echo -e "${RED}Python 3.10 not found${NC}"
    echo -e "${YELLOW}Please install Python 3.10${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3.10 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

if ! command -v pip3 >/dev/null 2>&1; then
    echo -e "${RED}Error: pip not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip detected${NC}"

# Create virtual environment with python3.10
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo -e "${YELLOW}Creating virtual environment with Python 3.10...${NC}"
    python3.10 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Install dependencies
source .venv/bin/activate
pip install --upgrade pip

# Install PyTorch with CPU support first
echo -e "${YELLOW}Installing PyTorch (CPU version) and deepfilternet...${NC}"
pip install torch==1.13.1+cpu torchaudio==0.13.1+cpu -f https://download.pytorch.org/whl/torch_stable.html
pip install deepfilternet
echo -e "${GREEN}✓ PyTorch and deepfilternet installed${NC}"

# Install remaining dependencies
echo -e "${YELLOW}Installing remaining dependencies...${NC}"
pip install -r requirements.txt
deactivate
echo -e "${GREEN}✓ All dependencies installed${NC}"

mkdir -p "$SCRIPT_DIR/output/completed"
echo -e "${GREEN}✓ Directories created${NC}"

# .env check (optional)
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
fi

echo -e "${GREEN}Installation complete!${NC}"
