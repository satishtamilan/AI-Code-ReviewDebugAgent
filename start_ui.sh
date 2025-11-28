#!/bin/bash

echo "🚀 Starting AI Code Review Agent with Beautiful UI"
echo "================================================================"

cd /Users/sanandhan/code/kaggle-genai

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Set API key
export GEMINI_API_KEY="${GEMINI_API_KEY:-your-api-key-here}"

# Install Flask and CORS if not installed
pip install flask flask-cors --quiet

echo ""
echo "================================================================"
echo "✅ Starting server with live tracking..."
echo "================================================================"
echo ""
echo "🌐 Open your browser to: http://localhost:5001"
echo ""
echo "Features available:"
echo "  ✓ Real-time code analysis"
echo "  ✓ Multi-language support (Python, JS, Go, Java, C++, Rust)"
echo "  ✓ Live session tracking"
echo "  ✓ Memory bank visualization"
echo "  ✓ Observability metrics"
echo "  ✓ Analysis history"
echo "  ✓ Beautiful modern UI"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================================================"
echo ""

python app_ui.py

