# How to Run the Code Review and Debug Agent

## Prerequisites

1. **Python 3.8+** installed on your system
2. **OpenAI API Key** (get one from https://platform.openai.com/api-keys)

## Option 1: Run Locally with Jupyter Notebook

### Step 1: Install Dependencies

Open your terminal and navigate to the project directory:

```bash
cd /Users/sanandhan/code/kaggle-genai
pip install -r requirements.txt
```

Or install manually:
```bash
pip install openai anthropic langchain langchain-openai python-dotenv pydantic tenacity jupyter notebook
```

### Step 2: Set Up API Key

Create a `.env` file in the project root:
```bash
# 1. Set Google API Key (Required)
# You can get this from Google AI Studio
export GEMINI_API_KEY='your-gemini-api-key'

# 2. Set Google Cloud Project (Required for Code Execution)
export GOOGLE_CLOUD_PROJECT='your-project-id'

# 3. Google Cloud Code Execution (Required for 'google_code_execution' tool)
# Format: projects/{PROJECT_ID}/locations/{LOCATION_ID}/reasoningEngines/{REASONING_ENGINE_ID}/sandboxEnvironments/{SANDBOX_ID}
export GOOGLE_SANDBOX_RESOURCE_NAME='your-sandbox-resource-name'

# 4. (Optional) MCP Server Configuration
export MCP_SERVER_CONFIG='[{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]}]'

# Note: OpenAI key is no longer required if using Gemini
# export OPENAI_API_KEY='...' 


# Optional: Google Cloud Code Execution (Required for 'google_code_execution' tool)
# Format: projects/{PROJECT_ID}/locations/{LOCATION_ID}/reasoningEngines/{REASONING_ENGINE_ID}/sandboxEnvironments/{SANDBOX_ID}
export GOOGLE_SANDBOX_RESOURCE_NAME='your-sandbox-resource-name'

# Optional: MCP Server Configuration (Required for MCP tools)
export MCP_SERVER_CONFIG='[{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]}]'

```

### Step 3: Launch Jupyter Notebook

```bash
jupyter notebook notebooks/submission.ipynb
```

This will open the notebook in your default web browser. Run cells by:
- Click on a cell and press `Shift + Enter` to run it
- Or use the "Run" button in the toolbar

### Step 4: Run All Cells

Once the notebook opens:
1. Go to **Cell** → **Run All** to execute all cells
2. Or run cells one by one with `Shift + Enter`

## Option 2: Run with JupyterLab (Modern Interface)

```bash
pip install jupyterlab
jupyter lab notebooks/submission.ipynb
```

## Option 3: Run with VS Code

1. Open VS Code
2. Install the "Jupyter" extension
3. Open `notebooks/submission.ipynb`
4. Click "Select Kernel" → Choose your Python environment
5. Run cells by clicking the play button or pressing `Shift + Enter`

## Option 4: Run the Python Scripts Directly

Instead of the notebook, you can run the Python example:

```bash
# Set your API key first
export OPENAI_API_KEY='your-api-key-here'

# Run the example script
python example.py
```

## Option 5: Run on Kaggle (For Competition Submission)

### Step 1: Upload to Kaggle

1. Go to https://www.kaggle.com/
2. Create a new notebook or upload `submission.ipynb`
3. Go to **Settings** → **Secrets** → **Add Secret**
4. Add your `OPENAI_API_KEY`

### Step 2: Modify API Key Setup

In the notebook, uncomment this section:
```python
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
os.environ['OPENAI_API_KEY'] = user_secrets.get_secret("OPENAI_API_KEY")
```

### Step 3: Run and Submit

1. Click **Run All** in the Kaggle notebook
2. Once successful, click **Submit to Competition**

## Quick Test (Command Line)

For a quick test without Jupyter:

```bash
# Test with Python interactive shell
python3 << EOF
import os
os.environ['OPENAI_API_KEY'] = 'your-key-here'

from agent import CodeReviewAgent

agent = CodeReviewAgent()
result = agent.review_code('''
def test():
    x = 1
    return x
''', language='python')

print(result)
EOF
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=agent

# Run specific test file
pytest tests/test_agent.py -v
```

## Troubleshooting

### Issue: "No module named 'openai'"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: "OpenAI API key not provided"
**Solution:** Set your API key:
```bash
export OPENAI_API_KEY='sk-...'
```

### Issue: Jupyter not found
**Solution:** Install Jupyter:
```bash
pip install jupyter notebook
```

### Issue: Rate limit errors from OpenAI
**Solution:** The agent has retry logic built-in. Wait a moment and try again.

## Next Steps

1. **Customize the Agent**: Edit `agent/code_reviewer.py` or `agent/debugger.py`
2. **Add More Languages**: Update `agent/utils.py` → `detect_language()`
3. **Improve Prompts**: Modify `agent/prompts.py`
4. **Test Locally**: Use `example.py` to test changes
5. **Submit to Kaggle**: Upload `submission.ipynb` to Kaggle

