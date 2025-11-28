# 🚀 Run Right Now - 3 Commands

## Copy and paste these 3 commands:

### 1. Navigate to project
```bash
cd /Users/sanandhan/code/kaggle-genai
```

### 2. Activate virtual environment
```bash
source venv/bin/activate
```

### 3. Set your API key and run
```bash
export GEMINI_API_KEY='paste-your-gemini-key-here'
python test_gemini_only.py
```

---

## 📝 Don't Have API Key Yet?

**Get it here:** https://makersuite.google.com/app/apikey

Steps:
1. Click "Create API Key"
2. Copy the key (starts with `AIza...`)
3. Paste it in the command above

---

## 🔧 The Script Will Try Multiple Models

The updated script now tries:
1. `gemini-pro` (most common)
2. `gemini-1.5-pro` (newer)
3. `gemini-1.0-pro` (stable)

It will use whichever one works with your API key!

---

## ✅ What to Expect

```
🔵🔵🔵 PURE GOOGLE STACK TEST 🔵🔵🔵
✅ Gemini API key found
🔧 Configuring Gemini...
🤖 Initializing Gemini model...
   Trying: gemini-pro...
✅ Model ready: gemini-pro
   
🤖 Sending to Gemini for review...
✅ Review received from Gemini!
[... code review results ...]
✅ SUCCESS - Pure Google Stack Working!
```

---

## 🐛 Still Getting Errors?

### Error: "GEMINI_API_KEY not set"
Make sure you ran: `export GEMINI_API_KEY='your-key'`

### Error: "No models available"  
Your API key might not have Gemini access. Check:
- Key is correct (starts with `AIza...`)
- API is enabled at: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

### Error: "404 not found"
The script now tries multiple model names automatically!

---

## 💡 Quick Test

Just want to see if it works? Run this one-liner:

```bash
cd /Users/sanandhan/code/kaggle-genai && source venv/bin/activate && export GEMINI_API_KEY='your-key' && python test_gemini_only.py
```

(Replace `your-key` with your actual Gemini API key)

---

**That's it! Just 3 commands to run!** 🚀


