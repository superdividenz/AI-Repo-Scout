#!/bin/bash

# AI Repo Scout - Quick Start Script
# This script sets up and runs AI Repo Scout for the first time

echo "🚀 AI Repo Scout - Quick Start Setup"
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✅ Dependencies installed successfully"

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  No GITHUB_TOKEN environment variable found."
    echo "   You can still use the tool with rate limits (60 requests/hour)"
    echo "   To increase limits, get a GitHub token from: https://github.com/settings/tokens"
    echo "   Then export GITHUB_TOKEN=your_token_here"
else
    echo "✅ GitHub token found"
fi

# Create data directory
mkdir -p data
echo "✅ Data directory created"

# Run a quick test
echo "🧪 Running quick test..."
python3 src/main.py --timeframe daily --languages python --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Quick test passed"
else
    echo "❌ Quick test failed"
    exit 1
fi

echo ""
echo "🎉 Setup complete! Here's what you can do:"
echo ""
echo "1. 📊 Generate a daily report:"
echo "   python3 src/main.py --timeframe daily --languages python javascript"
echo ""
echo "2. 🌐 Launch the dashboard:"
echo "   streamlit run src/dashboard.py"
echo ""
echo "3. 🔄 Run continuous monitoring:"
echo "   python3 src/main.py --continuous --interval 24"
echo ""
echo "4. 📖 View example reports:"
echo "   ls reports/"
echo ""
echo "5. 🚀 Deploy to Streamlit Cloud:"
echo "   Visit: https://streamlit.io/cloud"
echo "   Connect this repository and set entry point to: src/dashboard.py"
echo ""
echo "Happy repository scouting! 🕵️‍♂️"