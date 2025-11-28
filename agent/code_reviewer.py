"""
Code Review Agent - Main implementation.
"""
import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .prompts import (
    CODE_REVIEW_SYSTEM_PROMPT,
    CODE_REVIEW_USER_PROMPT,
    LANGUAGE_SPECIFIC_CHECKS,
)
from .utils import (
    detect_language,
    parse_json_response,
    sanitize_code,
    calculate_complexity_score,
    format_issue_report,
)
import config


class CodeReviewAgent:
    """
    An AI agent that performs comprehensive code reviews.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = None,
    ):
        """
        Initialize the Code Review Agent.
        
        Args:
            api_key: OpenAI API key (defaults to config)
            model: Model to use (defaults to config)
            temperature: Temperature for generation (defaults to config)
        """
        self.api_key = api_key or config.OPENAI_API_KEY
        self.model = model or config.DEFAULT_MODEL
        self.temperature = temperature if temperature is not None else config.TEMPERATURE
        
        # Gemini Support
        self.gemini_agent = None
        if config.USE_GEMINI:
            try:
                from .gemini_integration import GeminiCodeReviewAgent
                self.gemini_agent = GeminiCodeReviewAgent(
                    api_key=config.GEMINI_API_KEY,
                    model=config.DEFAULT_MODEL if "gemini" in config.DEFAULT_MODEL else "gemini-pro",
                    temperature=self.temperature
                )
                print(f"✓ CodeReviewAgent using Gemini ({self.gemini_agent.model_name})")
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini agent: {e}. Falling back to OpenAI.")

        if not self.gemini_agent:
            if not self.api_key:
                # Only raise if we strictly need OpenAI and don't have it
                # But if we wanted Gemini and failed, we might still need OpenAI
                pass 
                
            self.client = OpenAI(api_key=self.api_key)
        
        self.review_history: List[Dict[str, Any]] = []
    
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
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=config.MAX_TOKENS,
        )
        return response.choices[0].message.content
    
    def review_code(
        self,
        code: str,
        language: Optional[str] = None,
        filename: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform a comprehensive code review.
        
        Args:
            code: Source code to review
            language: Programming language (auto-detected if not provided)
            filename: Optional filename for better language detection
            context: Optional context about what the code should do
            
        Returns:
            Dict containing review results
        """
        # Delegate to Gemini if active
        if self.gemini_agent:
            return self.gemini_agent.review_code(code, language, filename, context)

        # Sanitize input
        code = sanitize_code(code)
        
        # Detect language if not provided
        if not language:
            language = detect_language(code, filename)
        
        # Calculate complexity metrics
        complexity = calculate_complexity_score(code, language)
        
        # Build the prompt
        user_prompt = CODE_REVIEW_USER_PROMPT.format(
            language=language,
            code=code,
        )
        
        if context:
            user_prompt += f"\n\nAdditional Context: {context}"
        
        # Add language-specific checks
        if language in LANGUAGE_SPECIFIC_CHECKS:
            checks = "\n".join(f"- {check}" for check in LANGUAGE_SPECIFIC_CHECKS[language])
            user_prompt += f"\n\nLanguage-specific checks for {language}:\n{checks}"
        
        messages = [
            {"role": "system", "content": CODE_REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]
        
        # Call LLM
        try:
            response = self._call_llm(messages)
            review_result = parse_json_response(response)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get review: {str(e)}",
                "language": language,
                "complexity": complexity,
            }
        
        # Enhance result with metadata
        result = {
            "success": True,
            "language": language,
            "complexity": complexity,
            "review": review_result,
            "formatted_report": format_issue_report(review_result.get("issues", [])),
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
        Review code from a file.
        
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
            }
    
    def batch_review(
        self,
        code_snippets: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Review multiple code snippets.
        
        Args:
            code_snippets: List of dicts with 'code' and optional 'language', 'filename'
            
        Returns:
            List of review results
        """
        results = []
        for snippet in code_snippets:
            result = self.review_code(
                code=snippet['code'],
                language=snippet.get('language'),
                filename=snippet.get('filename'),
                context=snippet.get('context'),
            )
            results.append(result)
        
        return results
    
    def get_summary_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics from review history.
        
        Returns:
            Dict with statistics
        """
        if not self.review_history:
            return {"total_reviews": 0}
        
        total_issues = 0
        issues_by_severity = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        languages_reviewed = {}
        
        for entry in self.review_history:
            result = entry.get("result", {})
            if result.get("success"):
                review = result.get("review", {})
                issues = review.get("issues", [])
                total_issues += len(issues)
                
                for issue in issues:
                    severity = issue.get("severity", "info")
                    issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
                
                lang = entry.get("language", "unknown")
                languages_reviewed[lang] = languages_reviewed.get(lang, 0) + 1
        
        return {
            "total_reviews": len(self.review_history),
            "total_issues": total_issues,
            "issues_by_severity": issues_by_severity,
            "languages_reviewed": languages_reviewed,
        }
    
    def export_history(self, filepath: str) -> None:
        """
        Export review history to a JSON file.
        
        Args:
            filepath: Path to save the history
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.review_history, f, indent=2)


