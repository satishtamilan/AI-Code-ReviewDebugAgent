"""
Debug Agent - Identifies and fixes bugs in code.
"""
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .prompts import (
    DEBUG_SYSTEM_PROMPT,
    DEBUG_USER_PROMPT,
    ERROR_CONTEXT_TEMPLATE,
    AUTO_FIX_PROMPT,
)
from .utils import (
    detect_language,
    parse_json_response,
    sanitize_code,
    get_line_context,
)
import config


class DebugAgent:
    """
    An AI agent that debugs code and suggests fixes.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = None,
    ):
        """
        Initialize the Debug Agent.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Model to use (defaults to config)
            temperature: Temperature for generation (defaults to config)
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else config.TEMPERATURE
        
        # Gemini Support
        self.use_gemini = config.USE_GEMINI
        self.gemini_model = None
        
        if self.use_gemini:
            try:
                import google.generativeai as genai
                gemini_key = config.GEMINI_API_KEY
                if not gemini_key:
                    raise ValueError("GEMINI_API_KEY not found")
                
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel(
                    model_name=config.DEFAULT_MODEL if "gemini" in config.DEFAULT_MODEL else "gemini-pro",
                    generation_config={
                        "temperature": self.temperature,
                        "max_output_tokens": config.MAX_TOKENS,
                    }
                )
                print(f"✓ DebugAgent using Gemini ({config.DEFAULT_MODEL})")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini for DebugAgent: {e}. Falling back to OpenAI.")
                self.use_gemini = False

        if not self.use_gemini:
            if not self.api_key:
                 # Only raise if we strictly need OpenAI and don't have it
                 pass
            self.client = OpenAI(api_key=self.api_key)
            
        self.debug_history: List[Dict[str, Any]] = []
    
    @retry(
        stop=stop_after_attempt(config.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Call the LLM with retry logic.
        
        Args:
            messages: List of message dicts
            
        Returns:
            LLM response content
        """
        if self.use_gemini and self.gemini_model:
            # Convert messages to Gemini format (simplified)
            # Gemini prefers a single prompt or specific history structure
            prompt = ""
            for msg in messages:
                role = msg["role"]
                content = msg["content"]
                prompt += f"{role.upper()}: {content}\n\n"
            
            response = self.gemini_model.generate_content(prompt)
            return response.text

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=config.MAX_TOKENS,
        )
        return response.choices[0].message.content
    
    def debug_code(
        self,
        code: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        language: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Debug code and identify the root cause of issues.
        
        Args:
            code: Source code with bug
            error_message: Error message if available
            stack_trace: Stack trace if available
            expected_behavior: What should happen
            actual_behavior: What actually happens
            language: Programming language (auto-detected if not provided)
            filename: Optional filename for better language detection
            
        Returns:
            Dict containing debug results
        """
        # Sanitize input
        code = sanitize_code(code)
        
        # Detect language if not provided
        if not language:
            language = detect_language(code, filename)
        
        # Build error context
        error_context = ""
        if any([error_message, stack_trace, expected_behavior, actual_behavior]):
            error_context = ERROR_CONTEXT_TEMPLATE.format(
                error_message=error_message or "Not provided",
                stack_trace=stack_trace or "Not provided",
                expected_behavior=expected_behavior or "Not provided",
                actual_behavior=actual_behavior or "Not provided",
            )
        
        # Build the prompt
        user_prompt = DEBUG_USER_PROMPT.format(
            language=language,
            code=code,
            error_context=error_context,
        )
        
        messages = [
            {"role": "system", "content": DEBUG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        
        # Call LLM
        try:
            response = self._call_llm(messages)
            debug_result = parse_json_response(response)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to debug: {str(e)}",
                "language": language,
            }
        
        # Add context around bug location
        if "bug_location" in debug_result and "line" in debug_result["bug_location"]:
            line_num = debug_result["bug_location"]["line"]
            debug_result["bug_context"] = get_line_context(code, line_num)
        
        result = {
            "success": True,
            "language": language,
            "debug": debug_result,
            "original_code": code,
        }
        
        # Store in history
        self.debug_history.append({
            "code_snippet": code[:200] + "..." if len(code) > 200 else code,
            "error_message": error_message,
            "language": language,
            "result": result,
        })
        
        return result
    
    def auto_fix(
        self,
        code: str,
        issue_description: str,
        language: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Automatically generate a fixed version of the code.
        
        Args:
            code: Source code with issue
            issue_description: Description of the issue to fix
            language: Programming language (auto-detected if not provided)
            filename: Optional filename for better language detection
            
        Returns:
            Dict containing the fixed code
        """
        # Sanitize input
        code = sanitize_code(code)
        
        # Detect language if not provided
        if not language:
            language = detect_language(code, filename)
        
        # Build the prompt
        user_prompt = AUTO_FIX_PROMPT.format(
            language=language,
            code=code,
            issue_description=issue_description,
        )
        
        messages = [
            {"role": "system", "content": "You are an expert code fixer. Generate only the fixed code without explanations."},
            {"role": "user", "content": user_prompt},
        ]
        
        # Call LLM
        try:
            response = self._call_llm(messages)
            
            # Extract code from response
            from .utils import extract_code_blocks
            code_blocks = extract_code_blocks(response)
            
            if code_blocks:
                fixed_code = code_blocks[0]['code']
            else:
                fixed_code = response.strip()
            
            return {
                "success": True,
                "original_code": code,
                "fixed_code": fixed_code,
                "language": language,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to auto-fix: {str(e)}",
                "language": language,
            }
    
    def debug_file(
        self,
        filepath: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        expected_behavior: Optional[str] = None,
        actual_behavior: Optional[str] = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Debug code from a file.
        
        Args:
            filepath: Path to the file
            error_message: Error message if available
            stack_trace: Stack trace if available
            expected_behavior: What should happen
            actual_behavior: What actually happens
            language: Programming language (auto-detected if not provided)
            
        Returns:
            Dict containing debug results
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                code = f.read()
            
            return self.debug_code(
                code=code,
                error_message=error_message,
                stack_trace=stack_trace,
                expected_behavior=expected_behavior,
                actual_behavior=actual_behavior,
                language=language,
                filename=filepath,
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to read file: {str(e)}",
            }
    
    def iterative_debug(
        self,
        code: str,
        test_function: callable,
        max_iterations: int = None,
        language: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Iteratively debug code by testing and fixing.
        
        Args:
            code: Source code to debug
            test_function: Function that tests the code and returns (success, error_msg)
            max_iterations: Maximum debug iterations (defaults to config)
            language: Programming language (auto-detected if not provided)
            
        Returns:
            Dict containing final result
        """
        if max_iterations is None:
            max_iterations = config.MAX_DEBUG_ITERATIONS
        
        current_code = code
        iteration_history = []
        
        for iteration in range(max_iterations):
            # Test current code
            success, error_msg = test_function(current_code)
            
            if success:
                return {
                    "success": True,
                    "fixed_code": current_code,
                    "iterations": iteration + 1,
                    "history": iteration_history,
                }
            
            # Debug the code
            debug_result = self.debug_code(
                code=current_code,
                error_message=error_msg,
                language=language,
            )
            
            if not debug_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to debug code",
                    "iterations": iteration + 1,
                    "history": iteration_history,
                }
            
            # Get fixed code
            fixed_code = debug_result.get("debug", {}).get("fixed_code")
            
            if not fixed_code or fixed_code == current_code:
                return {
                    "success": False,
                    "error": "No fix generated or code unchanged",
                    "iterations": iteration + 1,
                    "history": iteration_history,
                }
            
            iteration_history.append({
                "iteration": iteration + 1,
                "error": error_msg,
                "debug_result": debug_result,
            })
            
            current_code = fixed_code
        
        return {
            "success": False,
            "error": f"Max iterations ({max_iterations}) reached without fix",
            "last_code": current_code,
            "iterations": max_iterations,
            "history": iteration_history,
        }
    
    def get_debug_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics from debug history.
        
        Returns:
            Dict with statistics
        """
        if not self.debug_history:
            return {"total_debugs": 0}
        
        successful_fixes = sum(1 for entry in self.debug_history 
                              if entry.get("result", {}).get("success"))
        languages_debugged = {}
        common_errors = {}
        
        for entry in self.debug_history:
            lang = entry.get("language", "unknown")
            languages_debugged[lang] = languages_debugged.get(lang, 0) + 1
            
            error_msg = entry.get("error_message", "")
            if error_msg:
                # Extract error type (simplified)
                error_type = error_msg.split(":")[0] if ":" in error_msg else "Unknown"
                common_errors[error_type] = common_errors.get(error_type, 0) + 1
        
        return {
            "total_debugs": len(self.debug_history),
            "successful_fixes": successful_fixes,
            "success_rate": successful_fixes / len(self.debug_history),
            "languages_debugged": languages_debugged,
            "common_errors": common_errors,
        }
    
    def export_history(self, filepath: str) -> None:
        """
        Export debug history to a JSON file.
        
        Args:
            filepath: Path to save the history
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.debug_history, f, indent=2)


