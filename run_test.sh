#!/bin/bash

# Simple script to run the Gemini test

echo "🚀 Running Gemini Code Review Test"
echo "=================================="
echo ""

# Navigate to project
cd /Users/sanandhan/code/kaggle-genai

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Set API key
export GEMINI_API_KEY="${GEMINI_API_KEY:-your-api-key-here}"

# Run test
echo "🤖 Running test..."
echo ""
python test_gemini_only.py

echo ""
echo "✅ Done!"

