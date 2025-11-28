"""
Flask API for deploying the Code Review and Debug Agent.
Use this for Cloud Run, Docker, or local deployment.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add agent to path
sys.path.insert(0, os.path.dirname(__file__))

from agent import (
    MultiAgentOrchestrator,
    SessionManager,
    ToolRegistry,
)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for web clients

# Initialize agent system
print("Initializing agent system...")
orchestrator = MultiAgentOrchestrator(
    enable_tracing=True,
    enable_metrics=True,
)
session_manager = SessionManager()
tool_registry = ToolRegistry()

print("✓ Agent system ready!")


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API documentation."""
    return jsonify({
        "name": "Code Review and Debug Agent",
        "version": "2.0.0",
        "description": "AI-powered multi-agent system for code review and debugging",
        "competition": "Kaggle Agents Intensive Capstone Project",
        "endpoints": {
            "/health": "Health check",
            "/review": "POST - Review code",
            "/debug": "POST - Debug code",
            "/sequential": "POST - Sequential workflow (Review → Debug → Fix)",
            "/loop": "POST - Loop workflow (Iterative refinement)",
            "/tools": "GET - List available tools",
            "/metrics": "GET - Get performance metrics",
            "/traces": "GET - Get trace log",
        },
        "features": [
            "Multi-agent system (sequential & loop workflows)",
            "Custom tools (syntax, complexity, security)",
            "Sessions & memory management",
            "Observability (tracing & metrics)",
            "Context engineering",
        ]
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": ["code_reviewer", "debugger"],
        "tools": len(tool_registry.list_tools()),
    })


@app.route('/review', methods=['POST'])
def review_code():
    """
    Review code endpoint.
    
    Request body:
    {
        "code": "def test(): pass",
        "language": "python",
        "filename": "test.py",  # optional
        "context": "This is a test function"  # optional
    }
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' in request"}), 400
        
        code = data['code']
        language = data.get('language')
        filename = data.get('filename')
        context = data.get('context')
        
        # Create session
        session_id = session_manager.create_session()
        
        # Review code
        from agent import CodeReviewAgent
        reviewer = CodeReviewAgent()
        result = reviewer.review_code(
            code=code,
            language=language,
            filename=filename,
            context=context,
        )
        
        # Save to session
        session_manager.save_interaction(session_id, {
            "type": "code_review",
            "result": result,
        })
        
        result['session_id'] = session_id
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/debug', methods=['POST'])
def debug_code():
    """
    Debug code endpoint.
    
    Request body:
    {
        "code": "def divide(a, b): return a/b",
        "error_message": "ZeroDivisionError",
        "stack_trace": "...",  # optional
        "language": "python"
    }
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' in request"}), 400
        
        code = data['code']
        error_message = data.get('error_message')
        stack_trace = data.get('stack_trace')
        language = data.get('language')
        
        # Create session
        session_id = session_manager.create_session()
        
        # Debug code
        from agent import DebugAgent
        debugger = DebugAgent()
        result = debugger.debug_code(
            code=code,
            error_message=error_message,
            stack_trace=stack_trace,
            language=language,
        )
        
        # Save to session
        session_manager.save_interaction(session_id, {
            "type": "debug",
            "result": result,
        })
        
        result['session_id'] = session_id
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/sequential', methods=['POST'])
def sequential_workflow():
    """
    Execute sequential multi-agent workflow.
    
    Request body:
    {
        "code": "def test(): pass",
        "language": "python"
    }
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' in request"}), 400
        
        code = data['code']
        language = data.get('language')
        
        # Create session
        session_id = session_manager.create_session()
        
        # Execute workflow
        result = orchestrator.execute_sequential_workflow(
            code=code,
            language=language,
            session_id=session_id,
        )
        
        result['session_id'] = session_id
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/loop', methods=['POST'])
def loop_workflow():
    """
    Execute loop-based iterative refinement workflow.
    
    Request body:
    {
        "code": "def test(): pass",
        "language": "python",
        "max_iterations": 3,
        "quality_threshold": 0.85
    }
    """
    try:
        data = request.json
        
        if not data or 'code' not in data:
            return jsonify({"error": "Missing 'code' in request"}), 400
        
        code = data['code']
        language = data.get('language')
        max_iterations = data.get('max_iterations', 3)
        quality_threshold = data.get('quality_threshold', 0.85)
        
        # Create session
        session_id = session_manager.create_session()
        
        # Execute workflow
        result = orchestrator.execute_loop_workflow(
            code=code,
            language=language,
            max_iterations=max_iterations,
            quality_threshold=quality_threshold,
            session_id=session_id,
        )
        
        result['session_id'] = session_id
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/tools', methods=['GET'])
def list_tools():
    """List available analysis tools."""
    tools = tool_registry.list_tools()
    return jsonify({
        "count": len(tools),
        "tools": tools,
    })


@app.route('/tools/<tool_name>', methods=['POST'])
def execute_tool(tool_name):
    """
    Execute a specific tool.
    
    Request body depends on the tool.
    Example for security_scanner:
    {
        "code": "password = '123'",
        "language": "python"
    }
    """
    try:
        data = request.json or {}
        
        result = tool_registry.execute_tool(tool_name, **data)
        
        return jsonify({
            "tool": tool_name,
            "success": result.success,
            "output": result.output,
            "error": result.error,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/metrics', methods=['GET'])
def get_metrics():
    """Get performance metrics."""
    metrics = orchestrator.get_metrics_summary()
    return jsonify(metrics)


@app.route('/traces', methods=['GET'])
def get_traces():
    """Get trace log."""
    limit = request.args.get('limit', type=int)
    event_type = request.args.get('type')
    
    traces = orchestrator.get_trace_log()
    
    if event_type:
        traces = [t for t in traces if t.get('type') == event_type]
    
    if limit:
        traces = traces[-limit:]
    
    return jsonify({
        "count": len(traces),
        "traces": traces,
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Get port from environment variable (Cloud Run uses PORT)
    port = int(os.environ.get('PORT', 8080))
    
    # Run server
    print(f"\n🚀 Starting Code Review Agent API on port {port}...")
    print(f"📝 Visit http://localhost:{port}/ for API documentation\n")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('DEBUG', 'False').lower() == 'true',
    )


