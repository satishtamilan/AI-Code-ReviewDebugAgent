#!/bin/bash

echo "📦 Codebase Analysis Tool"
echo "================================================================"

cd /Users/sanandhan/code/kaggle-genai

# Activate virtual environment
source venv/bin/activate

# Set API key
export GEMINI_API_KEY="${GEMINI_API_KEY:-your-api-key-here}"

echo ""
echo "Analyzing your codebase..."
echo ""

# Run analyzer
python codebase_analyzer.py "$@"

