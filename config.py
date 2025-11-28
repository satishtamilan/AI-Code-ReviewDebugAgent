"""
Configuration file for the Code Review and Debug Agent.
Built on Google Stack as required by competition.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import json

# Google Cloud Agent Engine Sandbox
# Format: projects/{PROJECT_ID}/locations/{LOCATION_ID}/reasoningEngines/{REASONING_ENGINE_ID}/sandboxEnvironments/{SANDBOX_ID}
GOOGLE_SANDBOX_RESOURCE_NAME = os.getenv("GOOGLE_SANDBOX_RESOURCE_NAME", "")

# MCP Server Configuration
# List of MCP servers to connect to. Each entry should be a dict with 'command' and 'args'
# Example: [{"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]}]
MCP_SERVER_CONFIG = json.loads(os.getenv("MCP_SERVER_CONFIG", "[]"))

# Project paths
PROJECT_ROOT = Path(__file__).parent
AGENT_DIR = PROJECT_ROOT / "agent"
TESTS_DIR = PROJECT_ROOT / "tests"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# API Keys (Google Stack Primary)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")

# OpenAI as fallback only
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model Configuration (Google Gemini by default)
USE_GEMINI = os.getenv("USE_GEMINI", "true").lower() == "true"
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-pro" if USE_GEMINI else "gpt-4-turbo-preview")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.2"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))  # Gemini supports more

# Agent Configuration
MAX_RETRIES = 3
TIMEOUT = 60  # seconds

# Code Review Settings
SEVERITY_LEVELS = ["critical", "high", "medium", "low", "info"]
SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "java",
    "cpp",
    "c",
    "go",
    "rust",
    "ruby",
    "php",
]

# Debug Settings
MAX_DEBUG_ITERATIONS = 5
ENABLE_AUTO_FIX = True


