"""
Codebase Analysis - Analyze entire projects, not just single files
"""
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import json

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent'))

from session_manager import SessionManager, MemoryBank
from observability import AgentTracer, MetricsCollector


class CodebaseAnalyzer:
    """
    Analyze entire codebases, not just single files.
    
    Features:
    - Multi-file analysis
    - Directory traversal
    - Cross-file issue detection
    - Architecture analysis
    - Dependency tracking
    """
    
    def __init__(self):
        self.session_manager = SessionManager(storage_path=".codebase_sessions")
        self.memory_bank = MemoryBank(storage_path=".codebase_memory")
        self.tracer = AgentTracer(export_path=".codebase_traces")
        self.metrics = MetricsCollector()
        
        # Supported file extensions
        self.extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.rs': 'rust',
            '.rb': 'ruby',
            '.php': 'php',
            '.cs': 'csharp',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.kts': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.R': 'r',
        }
        
        # Files to ignore
        self.ignore_patterns = [
            '__pycache__',
            'node_modules',
            '.git',
            '.venv',
            'venv',
            'dist',
            'build',
            '.egg-info',
            '.pytest_cache',
            '.mypy_cache',
            'coverage',
            '.DS_Store',
        ]
    
    def scan_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Scan directory and collect all code files.
        
        Args:
            directory: Path to directory
            
        Returns:
            List of file information dictionaries
        """
        span_id = self.tracer.start_span("scan_directory", {
            "directory": directory
        })
        
        files = []
        directory_path = Path(directory)
        
        if not directory_path.exists():
            self.tracer.end_span(span_id)
            raise ValueError(f"Directory does not exist: {directory}")
        
        for file_path in directory_path.rglob('*'):
            # Skip directories
            if file_path.is_dir():
                continue
            
            # Skip ignored patterns
            if any(pattern in str(file_path) for pattern in self.ignore_patterns):
                continue
            
            # Check extension
            ext = file_path.suffix.lower()
            if ext in self.extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    files.append({
                        'path': str(file_path.relative_to(directory_path)),
                        'absolute_path': str(file_path),
                        'language': self.extensions[ext],
                        'extension': ext,
                        'size': len(content),
                        'lines': len(content.split('\n')),
                        'content': content
                    })
                    
                    self.metrics.increment("files_scanned")
                    
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")
        
        self.tracer.end_span(span_id)
        self.metrics.record_value("files_in_codebase", len(files))
        
        return files
    
    def analyze_file(self, file_info: Dict[str, Any], model) -> Dict[str, Any]:
        """
        Analyze a single file.
        
        Args:
            file_info: File information dictionary
            model: Gemini model
            
        Returns:
            Analysis results
        """
        span_id = self.tracer.start_span("analyze_file", {
            "file": file_info['path'],
            "language": file_info['language']
        })
        
        prompt = f"""Analyze this {file_info['language']} file and provide:

1. Critical issues (bugs, errors)
2. Security vulnerabilities
3. Code quality issues
4. Suggestions for improvement

File: {file_info['path']}
Lines: {file_info['lines']}

Code:
```{file_info['language']}
{file_info['content'][:5000]}  # First 5000 chars
```

