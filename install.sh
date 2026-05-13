#!/bin/bash

# Audio Scraping Service - Installation Script
# This script sets up the development environment and installs dependencies

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
echo -e "${BLUE}  Audio Scraping Service${NC}"
echo -e "${BLUE}  Installation Script${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check for Python 3.10
echo -e "${BLUE}Checking Python 3.10...${NC}"
if ! command -v python3.10 >/dev/null 2>&1; then
    echo -e "${RED}Error: Python 3.10 not found${NC}"
    echo -e "${YELLOW}Please install Python 3.10${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3.10 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

if ! command -v pip3 >/dev/null 2>&1; then
    echo -e "${RED}Error: pip not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ pip detected${NC}\n"

# Create virtual environment
echo -e "${BLUE}Setting up virtual environment...${NC}"
if [python3.10 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate virtual environment and upgrade pip
source .venv/bin/activate
pip install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}\n"

# Install PyTorch
echo -e "${BLUE}========================================${NC}"
echo "Select PyTorch version:"
echo "1) CUDA (GPU support)"
echo "2) CPU only"
read -p "Enter your choice (1 or 2): " pytorch_choice

if [ "$pytorch_choice" == "1" ]; then
    echo -e "\n${YELLOW}Installing PyTorch with CUDA support...${NC}"
    pip install torch==2.0.1+cu118 torchaudio==2.0.2+cu118 --index-url https://download.pytorch.org/whl/cu118
    echo -e "${GREEN}✓ PyTorch (CUDA) installed${NC}"
elif [ "$pytorch_choice" == "2" ]; then
    echo -e "\n${YELLOW}Installing PyTorch with CPU support...${NC}"
    pip install torch==2.0.1+cpu torchaudio==2.0.2+cpu --index-url https://download.pytorch.org/whl/cpu
    echo -e "${GREEN}✓ PyTorch (CPU) installed${NC}"
else
    echo -e "\n${RED}Invalid choice. Defaulting to CPU version...${NC}"
    pip install torch==2.0.1+cpu torchaudio==2.0.2+cpu --index-url https://download.pytorch.org/whl/cpu
    echo -e "${GREEN}✓ PyTorch (CPU) installed${NC}"
fi

# Install deepfilternet
echo -e "\n${YELLOW}Installing deepfilternet...${NC}"
pip install deepfilternet
echo -e "${GREEN}✓ deepfilternet installed${NC}"

# Install remaining dependencies
echo -e "\n${YELLOW}Installing remaining dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ All dependencies installed${NC}"

# Deactivate virtual environment
deactivate

# Create necessary directories
echo -e "\n${BLUE}Creating directories...${NC}"
mkdir -p "$SCRIPT_DIR/output/completed"
mkdir -p "$SCRIPT_DIR/logs"
echo -e "${GREEN}✓ Directories created${NC}"

# Check for .env file
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "\n${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo -e "${YELLOW}The service may not work correctly without proper configuration${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Installation complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\n${GREEN}Next steps:${NC}"
echo -e "1. Configure your .env file"
echo -e "2. Run ${BLUE}./start.sh${NC} to start the service"
echo -e "${BLUE}========================================${NC}\n not found${NC}"
fi

echo -e "${GREEN}Installation complete!${NC}"
