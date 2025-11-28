"""
Diagnose Gemini API Key Issues
This will tell you exactly what's wrong with your API setup.
"""
import os
import google.generativeai as genai

print("\n" + "🔍" * 35)
print(" " * 15 + "GEMINI API DIAGNOSTICS")
print("🔍" * 35 + "\n")

# Check for API key
gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')

if not gemini_key:
    print("❌ GEMINI_API_KEY not set!")
    print("\n📝 Fix:")
    print("   export GEMINI_API_KEY='your-key-here'")
    exit(1)

print("✅ API Key found")
print(f"   Key: {gemini_key[:15]}...")
print(f"   Length: {len(gemini_key)} characters")

if not gemini_key.startswith('AIza'):
    print("\n⚠️  WARNING: Key doesn't start with 'AIza'")
    print("   This might not be a valid Gemini API key!")
    print("   Get correct key from: https://makersuite.google.com/app/apikey")

print("\n" + "="*60)
print("Step 1: Configuring API")
print("="*60)

try:
    genai.configure(api_key=gemini_key)
    print("✅ API configured successfully")
except Exception as e:
    print(f"❌ Failed to configure: {e}")
    exit(1)

print("\n" + "="*60)
print("Step 2: Listing Available Models")
print("="*60)

try:
    models = list(genai.list_models())
    
    if not models:
        print("\n❌ NO MODELS AVAILABLE!")
        print("\nPossible reasons:")
        print("   1. API key is for wrong service (not AI Studio)")
        print("   2. Gemini API not enabled for your project")
        print("   3. API key doesn't have permission")
        print("\n📝 Solutions:")
        print("   1. Get NEW key from: https://makersuite.google.com/app/apikey")
        print("   2. Make sure you're using 'Google AI Studio' not 'Google Cloud'")
        print("   3. Click 'Get API Key' then 'Create API Key'")
    else:
        print(f"\n✅ Found {len(models)} models!\n")
        
        # List models that support generateContent
        content_models = [m for m in models if 'generateContent' in m.supported_generation_methods]
        
        if content_models:
            print("✅ Models you can use for code review:")
            print("-" * 60)
            for model in content_models:
                print(f"\n📦 {model.name}")
                print(f"   Display Name: {model.display_name}")
                if hasattr(model, 'description'):
                    desc = model.description[:100]
                    print(f"   Description: {desc}...")
            
            print("\n" + "="*60)
            print("✅ SUCCESS - Your API key works!")
            print("="*60)
            
            # Show recommended model
            recommended = None
            for model in content_models:
                if 'gemini-pro' in model.name.lower():
                    recommended = model.name
                    break
            
            if not recommended and content_models:
                recommended = content_models[0].name
            
            if recommended:
                print(f"\n💡 Use this model: {recommended}")
                print(f"\nTo use it, update test_gemini_only.py:")
                print(f"   model = genai.GenerativeModel('{recommended}')")
        else:
            print("\n⚠️  Models found but none support generateContent")
            print("This shouldn't happen with a valid AI Studio key")
            
except Exception as e:
    print(f"\n❌ Error listing models: {e}")
    print("\n🔧 This usually means:")
    print("   1. API key is invalid")
    print("   2. API key is for wrong Google service")
    print("   3. Gemini API not enabled")
    print("\n📝 Get correct key:")
    print("   Visit: https://makersuite.google.com/app/apikey")
    print("   Click: 'Create API Key' (in Google AI Studio)")
    print("   Copy the new key")

print("\n" + "🔍" * 35)
print(" " * 15 + "DIAGNOSTICS COMPLETE")
print("🔍" * 35 + "\n")