Return JSON:
{{
  "issues": [
    {{"severity": "high|medium|low", "type": "bug|security|quality", "description": "...", "line": 0, "fix": "..."}}
  ],
  "score": 85,
  "summary": "..."
}}
"""
        
        try:
            response = model.generate_content(prompt)
            result_text = response.text
            
            # Parse JSON
            if "```json" in result_text:
                json_start = result_text.find("```json") + 7
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            elif "```" in result_text:
                json_start = result_text.find("```") + 3
                json_end = result_text.find("```", json_start)
                result_text = result_text[json_start:json_end].strip()
            
            result = json.loads(result_text)
            result['file'] = file_info['path']
            result['language'] = file_info['language']
            
            self.metrics.increment("files_analyzed")
            self.metrics.increment("issues_found", len(result.get('issues', [])))
            
        except Exception as e:
            print(f"Error analyzing {file_info['path']}: {e}")
            result = {
                'file': file_info['path'],
                'language': file_info['language'],
                'issues': [],
                'score': 50,
                'summary': f'Error: {str(e)}',
                'error': str(e)
            }
        
        self.tracer.end_span(span_id)
        return result
    
    def analyze_codebase(self, directory: str, model) -> Dict[str, Any]:
        """
        Analyze entire codebase.
        
        Args:
            directory: Path to codebase
            model: Gemini model
            
        Returns:
            Complete codebase analysis
        """
        session_id = self.session_manager.create_session()
        
        span_id = self.tracer.start_span("analyze_codebase", {
            "directory": directory
        })
        
        # Scan files
        print(f"Scanning directory: {directory}")
        files = self.scan_directory(directory)
        print(f"Found {len(files)} code files")
        
        # Analyze each file
        results = []
        for i, file_info in enumerate(files[:50], 1):  # Limit to 50 files for demo
            print(f"Analyzing {i}/{min(len(files), 50)}: {file_info['path']}")
            result = self.analyze_file(file_info, model)
            results.append(result)
        
        # Aggregate results
        total_issues = sum(len(r.get('issues', [])) for r in results)
        total_lines = sum(f['lines'] for f in files)
        avg_score = sum(r.get('score', 50) for r in results) / len(results) if results else 0
        
        # Count by severity
        severity_counts = {'high': 0, 'medium': 0, 'low': 0}
        issue_types = {'bug': 0, 'security': 0, 'quality': 0}
        
        for result in results:
            for issue in result.get('issues', []):
                sev = issue.get('severity', 'low')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
                
                typ = issue.get('type', 'quality')
                issue_types[typ] = issue_types.get(typ, 0) + 1
        
        # Language breakdown
        language_counts = {}
        for file_info in files:
            lang = file_info['language']
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        codebase_analysis = {
            'session_id': session_id,
            'directory': directory,
            'total_files': len(files),
            'analyzed_files': len(results),
            'total_lines': total_lines,
            'total_issues': total_issues,
            'average_score': round(avg_score, 1),
            'severity_breakdown': severity_counts,
            'issue_types': issue_types,
            'languages': language_counts,
            'file_results': results
        }
        
        # Save to session
        self.session_manager.save_interaction(session_id, {
            'type': 'codebase_analysis',
            'directory': directory,
            'summary': codebase_analysis
        })
        
        # Store patterns in memory
        for result in results:
            for issue in result.get('issues', []):
                if issue.get('severity') == 'high':
                    self.memory_bank.store_memory("critical_issues", {
                        'file': result['file'],
                        'issue': issue.get('description', ''),
                        'type': issue.get('type', ''),
                        'language': result['language']
                    })
        
        self.tracer.end_span(span_id)
        
        # Export traces
        trace_file = self.tracer.export_traces(f"codebase_{session_id}.json")
        codebase_analysis['trace_file'] = trace_file
        
        return codebase_analysis
    
    def generate_report(self, analysis: Dict[str, Any], output_file: str = None) -> str:
        """
        Generate analysis report.
        
        Args:
            analysis: Codebase analysis results
            output_file: Optional output file path
            
        Returns:
            Report text
        """
        report = f"""
# Codebase Analysis Report

## Overview
- **Directory**: {analysis['directory']}
- **Total Files**: {analysis['total_files']}
- **Analyzed Files**: {analysis['analyzed_files']}
- **Total Lines of Code**: {analysis['total_lines']:,}
- **Average Quality Score**: {analysis['average_score']}/100

## Issues Summary
- **Total Issues Found**: {analysis['total_issues']}
- **High Severity**: {analysis['severity_breakdown'].get('high', 0)}
- **Medium Severity**: {analysis['severity_breakdown'].get('medium', 0)}
- **Low Severity**: {analysis['severity_breakdown'].get('low', 0)}

## Issue Types
- **Bugs**: {analysis['issue_types'].get('bug', 0)}
- **Security**: {analysis['issue_types'].get('security', 0)}
- **Code Quality**: {analysis['issue_types'].get('quality', 0)}

## Languages
"""
        
        for lang, count in analysis['languages'].items():
            report += f"- **{lang}**: {count} files\n"
        
        report += "\n## File Analysis\n\n"
        
        for result in analysis['file_results']:
            if result.get('issues'):
                report += f"\n### {result['file']} ({result['language']})\n"
                report += f"Score: {result.get('score', 0)}/100\n\n"
                
                for issue in result['issues'][:5]:  # Top 5 issues per file
                    report += f"- **[{issue.get('severity', 'low').upper()}]** "
                    report += f"{issue.get('description', 'No description')}\n"
                    if issue.get('fix'):
                        report += f"  Fix: {issue['fix']}\n"
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_file}")
        
        return report


if __name__ == '__main__':
    import google.generativeai as genai
    
    # Configure Gemini
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        print("Error: GEMINI_API_KEY not set!")
        sys.exit(1)
    
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
        
        model = genai.GenerativeModel(model_name)
        print(f"Using model: {model_name}")
    except Exception as e:
        print(f"Error initializing Gemini: {e}")
        sys.exit(1)
    
    # Analyze codebase
    analyzer = CodebaseAnalyzer()
    
    # Get directory from command line or use current directory
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    
    print("=" * 70)
    print("CODEBASE ANALYSIS")
    print("=" * 70)
    
    results = analyzer.analyze_codebase(directory, model)
    
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Files analyzed: {results['analyzed_files']}")
    print(f"Total issues: {results['total_issues']}")
    print(f"Average score: {results['average_score']}/100")
    print(f"High severity: {results['severity_breakdown'].get('high', 0)}")
    print(f"Medium severity: {results['severity_breakdown'].get('medium', 0)}")
    print(f"Low severity: {results['severity_breakdown'].get('low', 0)}")
    
    # Generate report
    report = analyzer.generate_report(results, f"codebase_report_{results['session_id']}.md")
    
    print(f"\nReport saved: codebase_report_{results['session_id']}.md")
    print(f"Traces saved: {results['trace_file']}")
    print("\n✅ Codebase analysis complete!")

