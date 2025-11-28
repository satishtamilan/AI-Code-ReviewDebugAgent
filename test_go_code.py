import os
import sys

# Don't import the agent package to avoid OpenAI dependency
import google.generativeai as genai

print("=" * 70)
print("Testing Go Code Analysis with Pure Google Stack")
print("=" * 70)

# Read the Go code
with open('test_golang.go', 'r') as f:
    go_code = f.read()

print("\nGo Code to Review:")
print("-" * 70)
print(go_code[:500] + "...")
print("-" * 70)

# Initialize Gemini
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("\nError: GEMINI_API_KEY not set!")
    print("Run: export GEMINI_API_KEY='your-key-here'")
    sys.exit(1)

genai.configure(api_key=api_key)

# List available models and pick the best one
print("\nFinding best Gemini model...")
available_models = []
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    # Prioritize Flash models for speed
    model_name = None
    for priority in ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-pro', 'gemini-1.5-pro', 'gemini-1.0-pro']:
        for m in available_models:
            if priority in m:
                model_name = m
                break
        if model_name:
            break
    
    if not model_name:
        model_name = available_models[0] if available_models else 'gemini-pro'
    
    print(f"Using model: {model_name}")
    
except Exception as e:
    print(f"Warning: Could not list models ({e}), using gemini-pro")
    model_name = 'gemini-pro'

model = genai.GenerativeModel(model_name)

print("\nAnalyzing Go code with Gemini...")
print("-" * 70)

prompt = f"""You are an expert code reviewer. Analyze this Go code and provide:

1. List all bugs and errors
2. Security vulnerabilities
3. Performance issues
4. Best practice violations
5. Suggested fixes

Go Code:
```go
{go_code}
```

Provide detailed analysis with line numbers."""

try:
    response = model.generate_content(prompt)
    
    print("\nReview Results:")
    print("=" * 70)
    print(response.text)
    print("=" * 70)
    
    print("\nKey Issues to Look For:")
    print("1. Division by zero vulnerability in ProcessData")
    print("2. SQL injection vulnerability in UserLogin")
    print("3. Index out of bounds in ParseConfig")
    print("\n✅ Go code analysis complete!")
    
except Exception as e:
    print(f"\nError during analysis: {e}")
    import traceback
    traceback.print_exc()
