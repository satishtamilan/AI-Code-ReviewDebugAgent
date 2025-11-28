#!/bin/bash
# Quick start script for running the Jupyter notebook

echo "🚀 Code Review & Debug Agent - Jupyter Launcher"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo ""
    echo "Please install Python first:"
    echo "  macOS:   brew install python3"
    echo "  Ubuntu:  sudo apt install python3 python3-pip"
    echo "  Windows: Download from https://www.python.org/downloads/"
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if Jupyter is installed
if ! command -v jupyter &> /dev/null; then
    echo ""
    echo "📦 Installing Jupyter and dependencies..."
    python3 -m pip install --user jupyter notebook openai python-dotenv tenacity
    
    if [ $? -ne 0 ]; then
        echo "❌ Installation failed. Please install manually:"
        echo "   pip3 install jupyter notebook openai python-dotenv tenacity"
        exit 1
    fi
    echo "✓ Installation complete!"
fi

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "⚠️  OpenAI API key not set!"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    
    if [ -n "$api_key" ]; then
        export OPENAI_API_KEY="$api_key"
        echo "✓ API key set for this session"
    else
        echo ""
        echo "You can set it later by:"
        echo "  export OPENAI_API_KEY='your-key-here'"
        echo "or adding it to a .env file"
    fi
else
    echo "✓ OpenAI API key found"
fi

echo ""
echo "🎉 Starting Jupyter Notebook..."
echo ""
echo "The notebook will open in your default browser."
echo "Press Ctrl+C here to stop the server."
echo ""

# Launch Jupyter
jupyter notebook notebooks/submission.ipynb

