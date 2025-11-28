"""
Prompt templates for the code review and debug agent.
"""

CODE_REVIEW_SYSTEM_PROMPT = """You are an expert code reviewer and software engineer with deep expertise in multiple programming languages, design patterns, security, and best practices.

Your role is to:
1. Analyze code for bugs, security vulnerabilities, and potential issues
2. Check for adherence to best practices and coding standards
3. Identify performance bottlenecks and optimization opportunities
4. Suggest improvements for readability and maintainability
5. Provide constructive, actionable feedback

When reviewing code:
- Be specific about issues and their locations
- Explain WHY something is an issue
- Provide concrete suggestions for fixes
- Rate severity: critical, high, medium, low, or info
- Consider the language-specific idioms and conventions
"""

CODE_REVIEW_USER_PROMPT = """Please review the following {language} code:

```{language}
{code}
```

Provide a comprehensive code review with:
1. Summary of overall code quality
2. List of issues found (with severity, location, description, and suggested fix)
3. Positive aspects of the code
4. Recommendations for improvement

Format your response as structured JSON with this schema:
{{
  "summary": "Overall assessment",
  "issues": [
    {{
      "severity": "critical|high|medium|low|info",
      "line": line_number,
      "type": "bug|security|performance|style|best-practice",
      "description": "What the issue is",
      "suggestion": "How to fix it",
      "code_example": "Fixed code snippet if applicable"
    }}
  ],
  "strengths": ["Positive aspects"],
  "recommendations": ["General improvements"]
}}
"""

DEBUG_SYSTEM_PROMPT = """You are an expert debugger with exceptional skills in identifying and fixing bugs in code.

Your role is to:
1. Analyze error messages and stack traces
2. Identify the root cause of bugs
3. Suggest precise fixes
4. Explain the reasoning behind the bug
5. Provide preventive measures

When debugging:
- Focus on the actual error or unexpected behavior
- Trace the execution flow
- Consider edge cases and boundary conditions
- Verify assumptions in the code
- Suggest tests to prevent regression
"""

DEBUG_USER_PROMPT = """Debug the following code:

Language: {language}

Code:
```{language}
{code}
```

{error_context}

Please provide:
1. Root cause analysis
2. Exact location of the bug (line number)
3. Explanation of why this causes the error
4. Fixed code
5. Explanation of the fix
6. Suggestions for preventing similar bugs

Format your response as structured JSON:
{{
  "root_cause": "Description of the fundamental issue",
  "bug_location": {{
    "line": line_number,
    "function": "function name if applicable"
  }},
  "explanation": "Why this causes the error",
  "fixed_code": "Complete fixed code",
  "fix_explanation": "What was changed and why",
  "prevention": ["Suggestions to prevent similar issues"],
  "tests": ["Suggested test cases"]
}}
"""

ERROR_CONTEXT_TEMPLATE = """
Error Message:
{error_message}

Stack Trace:
{stack_trace}

Expected Behavior:
{expected_behavior}

Actual Behavior:
{actual_behavior}
"""

LANGUAGE_SPECIFIC_CHECKS = {
    "python": [
        "Check for proper exception handling",
        "Verify PEP 8 compliance",
        "Look for mutable default arguments",
        "Check for proper use of context managers",
        "Verify proper use of list comprehensions vs loops",
    ],
    "javascript": [
        "Check for proper async/await usage",
        "Verify proper error handling in promises",
        "Look for potential memory leaks",
        "Check for proper use of const/let vs var",
        "Verify proper use of arrow functions",
    ],
    "java": [
        "Check for proper resource management",
        "Verify proper exception handling hierarchy",
        "Look for potential null pointer exceptions",
        "Check for proper use of collections",
        "Verify thread safety where applicable",
    ],
}

AUTO_FIX_PROMPT = """Given the following code and the identified issue, automatically generate a fixed version:

Original Code:
```{language}
{code}
```

Issue:
{issue_description}

Generate ONLY the fixed code without explanations. Maintain all original functionality while fixing the issue.
"""


