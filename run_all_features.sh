#!/bin/bash

echo "🏆 Running COMPLETE Feature Demo"
echo "Including: Multi-Agent, MCP, Code Execution, Tools, Memory, Observability"
echo "=========================================================================="
echo ""

# Navigate to project
cd /Users/sanandhan/code/kaggle-genai

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Set API key
export GEMINI_API_KEY="${GEMINI_API_KEY:-your-api-key-here}"

echo ""
echo "================================================================"
echo "Running Enhanced Example with ALL 7 Features:"
echo "================================================================"
echo "1. Multi-Agent System (Sequential + Loop)"
echo "2. Custom Tools (4 analysis tools)"
echo "3. MCP (Model Context Protocol)"
echo "4. Code Execution (Google Cloud Sandbox)"
echo "5. Sessions & Memory"
echo "6. Observability (Logging + Tracing + Metrics)"
echo "7. Context Engineering"
echo ""
echo "🤖 Starting..."
echo ""

# Run pure Google demo (NO OpenAI - 100% Google)
python demo_pure_google.py

echo ""
echo "================================================================"
echo "✅ Complete Feature Demo Finished!"
echo "================================================================"

