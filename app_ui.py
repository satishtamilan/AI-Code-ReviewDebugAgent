from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent'))

from session_manager import SessionManager, MemoryBank
from observability import AgentTracer, MetricsCollector
import google.generativeai as genai

# Import codebase analyzer
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codebase_analyzer import CodebaseAnalyzer

app = Flask(__name__)
CORS(app)

# Initialize tracking systems
session_manager = SessionManager(storage_path=".live_sessions")
memory_bank = MemoryBank(storage_path=".live_memory")
tracer = AgentTracer(export_path=".live_traces")
metrics = MetricsCollector()
codebase_analyzer = CodebaseAnalyzer()

# Configure Gemini
api_key = os.environ.get('GEMINI_API_KEY')
if api_key:
    genai.configure(api_key=api_key)
    
    # Find best model
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
        
        model_name = None
        for priority in ['gemini-2.5-flash', 'gemini-1.5-flash', 'gemini-pro']:
            for m in available_models:
                if priority in m:
                    model_name = m
                    break
            if model_name:
                break
        
        if not model_name:
            model_name = available_models[0] if available_models else 'gemini-pro'
        
        model = genai.GenerativeModel(model_name)
        print(f"Using Gemini model: {model_name}")
    except Exception as e:
        print(f"Warning: Could not initialize Gemini: {e}")
        model = None
else:
    print("Warning: GEMINI_API_KEY not set")
    model = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_code():
    """Analyze code and track everything"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'error': 'No code provided'}), 400
        
        if not model:
            return jsonify({'error': 'Gemini API not configured'}), 500
        
        # Create session
        session_id = session_manager.create_session()
        
        # Start trace
        span_id = tracer.start_span("code_analysis", {
            "language": language,
            "code_length": len(code)
        })
        
        # Track metrics
        metrics.increment("analyses_requested")
        
        # Build prompt
        prompt = f"""You are an expert code reviewer. Analyze this {language} code and provide:

1. List of bugs/errors (with severity: error/warning/info)
2. Security vulnerabilities
3. Performance issues
4. Code quality improvements

Return the response in JSON format like this:
{{
  "issues": [
    {{"type": "error", "line": 5, "title": "Bug title", "description": "Details", "fix": "How to fix"}},
    {{"type": "warning", "line": 3, "title": "Warning", "description": "Details", "fix": "Suggestion"}}
  ],
  "complexity": 7,
  "quality_score": 85,
  "summary": "Overall assessment"
}}

