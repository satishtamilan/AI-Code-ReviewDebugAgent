#!/bin/bash

echo "🔵 Google Stack Quick Start"
echo "=============================="
echo ""

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set"
    echo ""
    echo "📝 Please follow these steps:"
    echo ""
    echo "1️⃣  Get your Gemini API key:"
    echo "    Visit: https://makersuite.google.com/app/apikey"
    echo "    Click: 'Create API Key'"
    echo "    Copy the key (starts with AIza...)"
    echo ""
    echo "2️⃣  Set the environment variable:"
    echo "    export GEMINI_API_KEY='your-api-key-here'"
    echo ""
    echo "3️⃣  Run this script again:"
    echo "    ./QUICK_START.sh"
    echo ""
    exit 1
fi

echo "✅ GEMINI_API_KEY is set"
echo "   Key: ${GEMINI_API_KEY:0:10}..."
echo ""

# Navigate to project directory
cd /Users/sanandhan/code/kaggle-genai

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "✅ Virtual environment activated"
echo ""

# Option 1: List available models
echo "Choose what to run:"
echo ""
echo "1) List available Gemini models"
echo "2) Run Google Stack test (code review)"
echo "3) Both"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "📋 Listing Gemini models..."
        python list_gemini_models.py
        ;;
    2)
        echo ""
        echo "🤖 Running Google Stack test..."
        python test_gemini_only.py
        ;;
    3)
        echo ""
        echo "📋 Listing models first..."
        python list_gemini_models.py
        echo ""
        echo "🤖 Now running test..."
        python test_gemini_only.py
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"


