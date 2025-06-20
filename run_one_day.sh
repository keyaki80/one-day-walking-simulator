#!/bin/bash

# One Day App Launcher
# A relaxing walking experience with seasonal and time-based variations

echo "🌅 One Day - A Relaxing Walking Experience 🌅"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

echo "✓ Python 3 found"

# Check if Pygame is installed
python3 -c "import pygame" 2> /dev/null
if [ $? -ne 0 ]; then
    echo "📦 Pygame is not installed. Installing now..."
    pip3 install pygame
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Pygame. Please install it manually:"
        echo "   pip3 install pygame"
        exit 1
    fi
fi

echo "✓ Pygame is available"

# Get current directory
SCRIPT_DIR="$(dirname "$0")"

# Check if the main Python file exists
if [ ! -f "$SCRIPT_DIR/one_day.py" ]; then
    echo "❌ one_day.py not found in $SCRIPT_DIR"
    exit 1
fi

echo "✓ Application file found"
echo ""
echo "🎮 Starting One Day..."
echo "   • Select your walking duration from the menu"
echo "   • Enjoy the seasonal scenery and time-based atmosphere"
echo "   • Press R to restart after completion"
echo "   • Close the window to exit"
echo ""

# Run the One Day app
python3 "$SCRIPT_DIR/one_day.py"

echo ""
echo "👋 Thanks for using One Day! Have a great day!"
