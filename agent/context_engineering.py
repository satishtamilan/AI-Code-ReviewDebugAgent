"""
Context Engineering: Context compaction and management.
Demonstrates: Context engineering, Token optimization, Summarization
"""
import re
from typing import List, Dict, Any, Optional


class ContextCompactor:
    """
    Manages context size through compaction and summarization.
    
    Implements:
    - Token counting
    - Context summarization
    - Intelligent truncation
    - Priority-based context selection
    """
    
    def __init__(self, max_tokens: int = 4000):
        """
        Initialize context compactor.
        
        Args:
            max_tokens: Maximum tokens to allow
        """
        self.max_tokens = max_tokens
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        
        Args:
            text: Text to estimate
            
        Returns:
            Estimated token count
        """
        # Rough estimate: ~4 characters per token on average
        return len(text) // 4
    
    def compact_code(
        self,
        code: str,
        preserve_structure: bool = True,
    ) -> str:
        """
        Compact code while preserving structure.
        
        Args:
            code: Code to compact
            preserve_structure: Whether to preserve structure
            
        Returns:
            Compacted code
        """
        lines = code.split('\n')
        compacted_lines = []
        
        for line in lines:
            # Remove excessive whitespace
            line = re.sub(r'\s+', ' ', line)
            line = line.strip()
            
            # Skip empty lines (unless preserving structure)
            if not line and not preserve_structure:
                continue
            
            # Remove single-line comments if not preserving structure
            if not preserve_structure and line.startswith('#'):
                continue
            
            compacted_lines.append(line)
        
        return '\n'.join(compacted_lines)
    
    def summarize_code_block(
        self,
        code: str,
        language: str = "python",
    ) -> str:
        """
        Create a summary of a code block.
        
        Args:
            code: Code to summarize
            language: Programming language
            
        Returns:
            Code summary
        """
        summary_parts = []
        
        # Extract functions/methods
        if language == "python":
            functions = re.findall(r'def\s+(\w+)\s*\([^)]*\):', code)
            if functions:
                summary_parts.append(f"Functions: {', '.join(functions)}")
            
            classes = re.findall(r'class\s+(\w+)', code)
            if classes:
                summary_parts.append(f"Classes: {', '.join(classes)}")
        
        elif language == "javascript":
            functions = re.findall(r'function\s+(\w+)\s*\(|const\s+(\w+)\s*=\s*\(', code)
            flat_functions = [f[0] or f[1] for f in functions]
            if flat_functions:
                summary_parts.append(f"Functions: {', '.join(flat_functions)}")
        
        # Count lines
        lines = code.split('\n')
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        summary_parts.append(f"{code_lines} lines of code")
        
        return "; ".join(summary_parts) if summary_parts else "Code block"
    
    def truncate_with_priority(
        self,
        items: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        priority_key: str = "priority",
    ) -> List[Dict[str, Any]]:
        """
        Truncate items based on priority.
        
        Args:
            items: List of items with priority
            max_tokens: Maximum tokens (uses self.max_tokens if not provided)
            priority_key: Key for priority value
            
        Returns:
            Truncated list of items
        """
        if max_tokens is None:
            max_tokens = self.max_tokens
        
        # Sort by priority (higher first)
        sorted_items = sorted(
            items,
            key=lambda x: x.get(priority_key, 0),
            reverse=True
        )
        
        # Add items until token limit
        selected_items = []
        current_tokens = 0
        
        for item in sorted_items:
            item_text = str(item.get("content", ""))
            item_tokens = self.estimate_tokens(item_text)
            
            if current_tokens + item_tokens <= max_tokens:
                selected_items.append(item)
                current_tokens += item_tokens
            else:
                break
        
        return selected_items
    
    def compact_conversation_history(
        self,
        history: List[Dict[str, Any]],
        keep_recent: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Compact conversation history by keeping recent and summarizing old.
        
        Args:
            history: Conversation history
            keep_recent: Number of recent messages to keep in full
            
        Returns:
            Compacted history
        """
        if len(history) <= keep_recent:
            return history
        
        # Keep recent messages
        recent = history[-keep_recent:]
        
        # Summarize older messages
        older = history[:-keep_recent]
        summary = {
            "role": "system",
            "content": f"[Earlier conversation summary: {len(older)} messages exchanged]",
            "is_summary": True,
        }
        
        return [summary] + recent
    
    def extract_key_information(
        self,
        text: str,
        max_length: int = 500,
    ) -> str:
        """
        Extract key information from text.
        
        Args:
            text: Text to extract from
            max_length: Maximum length of result
            
        Returns:
            Extracted key information
        """
        # Extract sentences with keywords
        sentences = re.split(r'[.!?]\s+', text)
        
        keywords = [
            'error', 'bug', 'issue', 'problem', 'fix', 'solution',
            'critical', 'important', 'must', 'should', 'warning',
        ]
        
        key_sentences = []
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                key_sentences.append(sentence)
        
        # If no key sentences, take first few sentences
        if not key_sentences:
            key_sentences = sentences[:3]
        
        result = '. '.join(key_sentences)
        
        # Truncate if too long
        if len(result) > max_length:
            result = result[:max_length] + "..."
        
        return result
    
    def optimize_prompt_context(
        self,
        prompt: str,
        code: str,
        additional_context: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """
        Optimize prompt context to fit within token limits.
        
        Args:
            prompt: Base prompt
            code: Code to include
            additional_context: Additional context items
            
        Returns:
            Optimized context dict
        """
        # Calculate token budget
        prompt_tokens = self.estimate_tokens(prompt)
        remaining_tokens = self.max_tokens - prompt_tokens - 500  # Reserve 500 for response
        
        # Allocate tokens
        code_budget = int(remaining_tokens * 0.7)  # 70% for code
        context_budget = int(remaining_tokens * 0.3)  # 30% for context
        
        # Compact code if necessary
        code_tokens = self.estimate_tokens(code)
        if code_tokens > code_budget:
            code = self.compact_code(code, preserve_structure=True)
            code_tokens = self.estimate_tokens(code)
            
            # If still too long, truncate
            if code_tokens > code_budget:
                char_limit = code_budget * 4
                code = code[:char_limit] + "\n... [truncated]"
        
        # Handle additional context
        context_text = ""
        if additional_context:
            combined_context = "\n".join(additional_context)
            context_tokens = self.estimate_tokens(combined_context)
            
            if context_tokens > context_budget:
                # Summarize context
                context_text = self.extract_key_information(
                    combined_context,
                    max_length=context_budget * 4
                )
            else:
                context_text = combined_context
        
        return {
            "prompt": prompt,
            "code": code,
            "context": context_text,
            "estimated_tokens": prompt_tokens + self.estimate_tokens(code) + self.estimate_tokens(context_text),
        }

