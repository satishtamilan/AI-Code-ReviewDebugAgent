# Codebase Analysis Guide

## 🎯 Support for Whole Codebase Analysis

Your agent now supports analyzing entire codebases, not just single files!

---

## 3 Ways to Analyze Codebases

### 1. Command Line Tool

**Analyze current directory:**
```bash
cd /Users/sanandhan/code/kaggle-genai
./analyze_codebase.sh
```

**Analyze specific directory:**
```bash
./analyze_codebase.sh /path/to/your/project
```

**What it does:**
- Scans all code files in the directory
- Analyzes each file with Gemini
- Generates comprehensive report
- Tracks all metrics and sessions
- Exports traces

**Output:**
- Console summary
- Markdown report: `codebase_report_<session_id>.md`
- Trace file: `.codebase_traces/codebase_<session_id>.json`

---

### 2. Web UI (Coming Soon)

The web UI at `http://localhost:5001` can be enhanced to support:
- Directory upload
- Multi-file drag & drop
- Real-time progress tracking
- Visual reports

---

### 3. Python API

```python
from codebase_analyzer import CodebaseAnalyzer
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key='your-key')
model = genai.GenerativeModel('gemini-2.5-flash')

# Analyze codebase
analyzer = CodebaseAnalyzer()
results = analyzer.analyze_codebase('/path/to/project', model)

# Generate report
report = analyzer.generate_report(results, 'report.md')
```

---

## What Gets Analyzed

### Supported Languages
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`)
- Go (`.go`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- Rust (`.rs`)
- Ruby (`.rb`)
- PHP (`.php`)
- C# (`.cs`)
- Swift (`.swift`)
- Kotlin (`.kt`, `.kts`)
- Scala (`.scala`)
- R (`.r`, `.R`)

### What's Analyzed Per File
1. **Critical Issues** - Bugs and errors
2. **Security Vulnerabilities** - SQL injection, XSS, etc.
3. **Code Quality** - Style, best practices
4. **Improvement Suggestions** - Refactoring ideas

### Automatically Ignored
- `__pycache__`, `node_modules`
- `.git`, `.venv`, `venv`
- `dist`, `build`
- Test coverage files
- Cache directories

---

## Features

### 🔍 Analysis Capabilities

**File-Level:**
- Syntax analysis
- Security scanning
- Quality scoring (0-100)
- Issue detection with severity (high/medium/low)

**Codebase-Level:**
- Total lines of code
- Files by language
- Issue aggregation
- Average quality score
- Security vulnerability count
- Architecture insights

### 📊 Tracking & Observability

**Everything is tracked:**
- ✅ Sessions per codebase analysis
- ✅ Memory bank learns patterns
- ✅ Traces for performance
- ✅ Metrics for all operations

**Storage:**
```
.codebase_sessions/     # Analysis sessions
.codebase_memory/       # Learned patterns
.codebase_traces/       # Performance traces
```

---

## Example Output

### Console Output
```
======================================================================
CODEBASE ANALYSIS
======================================================================
Using model: models/gemini-2.5-flash
Scanning directory: .
Found 45 code files
Analyzing 1/45: agent/session_manager.py
Analyzing 2/45: agent/observability.py
...

======================================================================
RESULTS
======================================================================
Files analyzed: 45
Total issues: 127
Average score: 82.5/100
High severity: 8
Medium severity: 34
Low severity: 85

Report saved: codebase_report_session_123.md
Traces saved: .codebase_traces/codebase_session_123.json

✅ Codebase analysis complete!
```

### Report Structure

```markdown
# Codebase Analysis Report

## Overview
- Directory: /path/to/project
- Total Files: 45
- Total Lines of Code: 12,543
- Average Quality Score: 82.5/100

## Issues Summary
- Total Issues Found: 127
- High Severity: 8
- Medium Severity: 34
- Low Severity: 85

## Issue Types
- Bugs: 15
- Security: 8
- Code Quality: 104

## Languages
- python: 25 files
- javascript: 10 files
- go: 5 files
- java: 5 files

## File Analysis

### agent/session_manager.py (python)
Score: 85/100

- **[HIGH]** Potential SQL injection in query construction
  Fix: Use parameterized queries
- **[MEDIUM]** Missing error handling for file operations
  Fix: Add try-catch blocks
...
```

---

## Use Cases

### 1. Code Review Before Deployment
```bash
./analyze_codebase.sh /path/to/production/code
```

### 2. Onboard to New Project
```bash
# Get overview of entire codebase
./analyze_codebase.sh /path/to/new/project
```

### 3. Security Audit
```bash
# Find all security issues
./analyze_codebase.sh . | grep -i security
```

### 4. Quality Assessment
```bash
# Check code quality across project
./analyze_codebase.sh /path/to/project
# See report for average quality score
```

---

## Advanced Configuration

### Customize File Extensions

Edit `codebase_analyzer.py`:
```python
self.extensions = {
    '.py': 'python',
    '.js': 'javascript',
    # Add your extensions
    '.vue': 'vue',
    '.svelte': 'svelte',
}
```

### Customize Ignore Patterns

Edit `codebase_analyzer.py`:
```python
self.ignore_patterns = [
    '__pycache__',
    'node_modules',
    # Add your patterns
    'migrations',
    'tests',
]
```

### Adjust Analysis Depth

Edit the file limit in `analyze_codebase`:
```python
for i, file_info in enumerate(files[:50], 1):  # Change 50 to your limit
```

---

## Integration with UI

The codebase analyzer is now available as an API endpoint:

```javascript
// Call from frontend
fetch('/api/analyze-codebase', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        directory: '/path/to/project'
    })
})
.then(res => res.json())
.then(data => {
    console.log('Analysis complete!', data);
});
```

---

## Performance

- **Small projects** (< 10 files): ~30 seconds
- **Medium projects** (10-50 files): ~2-5 minutes
- **Large projects** (50+ files): ~5-15 minutes

Tip: For very large codebases, analyze in chunks by subdirectory.

---

## Next Steps

1. **Try it now:**
   ```bash
   ./analyze_codebase.sh agent/
   ```

2. **Check the report:**
   ```bash
   cat codebase_report_*.md
   ```

3. **View metrics:**
   ```bash
   cat .codebase_traces/*.json
   ```

4. **Integrate with CI/CD** - Run before deployments

---

## Benefits for Kaggle Submission

✅ **Shows scalability** - Not just single files
✅ **Enterprise-ready** - Analyze entire projects
✅ **Real-world use case** - Production code review
✅ **Comprehensive tracking** - All features used
✅ **Automated reports** - Professional output

This demonstrates your agent can handle real production codebases, not just toy examples!

