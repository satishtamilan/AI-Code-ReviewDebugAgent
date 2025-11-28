"""
Utility functions for the code review and debug agent.
"""
import re
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


def detect_language(code: str, filename: Optional[str] = None) -> str:
    """
    Detect the programming language of the given code.
    
    Args:
        code: Source code string
        filename: Optional filename to help with detection
        
    Returns:
        Detected language name
    """
    if filename:
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
        }
        ext = Path(filename).suffix.lower()
        if ext in extension_map:
            return extension_map[ext]
    
    # Pattern-based detection
    patterns = {
        'python': [r'def\s+\w+\s*\(', r'import\s+\w+', r'from\s+\w+\s+import', r'if\s+__name__\s*=='],
        'javascript': [r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=', r'=>', r'console\.log'],
        'typescript': [r'interface\s+\w+', r'type\s+\w+\s*=', r':\s*\w+(\[\])?(\s*=>)?'],
        'java': [r'public\s+class', r'private\s+\w+\s+\w+', r'System\.out\.println'],
        'cpp': [r'#include\s*<', r'std::', r'int\s+main\s*\('],
        'go': [r'func\s+\w+\s*\(', r'package\s+\w+', r'import\s+\('],
        'rust': [r'fn\s+\w+\s*\(', r'let\s+mut', r'impl\s+\w+'],
    }
    
    for lang, lang_patterns in patterns.items():
        for pattern in lang_patterns:
            if re.search(pattern, code):
                return lang
    
    return 'unknown'


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    Extract code blocks from markdown-formatted text.
    
    Args:
        text: Text containing markdown code blocks
        
    Returns:
        List of dicts with 'language' and 'code' keys
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    
    blocks = []
    for lang, code in matches:
        blocks.append({
            'language': lang if lang else 'unknown',
            'code': code.strip()
        })
    
    return blocks


def parse_json_response(response: str) -> Dict[str, Any]:
    """
    Parse JSON from LLM response, handling markdown code blocks.
    
    Args:
        response: LLM response text
        
    Returns:
        Parsed JSON dict
    """
    # Try direct parsing first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try extracting from code block
    code_blocks = extract_code_blocks(response)
    for block in code_blocks:
        if block['language'] in ['json', '']:
            try:
                return json.loads(block['code'])
            except json.JSONDecodeError:
                continue
    
    # Try extracting JSON object pattern
    json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\}))*\}'
    matches = re.findall(json_pattern, response, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    raise ValueError("Could not parse JSON from response")


def count_lines(code: str) -> int:
    """Count the number of lines in code."""
    return len(code.splitlines())


def get_line_context(code: str, line_number: int, context_lines: int = 3) -> str:
    """
    Get code context around a specific line.
    
    Args:
        code: Full source code
        line_number: Target line number (1-indexed)
        context_lines: Number of lines before/after to include
        
    Returns:
        Code snippet with context
    """
    lines = code.splitlines()
    start = max(0, line_number - context_lines - 1)
    end = min(len(lines), line_number + context_lines)
    
    context = []
    for i in range(start, end):
        prefix = ">>> " if i == line_number - 1 else "    "
        context.append(f"{prefix}{i + 1:4d} | {lines[i]}")
    
    return "\n".join(context)


def calculate_complexity_score(code: str, language: str) -> Dict[str, Any]:
    """
    Calculate basic complexity metrics for code.
    
    Args:
        code: Source code
        language: Programming language
        
    Returns:
        Dict with complexity metrics
    """
    lines = code.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]
    
    # Basic metrics
    total_lines = len(lines)
    code_lines = len(non_empty_lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith('#') or 
                       line.strip().startswith('//'))
    
    # Cyclomatic complexity (simplified)
    decision_keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', 'and', 'or']
    complexity = 1  # Base complexity
    for line in non_empty_lines:
        for keyword in decision_keywords:
            complexity += line.count(f' {keyword} ') + line.count(f' {keyword}(')
    
    return {
        'total_lines': total_lines,
        'code_lines': code_lines,
        'comment_lines': comment_lines,
        'complexity': complexity,
        'comment_ratio': comment_lines / code_lines if code_lines > 0 else 0,
    }


def sanitize_code(code: str) -> str:
    """
    Sanitize code input by removing dangerous patterns.
    
    Args:
        code: Raw code input
        
    Returns:
        Sanitized code
    """
    # Remove potential script injections (basic)
    code = re.sub(r'<script[^>]*>.*?</script>', '', code, flags=re.DOTALL | re.IGNORECASE)
    
    return code.strip()


def format_issue_report(issues: List[Dict[str, Any]]) -> str:
    """
    Format issues into a readable report.
    
    Args:
        issues: List of issue dicts
        
    Returns:
        Formatted report string
    """
    if not issues:
        return "No issues found! ✓"
    
    report = []
    report.append(f"Found {len(issues)} issue(s):\n")
    
    # Group by severity
    severity_order = ['critical', 'high', 'medium', 'low', 'info']
    by_severity = {s: [] for s in severity_order}
    
    for issue in issues:
        severity = issue.get('severity', 'info')
        by_severity[severity].append(issue)
    
    for severity in severity_order:
        severity_issues = by_severity[severity]
        if not severity_issues:
            continue
        
        icon = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵', 'info': '⚪️'}
        report.append(f"\n{icon[severity]} {severity.upper()} ({len(severity_issues)})")
        
        for i, issue in enumerate(severity_issues, 1):
            report.append(f"\n  {i}. Line {issue.get('line', '?')}: {issue.get('description', 'Unknown issue')}")
            if 'suggestion' in issue:
                report.append(f"     → {issue['suggestion']}")
    
    return "\n".join(report)


