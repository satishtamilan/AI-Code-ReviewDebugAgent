# 🔍 API Key Diagnostics

## The Problem

Your API key doesn't have access to `gemini-pro` or other models. This means:
- ❌ Wrong API key type
- ❌ API not enabled  
- ❌ Key from wrong Google service

---

## ✅ Run This Diagnostic

```bash
cd /Users/sanandhan/code/kaggle-genai
source venv/bin/activate
export GEMINI_API_KEY='your-key-here'
python diagnose_api.py
```

This will tell you:
1. ✅ If your API key is valid
2. ✅ What models are available
3. ✅ What model name to use

---

## 🔑 Get the CORRECT API Key

### ⚠️ IMPORTANT: Use Google AI Studio (NOT Google Cloud)

There are TWO different APIs:
1. **Google AI Studio** ✅ (FREE, easy setup) - USE THIS
2. **Google Cloud Vertex AI** ❌ (Complex, needs billing) - DON'T USE

### Steps to Get Correct Key:

1. **Visit:** https://makersuite.google.com/app/apikey  
   (This is Google AI Studio - the free one!)

2. **Sign in** with Google account

3. **Click:** "Create API Key" button

4. **Copy** the key (starts with `AIza...`)

5. **Use it:**
   ```bash
   export GEMINI_API_KEY='AIza_your_new_key'
   ```

---

## 🎯 Common Issues

### Issue 1: Wrong API Key Type
**Problem:** You got key from Google Cloud Console (wrong place)  
**Solution:** Get key from AI Studio: https://makersuite.google.com/app/apikey

### Issue 2: API Not Enabled
**Problem:** Gemini API not enabled for your project  
**Solution:** Use AI Studio (automatically enabled) not Cloud Console

### Issue 3: Key Doesn't Start with "AIza"
**Problem:** Wrong type of credential  
**Solution:** Create new API key (not service account, not OAuth)

---

## 📋 Two Ways to Get Gemini API Key

### ✅ WAY 1: Google AI Studio (RECOMMENDED)
- **URL:** https://makersuite.google.com/app/apikey
- **Free:** 60 requests/minute
- **Setup:** 30 seconds
- **Key format:** `AIzaSy...`
- **Use for:** Development, testing, Kaggle

### ❌ WAY 2: Google Cloud Vertex AI (Complex)
- **URL:** https://console.cloud.google.com/
- **Requires:** Project, billing, service account
- **Setup:** 30 minutes
- **Different API:** Uses Vertex AI SDK
- **Use for:** Production with billing

**For Kaggle competition: Use AI Studio (Way 1)!**

---

## 🚀 Quick Fix (3 Steps)

```bash
# 1. Get NEW key from AI Studio
# Visit: https://makersuite.google.com/app/apikey

# 2. Run diagnostic
cd /Users/sanandhan/code/kaggle-genai
source venv/bin/activate
export GEMINI_API_KEY='your-NEW-key-here'
python diagnose_api.py

# 3. If diagnostic passes, run test
python test_gemini_only.py
```

---

## ✅ What Success Looks Like

When diagnostic runs successfully:

```
🔍 GEMINI API DIAGNOSTICS

✅ API Key found
   Key: AIzaSy... (example format)
   Length: 39 characters

✅ API configured successfully

✅ Found 5 models!

✅ Models you can use:
   📦 models/gemini-pro
   📦 models/gemini-1.5-pro
   
✅ SUCCESS - Your API key works!
💡 Use this model: models/gemini-pro
```

---

## 🔧 After Diagnostic Passes

If diagnostic shows available models, update the test script with the correct model name:

```bash
# It will tell you something like:
# "Use this model: models/gemini-pro"

# Then run:
python test_gemini_only.py
```

---

## 💡 Key Points

1. ✅ Use **Google AI Studio** (https://makersuite.google.com/)
2. ✅ Create **API Key** (not service account)
3. ✅ Key should start with `AIza`
4. ✅ Free tier: 60 requests/minute
5. ✅ Run `diagnose_api.py` to verify

---

**Run the diagnostic now to see exactly what's wrong!** 🔍

```bash
export GEMINI_API_KEY='your-key'
python diagnose_api.py
```