Code to analyze:
```{language}
{code}
```
"""
        
        # Call Gemini
        tracer.add_span_event(span_id, "gemini_call_start")
        start_time = datetime.now()
        
        response = model.generate_content(prompt)
        result_text = response.text
        
        duration = (datetime.now() - start_time).total_seconds()
        tracer.add_span_event(span_id, "gemini_call_complete", {"duration": duration})
        metrics.record_timing("gemini_call_duration", duration)
        
        # Parse JSON from response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            result = json.loads(result_text)
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                raise ValueError("Invalid result format")
            
            if 'issues' not in result:
                result['issues'] = []
            
            # Validate each issue has required fields
            for issue in result['issues']:
                if 'type' not in issue:
                    issue['type'] = 'info'
                if 'title' not in issue:
                    issue['title'] = 'Issue found'
                if 'description' not in issue:
                    issue['description'] = 'No description provided'
                    
        except Exception as parse_error:
            print(f"Warning: JSON parsing failed: {parse_error}")
            # Fallback if JSON parsing fails
            result = {
                "issues": [
                    {
                        "type": "info",
                        "line": 0,
                        "title": "Analysis Complete",
                        "description": result_text[:500] if result_text else "Analysis completed",
                        "fix": "See full analysis"
                    }
                ],
                "complexity": 5,
                "quality_score": 75,
                "summary": "Analysis completed"
            }
        
        # Save to session
        session_manager.save_interaction(session_id, {
            "type": "code_analysis",
            "language": language,
            "code_length": len(code),
            "issues_found": len(result.get('issues', [])),
            "result": result
        })
        
        # Store in memory bank
        try:
            for issue in result.get('issues', []):
                if issue.get('type') == 'error':
                    memory_bank.store_memory("common_bugs", {
                        "pattern": issue.get('title', 'unknown'),
                        "language": language,
                        "fix": issue.get('fix', ''),
                        "description": issue.get('description', '')
                    })
        except Exception as mem_error:
            print(f"Warning: Could not store in memory bank: {mem_error}")
        
        # End trace
        tracer.end_span(span_id)
        
        # Record metrics
        metrics.increment("analyses_completed")
        metrics.increment("total_issues_found", len(result.get('issues', [])))
        metrics.record_value("code_complexity", result.get('complexity', 0))
        metrics.record_value("quality_score", result.get('quality_score', 0))
        
        # Add tracking info
        result['tracking'] = {
            'session_id': session_id,
            'span_id': span_id,
            'duration_ms': tracer.spans[span_id].duration_ms
        }
        
        return jsonify(result)
        
    except Exception as e:
        metrics.increment("analyses_failed")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get real-time tracking statistics"""
    try:
        # Session stats
        session_count = len(list(Path(".live_sessions").glob("*.json")))
        
        # Memory bank stats
        memory_stats = {}
        if Path(".live_memory/memories.json").exists():
            with open(".live_memory/memories.json", 'r') as f:
                memories = json.load(f)
                memory_stats = {
                    category: len(items) 
                    for category, items in memories.items()
                }
        
        # Trace stats
        trace_summary = tracer.get_span_summary()
        
        # Metrics summary
        metrics_summary = metrics.get_summary()
        
        return jsonify({
            'sessions': {
                'total': session_count,
                'active': len(session_manager.sessions)
            },
            'memory': memory_stats,
            'traces': trace_summary,
            'metrics': {
                'counters': metrics_summary.get('counters', {}),
                'timings': {
                    name: stats.get('avg', 0)
                    for name, stats in metrics_summary.get('timings', {}).items()
                },
                'values': {
                    name: stats.get('avg', 0)
                    for name, stats in metrics_summary.get('values', {}).items()
                }
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get recent analysis history"""
    try:
        sessions_path = Path(".live_sessions")
        history = []
        
        if sessions_path.exists():
            for session_file in sorted(sessions_path.glob("*.json"), reverse=True)[:10]:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)
                    for interaction in session_data.get('interactions', []):
                        if interaction.get('type') == 'code_analysis':
                            history.append({
                                'timestamp': interaction.get('timestamp'),
                                'language': interaction.get('language'),
                                'issues_found': interaction.get('issues_found', 0),
                                'session_id': session_data.get('session_id')
                            })
        
        return jsonify(history[:20])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory', methods=['GET'])
def get_memory():
    """Get memory bank patterns"""
    try:
        category = request.args.get('category', 'common_bugs')
        limit = int(request.args.get('limit', 10))
        
        memories = memory_bank.retrieve_memories(category, limit=limit)
        
        return jsonify(memories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze-codebase', methods=['POST'])
def analyze_codebase():
    """Analyze entire codebase"""
    try:
        data = request.json
        directory = data.get('directory', '.')
        
        if not model:
            return jsonify({'error': 'Gemini API not configured'}), 500
        
        # Validate directory
        if not Path(directory).exists():
            return jsonify({'error': f'Directory not found: {directory}'}), 400
        
        # Start analysis
        results = codebase_analyzer.analyze_codebase(directory, model)
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 70)
    print("Starting Code Review Agent with Live Tracking")
    print("=" * 70)
    print("\nOpen your browser to: http://localhost:5000")
    print("\nFeatures:")
    print("  - Real-time code analysis with Gemini")
    print("  - Live session tracking")
    print("  - Memory bank visualization")
    print("  - Observability metrics")
    print("  - Beautiful modern UI")
    print("\nPress Ctrl+C to stop")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5001, debug=True)

