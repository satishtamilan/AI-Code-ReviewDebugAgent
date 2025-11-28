# 🚀 Quick Start Guide

## For Kaggle Competition (Easiest - No Installation Required!)

### Method 1: Run on Kaggle Platform ⭐ RECOMMENDED

1. Open https://www.kaggle.com/
2. Sign in to your account
3. Go to: https://www.kaggle.com/competitions/agents-intensive-capstone-project
4. Click **"Code"** tab → **"New Notebook"**
5. Click **File** → **Upload Notebook** → Select `notebooks/submission.ipynb`
6. Add your OpenAI API key:
   - Click **"Add-ons"** → **"Secrets"**
   - Add new secret: `OPENAI_API_KEY` = `your-key-here`
7. In the notebook, uncomment these lines:
   ```python
   from kaggle_secrets import UserSecretsClient
   user_secrets = UserSecretsClient()
   os.environ['OPENAI_API_KEY'] = user_secrets.get_secret("OPENAI_API_KEY")
   ```
8. Click **"Run All"** (▶▶ button at the top)
9. When ready to submit: **"Submit to Competition"**

**✅ This is the easiest way - everything runs in the cloud!**

---

## For Local Development

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- OpenAI API key

### Step-by-Step Setup

#### 1️⃣ Install Python (if needed)

**On macOS:**
```bash
brew install python3
```

**On Windows:**
Download from https://www.python.org/downloads/

**On Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

#### 2️⃣ Install Required Packages

Open terminal/command prompt in this directory:
```bash
cd /Users/sanandhan/code/kaggle-genai
pip3 install jupyter notebook openai python-dotenv tenacity
```

Or install all requirements:
```bash
pip3 install -r requirements.txt
```

#### 3️⃣ Set Up Your API Key

Create a file called `.env` in this directory with:
```
OPENAI_API_KEY=your-actual-api-key-here
```

Or set it in terminal (temporary):
```bash
export OPENAI_API_KEY='your-key-here'
```

#### 4️⃣ Run the Notebook

```bash
jupyter notebook notebooks/submission.ipynb
```

This opens your browser. Click on cells and press **Shift + Enter** to run them.

---

## Alternative: Run Python Script Instead

If you prefer not to use Jupyter:

```bash
# Set API key
export OPENAI_API_KEY='your-key-here'

# Run example
python3 example.py
```

---

## Using VS Code (Visual Studio Code)

1. Open VS Code
2. Install "Python" and "Jupyter" extensions
3. Open folder: `/Users/sanandhan/code/kaggle-genai`
4. Open `notebooks/submission.ipynb`
5. Click "Select Kernel" → Pick your Python installation
6. Run cells with the ▶ button

---

## Testing the Agent

Quick test in Python:

```python
from agent import CodeReviewAgent

# Initialize agent
agent = CodeReviewAgent(api_key='your-key-here')

# Review some code
result = agent.review_code('''
def calculate_sum(a, b):
    return a + b
''', language='python')

print(result)
```

---

## Project Structure

```
kaggle-genai/
├── agent/              # Main agent code
│   ├── code_reviewer.py
│   ├── debugger.py
│   ├── prompts.py
│   └── utils.py
├── notebooks/
│   └── submission.ipynb  # 👈 Your Kaggle submission
├── tests/              # Unit tests
├── example.py          # Demo script
├── requirements.txt    # Dependencies
└── README.md          # Documentation
```

---

## Getting an OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in
3. Click your profile → "API Keys"
4. Click "Create new secret key"
5. Copy the key (starts with `sk-...`)
6. **Save it securely** - you won't see it again!

---

## Need Help?

- **Kaggle Competition**: https://www.kaggle.com/competitions/agents-intensive-capstone-project
- **OpenAI API Docs**: https://platform.openai.com/docs
- **Jupyter Docs**: https://jupyter-notebook.readthedocs.io/

---

## ⚡ TL;DR - Fastest Way

```bash
# For Kaggle: Just upload submission.ipynb to Kaggle and run there!

# For local:
pip3 install jupyter openai tenacity
export OPENAI_API_KEY='your-key'
jupyter notebook notebooks/submission.ipynb
```

