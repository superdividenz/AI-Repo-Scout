#!/bin/bash

# AI Repo Scout - Enhanced Setup with DeepSeek Integration
# This script sets up AI Repo Scout with both DeepSeek and Hugging Face support

echo "🚀 AI Repo Scout - Enhanced Setup with DeepSeek Integration"
echo "============================================================"

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

# Check for API keys
echo ""
echo "🔑 Checking API Configuration..."

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  No GITHUB_TOKEN environment variable found."
    echo "   You can still use the tool with rate limits (60 requests/hour)"
    echo "   To increase limits, get a GitHub token from: https://github.com/settings/tokens"
    echo "   Then export GITHUB_TOKEN=your_token_here"
else
    echo "✅ GitHub token found"
fi

# Check for DeepSeek API key
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  No DEEPSEEK_API_KEY environment variable found."
    echo "   DeepSeek provides superior AI analysis compared to free models"
    echo "   Get your API key from: https://platform.deepseek.com/"
    echo "   Then export DEEPSEEK_API_KEY=your_deepseek_key_here"
    echo "   The system will fallback to free Hugging Face models"
else
    echo "✅ DeepSeek API key found - Enhanced AI analysis enabled!"
fi

# Create data directory
mkdir -p data
echo "✅ Data directory created"

# Create reports directory
mkdir -p reports
echo "✅ Reports directory created"

# Create environment file template
if [ ! -f ".env.example" ]; then
    cat > .env.example << 'EOF'
# GitHub API Configuration
GITHUB_TOKEN=your_github_token_here

# DeepSeek AI Configuration (Optional but recommended)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Usage:
# 1. Copy this file to .env
# 2. Replace the values with your actual API keys
# 3. Source the file: source .env
EOF
    echo "✅ Created .env.example template"
fi

# Run a quick test
echo "🧪 Running enhanced test..."
python3 -c "
import sys
sys.path.append('src')
try:
    from enhanced_ai_analyzer import EnhancedAIAnalyzer
    print('✅ Enhanced AI Analyzer imported successfully')
    
    # Test configuration loading
    analyzer = EnhancedAIAnalyzer()
    print('✅ AI Analyzer initialized successfully')
    
    if analyzer.deepseek_client:
        print('✅ DeepSeek integration active - Premium AI features enabled!')
    else:
        print('ℹ️  Using Hugging Face models - DeepSeek key not configured')
        
except Exception as e:
    print(f'❌ Enhanced test failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Enhanced test passed"
else
    echo "❌ Enhanced test failed"
    exit 1
fi

echo ""
echo "🎉 Enhanced setup complete! Here's what you can do:"
echo ""
echo "1. 📊 Generate enhanced reports with DeepSeek AI:"
echo "   export DEEPSEEK_API_KEY=your_key_here"
echo "   python3 src/main.py --timeframe daily --languages python javascript"
echo ""
echo "2. 🌐 Launch the enhanced dashboard:"
echo "   streamlit run src/dashboard.py"
echo ""
echo "3. 🤖 Try AI-powered analysis:"
echo "   python3 examples/usage_examples.py"
echo ""
echo "4. ⚙️ Set up API keys:"
echo "   cp .env.example .env"
echo "   # Edit .env with your API keys"
echo "   source .env"
echo ""
echo "5. 🚀 Deploy to Streamlit Cloud with DeepSeek:"
echo "   - Fork this repository"
echo "   - Visit: https://streamlit.io/cloud"
echo "   - Add DEEPSEEK_API_KEY in Streamlit secrets"
echo "   - Set entry point to: src/dashboard.py"
echo ""
echo "📚 Enhanced Features Available:"
echo "✨ Superior AI summaries with DeepSeek"
echo "✨ Advanced trend analysis and insights"
echo "✨ Intelligent recommendations"
echo "✨ Better repository categorization"
echo "✨ Fallback to free Hugging Face models"
echo ""
echo "🔑 API Key Setup:"
echo "• GitHub Token: https://github.com/settings/tokens (Free)"
echo "• DeepSeek API: https://platform.deepseek.com/ (Paid but very affordable)"
echo ""
echo "Happy repository scouting with enhanced AI! 🕵️‍♂️🤖"