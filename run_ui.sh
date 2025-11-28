#!/bin/bash

echo "🌐 Starting Beautiful Web UI for Code Review Agent"
echo "================================================================"

# Check if Python HTTP server is available
if command -v python3 &> /dev/null; then
    echo "✅ Python 3 found"
    echo ""
    echo "🚀 Starting web server..."
    echo "📱 Open your browser and go to:"
    echo ""
    echo "   http://localhost:8000/web_ui.html"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    cd /Users/sanandhan/code/kaggle-genai
    python3 -m http.server 8000
else
    echo "❌ Python 3 not found"
    echo "Please install Python 3 first"
    exit 1
fi

