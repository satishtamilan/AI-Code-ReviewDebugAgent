#!/usr/bin/env python3
"""
Real-time Memory and Observability Tracker
Shows where and how memory and observability are tracked
"""
import os
import sys
import json
from pathlib import Path

# Don't import agent package to avoid OpenAI dependency
# Import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'agent'))

from session_manager import SessionManager, MemoryBank
from observability import AgentTracer, MetricsCollector

print("=" * 80)
print("MEMORY AND OBSERVABILITY TRACKING - LIVE DEMO")
print("=" * 80)

# Initialize tracking systems
session_manager = SessionManager(storage_path=".demo_sessions")
memory_bank = MemoryBank(storage_path=".demo_memory")
tracer = AgentTracer(export_path=".demo_traces")
metrics = MetricsCollector()

print("\n" + "=" * 80)
print("FEATURE 5: SESSIONS & MEMORY")
print("=" * 80)

print("\n1. SESSION MANAGEMENT")
print("-" * 80)

# Create session
session_id = session_manager.create_session("demo_session_001")
print(f"✅ Session created: {session_id}")
print(f"   Storage location: {session_manager.storage_path}/{session_id}.json")

# Save interaction
session_manager.save_interaction(session_id, {
    "type": "code_review",
    "code": "def hello(): return 'world'",
    "result": "No issues found"
})
print(f"\n✅ Interaction saved to session")

# Update context
session_manager.update_context(session_id, {
    "language": "python",
    "user_preferences": {"strict_mode": True}
})
print(f"✅ Context updated")

# Get session info
session_data = session_manager.get_session(session_id)
print(f"\n📊 Session Info:")
print(f"   Session ID: {session_data['session_id']}")
print(f"   Created: {session_data['created_at']}")
print(f"   Interactions: {len(session_data['interactions'])}")
print(f"   Context keys: {list(session_data['context'].keys())}")

# Get history
history = session_manager.get_history(session_id)
print(f"\n📜 Interaction History:")
for i, interaction in enumerate(history, 1):
    print(f"   {i}. {interaction['type']} at {interaction['timestamp']}")

print("\n2. LONG-TERM MEMORY (Memory Bank)")
print("-" * 80)

# Store memories
memory_bank.store_memory("common_bugs", {
    "pattern": "division_by_zero",
    "description": "Missing zero check before division",
    "fix": "Add if denominator != 0 check"
})

memory_bank.store_memory("code_patterns", {
    "pattern": "list_comprehension",
    "language": "python",
    "example": "[x*2 for x in items if x > 0]"
})

memory_bank.store_memory("fix_strategies", {
    "pattern": "sql_injection",
    "strategy": "Use parameterized queries",
    "priority": "critical"
})

print(f"✅ Stored 3 memories in memory bank")
print(f"   Storage location: {memory_bank.storage_path}/memories.json")

# Retrieve memories
bugs = memory_bank.retrieve_memories("common_bugs")
patterns = memory_bank.retrieve_memories("code_patterns")
strategies = memory_bank.retrieve_memories("fix_strategies")

print(f"\n📊 Memory Bank Contents:")
print(f"   Common bugs: {len(bugs)} stored")
print(f"   Code patterns: {len(patterns)} stored")
print(f"   Fix strategies: {len(strategies)} stored")

print(f"\n🔍 Sample Memory (Common Bugs):")
for bug in bugs:
    print(f"   Pattern: {bug['pattern']}")
    print(f"   Description: {bug['description']}")
    print(f"   Stored at: {bug['stored_at']}")

print("\n" + "=" * 80)
print("FEATURE 6: OBSERVABILITY")
print("=" * 80)

print("\n1. DISTRIBUTED TRACING")
print("-" * 80)

# Start trace
span1 = tracer.start_span("code_review_workflow", {
    "language": "python",
    "lines": 42
})
print(f"✅ Started trace span: {span1}")

# Add events to span
tracer.add_span_event(span1, "syntax_check", {"status": "passed"})
tracer.add_span_event(span1, "security_scan", {"vulnerabilities": 0})
print(f"✅ Added 2 events to span")

# End span
tracer.end_span(span1)
print(f"✅ Ended trace span")

# Get span info
span_info = tracer.spans[span1]
print(f"\n📊 Trace Span Details:")
print(f"   Span ID: {span_info.span_id}")
print(f"   Name: {span_info.name}")
print(f"   Duration: {span_info.duration_ms:.2f}ms")
print(f"   Events: {len(span_info.events)}")
print(f"   Attributes: {span_info.attributes}")

# Get trace summary
summary = tracer.get_span_summary()
print(f"\n📊 Trace Summary:")
print(f"   Total spans: {summary['total_spans']}")
print(f"   Completed: {summary['completed_spans']}")
print(f"   Avg duration: {summary['avg_duration_ms']:.2f}ms")

# Export traces
trace_file = tracer.export_traces("demo_traces.json")
print(f"\n✅ Traces exported to: {trace_file}")

print("\n2. METRICS COLLECTION")
print("-" * 80)

# Record metrics
metrics.increment("reviews_completed", 1)
metrics.increment("bugs_found", 5)
metrics.record_timing("review_duration", 2.5)
metrics.record_timing("review_duration", 1.8)
metrics.record_timing("review_duration", 3.2)
metrics.record_value("code_complexity", 8.5)
metrics.record_value("code_quality_score", 92.0)

