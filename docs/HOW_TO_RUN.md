# ✅ How to Run - Super Simple!

## 🎯 **One Command to Run Everything:**

```bash
cd /Users/sanandhan/code/kaggle-genai && ./run_test.sh
```

**That's it!** ✅

---

## 📋 **What the Script Does:**

The `run_test.sh` script automatically:
1. ✅ Navigates to project directory
2. ✅ Activates virtual environment
3. ✅ Sets your Gemini API key
4. ✅ Runs the test
5. ✅ Shows Gemini's code review

---

## 🔧 **Manual Steps (if you prefer):**

If you want to run commands manually:

```bash
# 1. Go to project
cd /Users/sanandhan/code/kaggle-genai

# 2. Activate virtual environment (IMPORTANT!)
source venv/bin/activate

# 3. Set API key
export GEMINI_API_KEY='your-api-key-here'

# 4. Run test
python test_gemini_only.py
```

---

## ⚠️ **Why "command not found: python"?**

This happens when you haven't activated the virtual environment.

### ❌ **Wrong:**
```bash
python test_gemini_only.py  # ERROR: python not found
```

### ✅ **Right:**
```bash
source venv/bin/activate     # Activate venv first
python test_gemini_only.py   # Now it works!
```

---

## 🚀 **Quick Commands:**

### Run the test:
```bash
./run_test.sh
```

### Check available models:
```bash
./run_test.sh  # Change this to run diagnose_api.py
```

### Or use Python directly:
```bash
cd /Users/sanandhan/code/kaggle-genai
source venv/bin/activate
python test_gemini_only.py
```

---

## 💡 **Key Points:**

1. ✅ Always activate venv first: `source venv/bin/activate`
2. ✅ Or use the script: `./run_test.sh`
3. ✅ Your API key is already in the script
4. ✅ You have 62 models available
5. ✅ Using `gemini-2.5-flash` (fast + high quota)

---

## 📊 **Your Setup:**

| Item | Status |
|------|--------|
| Virtual environment | ✅ Created at `/Users/sanandhan/code/kaggle-genai/venv` |
| API Key | ✅ `AIzaSyDv8Robk1QGQJZEtHBLO_QEgS0H8MJ4xbA` |
| Models available | ✅ 62 models |
| Recommended model | ✅ `gemini-2.5-flash` |
| Run script | ✅ `./run_test.sh` |

---

## ✅ **What You'll See:**

```
🔵 PURE GOOGLE STACK TEST

✅ Gemini API key found
🤖 Finding available Gemini models...
   Found 40 available models
   Using: models/gemini-2.5-flash
✅ Model ready!

Testing Code Review with Gemini
================================

[Code being reviewed]

🤖 Sending to Gemini for review...
✅ Review received from Gemini!

[Gemini's detailed code review with bugs and improvements]

✅ SUCCESS - Pure Google Stack Working!
```

---

**Just run:** `./run_test.sh` 🚀

