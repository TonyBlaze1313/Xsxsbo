#!/data/data/com.termux/files/usr/bin/bash
# SoSoValue Bot - Quick Start Script

cd ~/SoSoValueBot

echo "🤖 Starting SoSoValue Bot..."
echo "⏰ $(date)"

# Check if Python packages are installed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

# Run the bot
python main.py