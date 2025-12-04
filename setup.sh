#!/data/data/com.termux/files/usr/bin/bash
# SoSoValue Bot Setup Script for Termux

echo "🚀 Installing SoSoValue Bot with Gmail Dot Trick..."
echo "📱 Optimized for Termux"

# Update packages
echo "🔄 Updating packages..."
pkg update -y && pkg upgrade -y

# Install required packages
echo "📦 Installing required packages..."
pkg install -y python git curl

# Install Python packages
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install requests beautifulsoup4 fake-useragent colorama schedule

# Create bot directory
echo "📁 Creating bot directory..."
cd ~
rm -rf SoSoValueBot
mkdir SoSoValueBot
cd SoSoValueBot

echo "📄 Creating bot files..."

# Create requirements.txt
cat > requirements.txt << 'EOF'
requests>=2.31.0
beautifulsoup4>=4.12.0
fake-useragent>=1.4.0
colorama>=0.4.6
schedule>=1.2.0
EOF

# Create config.json
cat > config.json << 'EOF'
{
  "referral_code": "NPH90834",
  "base_url": "https://www.sosovalue.com",
  "base_gmail": "",
  "max_accounts": 50,
  "daily_batch_size": 5,
  "delay_between_accounts": 10,
  "max_retries": 3,
  "termux_mode": true,
  "log_level": "INFO"
}
EOF

# Create directories
mkdir -p logs data

echo "✅ Installation complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure your Gmail:"
echo "   Run: python main.py"
echo "   Select option 4: Setup Gmail"
echo ""
echo "2. Create accounts:"
echo "   Select option 1: Create New Accounts"
echo ""
echo "3. Run daily tasks:"
echo "   Select option 2: Run Daily Tasks"
echo ""
echo "📱 Keep Termux open for best results!"
echo "🔋 Keep device charged and screen on"
echo ""
echo "🚀 To start: python main.py"