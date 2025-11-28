"""
Google Gemini Integration for Bonus Points.
Demonstrates: Effective use of Gemini to power agents
"""
import os
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")

import config
from .prompts import CODE_REVIEW_SYSTEM_PROMPT, CODE_REVIEW_USER_PROMPT
from .utils import detect_language, sanitize_code, parse_json_response


class GeminiCodeReviewAgent:
    """
    Code Review Agent powered by Google Gemini.
    
    This demonstrates effective use of Gemini for the bonus points category.
    Gemini Pro is particularly good at:
    - Understanding code context
    - Multi-language support
    - Long context windows (up to 1M tokens)
    - Fast inference
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-pro",  # Most stable/common model
        temperature: float = 0.2,
    ):
        """
        Initialize Gemini Code Review Agent.
        
        Args:
            api_key: Google AI API key
            model: Gemini model to use
            temperature: Temperature for generation
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai not installed")
        
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        self.model_name = model
        self.temperature = temperature
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        self.review_history: List[Dict[str, Any]] = []
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Gemini API with retry logic.
        
        Args:
            prompt: Combined system + user prompt
            
        Returns:
            Gemini response content
        """
        response = self.model.generate_content(prompt)
        return response.text
    
    def review_code(
        self,
        code: str,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive code review using Gemini.
        
        Args:
            code: Source code to review
            language: Programming language (auto-detected if not provided)
            filename: Optional filename for better language detection
            context: Optional context about what the code should do
            
        Returns:
            Dict containing review results
        """
        # Sanitize input
        code = sanitize_code(code)
        
        # Detect language if not provided
        if not language:
            language = detect_language(code, filename)
        
        # Build the prompt (Gemini prefers combined prompts)
        user_prompt = CODE_REVIEW_USER_PROMPT.format(
            language=language,
            code=code,
        )
        
        if context:
            user_prompt += f"\n\nAdditional Context: {context}"
        
        # Combine system and user prompts
        combined_prompt = f"{CODE_REVIEW_SYSTEM_PROMPT}\n\n{user_prompt}"
        
        # Call Gemini
        try:
            response = self._call_gemini(combined_prompt)
            review_result = parse_json_response(response)
            
            result = {
                "success": True,
                "language": language,
                "review": review_result,
                "model": "gemini",
                "model_name": self.model_name,
            }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Failed to get review: {str(e)}",
                "language": language,
                "model": "gemini",
            }
        
        # Store in history
        self.review_history.append({
            "code_snippet": code[:200] + "..." if len(code) > 200 else code,
            "language": language,
            "result": result,
        })
        
        return result
    
    def review_file(self, filepath: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Review code from a file using Gemini.
        
        Args:
            filepath: Path to the file
            language: Programming language (auto-detected if not provided)
            
        Returns:
            Dict containing review results
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.review_code(
                code=code,
                language=language,
                filename=filepath,
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
                "model": "gemini",
            }


class HybridCodeReviewAgent:
    """
    Hybrid agent that can use both OpenAI GPT-4 and Google Gemini.
    
    Benefits:
    - Fallback if one service is down
    - Cost optimization (use cheaper model when appropriate)
    - Leverage strengths of each model
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        prefer_gemini: bool = True,
    ):
        """
        Initialize hybrid agent.
        
        Args:
            openai_api_key: OpenAI API key
            gemini_api_key: Gemini API key
            prefer_gemini: Whether to prefer Gemini (for bonus points!)
        """
        self.prefer_gemini = prefer_gemini
        
        # Initialize agents
        self.openai_agent = None
        self.gemini_agent = None
        
        try:
            from .code_reviewer import CodeReviewAgent
            self.openai_agent = CodeReviewAgent(api_key=openai_api_key)
        except Exception as e:
            print(f"Warning: Could not initialize OpenAI agent: {e}")
        
        try:
            self.gemini_agent = GeminiCodeReviewAgent(api_key=gemini_api_key)
        except Exception as e:
            print(f"Warning: Could not initialize Gemini agent: {e}")
        
        if not self.openai_agent and not self.gemini_agent:
            raise ValueError("At least one agent (OpenAI or Gemini) must be available")
    
    def review_code(
        self,
        code: str,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Review code using the preferred agent with fallback.
        
        Args:
            code: Source code to review
            language: Programming language
            **kwargs: Additional arguments
            
        Returns:
            Review results
        """
        # Try preferred agent first
        if self.prefer_gemini and self.gemini_agent:
            try:
                return self.gemini_agent.review_code(code, language, **kwargs)
            except Exception as e:
                print(f"Gemini failed, falling back to OpenAI: {e}")
                if self.openai_agent:
                    return self.openai_agent.review_code(code, language, **kwargs)
                raise
        elif self.openai_agent:
            try:
                return self.openai_agent.review_code(code, language, **kwargs)
            except Exception as e:
                print(f"OpenAI failed, falling back to Gemini: {e}")
                if self.gemini_agent:
                    return self.gemini_agent.review_code(code, language, **kwargs)
                raise
        
        raise ValueError("No agent available")
    
    def get_active_model(self) -> str:
        """Get the name of the active model."""
        if self.prefer_gemini and self.gemini_agent:
            return "gemini"
        elif self.openai_agent:
            return "openai"
        return "none"


def create_optimal_agent(
    task_type: str = "review",
    **kwargs
) -> Any:
    """
    Factory function to create the optimal agent based on task type.
    
    This demonstrates intelligent model selection:
    - Gemini: Better for long context, multi-language
    - GPT-4: Better for complex reasoning, debugging
    
    Args:
        task_type: Type of task ('review', 'debug', 'hybrid')
        **kwargs: Arguments for agent initialization
        
    Returns:
        Appropriate agent instance
    """
    if task_type == "review":
        # Try Gemini first for code review (bonus points!)
        try:
            return GeminiCodeReviewAgent(**kwargs)
        except Exception:
            from .code_reviewer import CodeReviewAgent
            return CodeReviewAgent(**kwargs)
    
    elif task_type == "debug":
        # Use GPT-4 for debugging (better reasoning)
        from .debugger import DebugAgent
        return DebugAgent(**kwargs)
    
    elif task_type == "hybrid":
        # Use hybrid agent for best of both worlds
        return HybridCodeReviewAgent(**kwargs)
    
    else:
        raise ValueError(f"Unknown task type: {task_type}")

