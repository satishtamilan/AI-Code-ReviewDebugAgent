"""
List available Gemini models
Run this to see which models you can use
"""
import os
import google.generativeai as genai

print("🔍 Checking Available Gemini Models")
print("=" * 60)

# Check for API key
gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

if not gemini_key:
    print("❌ Error: GEMINI_API_KEY not set!")
    print("\n📝 To fix:")
    print("   1. Get key from: https://makersuite.google.com/app/apikey")
    print("   2. Run: export GEMINI_API_KEY='your-key-here'")
    print("   3. Run this script again")
    exit(1)

print(f"✅ API Key found: {gemini_key[:10]}...")

# Configure Gemini
genai.configure(api_key=gemini_key)

print("\n📋 Available Models:")
print("-" * 60)

try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"\n✅ {model.name}")
            print(f"   Display Name: {model.display_name}")
            print(f"   Description: {model.description[:80]}...")
            print(f"   Supports: {', '.join(model.supported_generation_methods)}")
    
    print("\n" + "=" * 60)
    print("✅ Models listed successfully!")
    print("\n💡 Recommended model: gemini-1.5-pro or gemini-pro")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nCheck:")
    print("   1. API key is correct")
    print("   2. Internet connection works")
    print("   3. API key has Gemini access")


