#!/bin/bash

# AI Emotion Tracking System - Start Script
# Activates virtual environment and starts the Flask server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}  AI Emotion Tracking System${NC}"
echo -e "${BLUE}===============================================${NC}"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source .venv311/bin/activate

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    echo "Please run: python3.11 -m venv .venv311"
    exit 1
fi

# Navigate to src directory
cd src

# Start the application
echo -e "${GREEN}Starting Flask server...${NC}"
echo ""
echo -e "${BLUE}Dashboard will be available at: http://localhost:5000${NC}"
echo -e "${BLUE}Press Ctrl+C to stop the server${NC}"
echo ""

python app.py


