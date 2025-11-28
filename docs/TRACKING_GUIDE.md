# Memory and Observability Tracking Guide

## Where Memory and Observability are Tracked

### Quick Answer

**Memory and Observability are tracked in 2 main files:**

1. **`agent/session_manager.py`** - Session Memory & Long-term Memory
2. **`agent/observability.py`** - Tracing & Metrics

---

## Feature 5: Sessions & Memory

### Location: `agent/session_manager.py`

#### 1. SessionManager (Lines 24-256)

**What it tracks:**
- Session state (conversations, interactions)
- Context (user preferences, language, settings)
- Interaction history (every code review, debug action)

**Where data is stored:**
```
.sessions/
  session_123.json
  session_456.json
```

**Usage:**
```python
from agent.session_manager import SessionManager

session_manager = SessionManager()
session_id = session_manager.create_session()

# Track interaction
session_manager.save_interaction(session_id, {
    "type": "code_review",
    "code": "...",
    "result": "..."
})

# Get history
history = session_manager.get_history(session_id)
```

#### 2. MemoryBank (Lines 258-393)

**What it tracks:**
- Long-term patterns (common bugs, code patterns)
- Fix strategies (security fixes, best practices)
- Learning insights (accumulated knowledge)

**Where data is stored:**
```
.memory_bank/
  memories.json
```

**Categories:**
- `common_bugs` - Frequently found bugs
- `code_patterns` - Recognized code patterns
- `fix_strategies` - Solutions and fixes
- `review_insights` - Review learnings

**Usage:**
```python
from agent.session_manager import MemoryBank

memory_bank = MemoryBank()

# Store learning
memory_bank.store_memory("common_bugs", {
    "pattern": "sql_injection",
    "fix": "Use parameterized queries"
})

# Retrieve patterns
bugs = memory_bank.retrieve_memories("common_bugs")
common = memory_bank.get_common_patterns("common_bugs", top_n=5)
```

---

## Feature 6: Observability

### Location: `agent/observability.py`

#### 1. AgentTracer (Lines 33-226)

**What it tracks:**
- Distributed traces (operation timelines)
- Span events (what happened when)
- Performance timing (duration, latency)

**Where data is stored:**
```
.traces/
  traces_1234567890.json
```

**Usage:**
```python
from agent.observability import AgentTracer

tracer = AgentTracer()

# Start tracking
span_id = tracer.start_span("code_review_workflow")

# Add events
tracer.add_span_event(span_id, "syntax_check", {"status": "passed"})
tracer.add_span_event(span_id, "security_scan", {"found": 2})

# End tracking
tracer.end_span(span_id)

# Get summary
summary = tracer.get_span_summary()
# Returns: total_spans, avg_duration_ms, etc.

# Export
tracer.export_traces("my_traces.json")
```

#### 2. MetricsCollector (Lines 228-356)

**What it tracks:**
- Counters (reviews completed, bugs found)
- Timings (review duration, p95, p99)
- Values (code quality score, complexity)

**Usage:**
```python
from agent.observability import MetricsCollector

metrics = MetricsCollector()

# Track counters
metrics.increment("reviews_completed")
metrics.increment("bugs_found", 5)

# Track timing
metrics.record_timing("review_duration", 2.5)

# Track values
metrics.record_value("code_quality_score", 95.0)

# Get stats
timing_stats = metrics.get_timing_stats("review_duration")
# Returns: count, avg, min, max, p50, p95, p99

counter_value = metrics.get_counter("reviews_completed")

summary = metrics.get_summary()
# Returns all metrics with statistics
```

---

## Real Data Locations

After running the agent, you'll find tracking data in:

```
/Users/sanandhan/code/kaggle-genai/
├── .sessions/              # Session data
│   └── session_*.json
├── .memory_bank/           # Long-term memory
│   └── memories.json
├── .traces/                # Trace exports
│   └── traces_*.json
└── metrics/                # Metrics exports
    └── metrics_*.json
```

---

## How It Works in the Code

### In Multi-Agent Orchestrator

```python
# agent/multi_agent_orchestrator.py

class SequentialWorkflow:
    def execute(self, code, language):
        # Start trace
        span_id = self.tracer.start_span("sequential_workflow")
        
        # Save to session
        self.session_manager.save_interaction(session_id, {
            "type": "workflow_start",
            "language": language
        })
        
        # Track metrics
        self.metrics.increment("workflows_started")
        
        # Execute agents...
        result1 = agent1.review(code)
        self.tracer.add_span_event(span_id, "agent1_complete")
        
        result2 = agent2.debug(code)
        self.tracer.add_span_event(span_id, "agent2_complete")
        
        # Store learning
        self.memory_bank.store_memory("review_insights", {
            "pattern": result1.pattern,
            "effectiveness": "high"
        })
        
        # End trace
        self.tracer.end_span(span_id)
        
        # Record timing
        duration = self.tracer.spans[span_id].duration_ms
        self.metrics.record_timing("workflow_duration", duration)
        
        return result
```

---

## View Tracking Data Live

Run the demo:
```bash
cd /Users/sanandhan/code/kaggle-genai
source venv/bin/activate
python show_tracking.py
```

This will:
1. Create sample sessions
2. Store memories
3. Generate traces
4. Collect metrics
5. Show you where all data is saved

---

## Key Files Summary

| Feature | File | Lines | What It Does |
|---------|------|-------|--------------|
| Session Management | `agent/session_manager.py` | 24-256 | Tracks conversations, state |
| Long-term Memory | `agent/session_manager.py` | 258-393 | Stores patterns, learnings |
| Distributed Tracing | `agent/observability.py` | 33-226 | Tracks operation timeline |
| Metrics Collection | `agent/observability.py` | 228-356 | Tracks performance stats |

---

## Quick Test Commands

```bash
# View session data
cat .demo_sessions/demo_session_001.json

# View memory bank
cat .demo_memory/memories.json

# View traces
cat .demo_traces/demo_traces.json

# View metrics
cat .demo_traces/demo_metrics.json
```

---

## Integration Points

All 4 tracking systems are integrated in:

1. **`demo_pure_google.py`** - Full demo with all features
2. **`agent/multi_agent_orchestrator.py`** - Used in workflows
3. **`kaggle_notebook_code.py`** - Kaggle submission version

Every time you run the agent:
- Sessions are created automatically
- Interactions are logged
- Traces are recorded
- Metrics are collected
- Memories are stored

All data persists to disk for analysis!

