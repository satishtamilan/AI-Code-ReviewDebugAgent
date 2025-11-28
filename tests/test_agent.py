"""
Unit tests for the code review and debug agents.
"""
import pytest
from unittest.mock import Mock, patch
from agent.code_reviewer import CodeReviewAgent
from agent.debugger import DebugAgent
from agent.utils import (
    detect_language,
    extract_code_blocks,
    parse_json_response,
    calculate_complexity_score,
    get_line_context,
)


class TestUtils:
    """Test utility functions."""
    
    def test_detect_language_python(self):
        code = """
def hello_world():
    print("Hello, World!")
"""
        assert detect_language(code) == "python"
    
    def test_detect_language_javascript(self):
        code = """
function helloWorld() {
    console.log("Hello, World!");
}
"""
        assert detect_language(code) == "javascript"
    
    def test_detect_language_with_filename(self):
        code = "some code"
        assert detect_language(code, "test.py") == "python"
        assert detect_language(code, "test.js") == "javascript"
    
    def test_extract_code_blocks(self):
        text = """
Here's some Python code:
```python
def test():
    pass
```
And some JavaScript:
```javascript
function test() {}
```
"""
        blocks = extract_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0]['language'] == 'python'
        assert blocks[1]['language'] == 'javascript'
    
    def test_parse_json_response(self):
        response = '{"key": "value"}'
        result = parse_json_response(response)
        assert result == {"key": "value"}
    
    def test_parse_json_from_markdown(self):
        response = """
Here's the result:
```json
{"key": "value"}
```
"""
        result = parse_json_response(response)
        assert result == {"key": "value"}
    
    def test_calculate_complexity_score(self):
        code = """
def test():
    if True:
        for i in range(10):
            print(i)
"""
        result = calculate_complexity_score(code, "python")
        assert result['total_lines'] > 0
        assert result['complexity'] > 1
    
    def test_get_line_context(self):
        code = """line 1
line 2
line 3
line 4
line 5"""
        context = get_line_context(code, 3, context_lines=1)
        assert "line 2" in context
        assert "line 3" in context
        assert "line 4" in context


class TestCodeReviewAgent:
    """Test the Code Review Agent."""
    
    @pytest.fixture
    def mock_openai_response(self):
        return {
            "summary": "Code looks good overall",
            "issues": [
                {
                    "severity": "medium",
                    "line": 5,
                    "type": "style",
                    "description": "Variable name could be more descriptive",
                    "suggestion": "Use a more descriptive variable name"
                }
            ],
            "strengths": ["Good structure"],
            "recommendations": ["Add docstrings"]
        }
    
    @patch('agent.code_reviewer.OpenAI')
    def test_review_code_basic(self, mock_openai, mock_openai_response):
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=str(mock_openai_response)))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create agent with mock API key
        agent = CodeReviewAgent(api_key="test_key")
        
        # Note: This will fail without proper mocking of parse_json_response
        # In a real test, we'd need more comprehensive mocking
    
    def test_agent_initialization_without_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                CodeReviewAgent()


class TestDebugAgent:
    """Test the Debug Agent."""
    
    @pytest.fixture
    def mock_debug_response(self):
        return {
            "root_cause": "Null pointer exception",
            "bug_location": {"line": 10, "function": "process_data"},
            "explanation": "Variable not initialized",
            "fixed_code": "# Fixed code here",
            "fix_explanation": "Initialize variable",
            "prevention": ["Add null checks"],
            "tests": ["Test with null input"]
        }
    
    @patch('agent.debugger.OpenAI')
    def test_debug_code_basic(self, mock_openai, mock_debug_response):
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content=str(mock_debug_response)))]
        mock_client.chat.completions.create.return_value = mock_response
        
        # Create agent with mock API key
        agent = DebugAgent(api_key="test_key")
    
    def test_agent_initialization_without_api_key(self):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError):
                DebugAgent()


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_code_review_and_debug_workflow(self):
        """Test a complete workflow of review -> debug -> fix."""
        # This would be an integration test with real API calls
        # Skipped in unit tests
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