print(f"✅ Recorded 7 metrics")

# Get metrics
print(f"\n📊 Counter Metrics:")
print(f"   Reviews completed: {metrics.get_counter('reviews_completed')}")
print(f"   Bugs found: {metrics.get_counter('bugs_found')}")

print(f"\n📊 Timing Metrics (review_duration):")
timing_stats = metrics.get_timing_stats("review_duration")
print(f"   Count: {timing_stats['count']}")
print(f"   Average: {timing_stats['avg']:.2f}s")
print(f"   Min: {timing_stats['min']:.2f}s")
print(f"   Max: {timing_stats['max']:.2f}s")
print(f"   P95: {timing_stats['p95']:.2f}s")

print(f"\n📊 Value Metrics:")
complexity_stats = metrics.get_value_stats("code_complexity")
quality_stats = metrics.get_value_stats("code_quality_score")
print(f"   Code complexity: {complexity_stats['avg']:.1f}")
print(f"   Quality score: {quality_stats['avg']:.1f}")

# Export metrics
metrics.export_metrics(".demo_traces/demo_metrics.json")
print(f"\n✅ Metrics exported to: .demo_traces/demo_metrics.json")

print("\n" + "=" * 80)
print("WHERE TO FIND TRACKING DATA")
print("=" * 80)

print("\n📁 File Locations:")
print(f"   Sessions: {session_manager.storage_path}/")
print(f"   Memory Bank: {memory_bank.storage_path}/memories.json")
print(f"   Traces: {tracer.export_path}/")
print(f"   Metrics: .demo_traces/demo_metrics.json")

print("\n🔧 Implementation Files:")
print("   agent/session_manager.py (Lines 1-394)")
print("      - SessionManager class (Lines 24-256)")
print("      - MemoryBank class (Lines 258-393)")
print("   agent/observability.py (Lines 1-357)")
print("      - AgentTracer class (Lines 33-226)")
print("      - MetricsCollector class (Lines 228-356)")

print("\n📊 Real-time Data:")

# Show actual files
if Path(f"{session_manager.storage_path}/{session_id}.json").exists():
    print(f"\n✅ Session file exists: {session_manager.storage_path}/{session_id}.json")
    with open(f"{session_manager.storage_path}/{session_id}.json", 'r') as f:
        session_file = json.load(f)
        print(f"   Size: {len(json.dumps(session_file))} bytes")
        print(f"   Contains: {len(session_file.get('interactions', []))} interactions")

if Path(f"{memory_bank.storage_path}/memories.json").exists():
    print(f"\n✅ Memory bank file exists: {memory_bank.storage_path}/memories.json")
    with open(f"{memory_bank.storage_path}/memories.json", 'r') as f:
        memory_file = json.load(f)
        total_memories = sum(len(v) for v in memory_file.values())
        print(f"   Total memories: {total_memories}")
        print(f"   Categories: {list(memory_file.keys())}")

if Path(trace_file).exists():
    print(f"\n✅ Trace file exists: {trace_file}")
    with open(trace_file, 'r') as f:
        trace_file_data = json.load(f)
        print(f"   Spans: {len(trace_file_data['spans'])}")
        print(f"   Events: {len(trace_file_data['events'])}")

print("\n" + "=" * 80)
print("API USAGE EXAMPLES")
print("=" * 80)

print("\n1. Track Session Memory:")
print("""
from agent.session_manager import SessionManager

session_manager = SessionManager()
session_id = session_manager.create_session()

# Save each interaction
session_manager.save_interaction(session_id, {
    "type": "code_review",
    "result": "..."
})

# Get history
history = session_manager.get_history(session_id)
""")

print("\n2. Store Long-term Memory:")
print("""
from agent.session_manager import MemoryBank

memory_bank = MemoryBank()

# Store learnings
memory_bank.store_memory("common_bugs", {
    "pattern": "sql_injection",
    "fix": "Use parameterized queries"
})

# Retrieve patterns
bugs = memory_bank.retrieve_memories("common_bugs")
""")

print("\n3. Track Traces:")
print("""
from agent.observability import AgentTracer

tracer = AgentTracer()

# Start span
span_id = tracer.start_span("code_review")

# Add events
tracer.add_span_event(span_id, "analysis_complete")

# End span
tracer.end_span(span_id)

# Export
tracer.export_traces("traces.json")
""")

print("\n4. Collect Metrics:")
print("""
from agent.observability import MetricsCollector

metrics = MetricsCollector()

# Record metrics
metrics.increment("reviews_completed")
metrics.record_timing("review_duration", 2.5)
metrics.record_value("code_quality", 95.0)

# Get stats
stats = metrics.get_timing_stats("review_duration")
summary = metrics.get_summary()
""")

print("\n" + "=" * 80)
print("✅ MEMORY AND OBSERVABILITY TRACKING COMPLETE!")
print("=" * 80)
print("\nAll tracking data is being automatically saved to:")
print(f"  - {session_manager.storage_path}/ (sessions)")
print(f"  - {memory_bank.storage_path}/ (memories)")
print(f"  - {tracer.export_path}/ (traces)")
print("\nYou can view these files to see real-time tracking data!")
