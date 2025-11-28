"""
Enhanced Example demonstrating all Kaggle competition requirements.

This example showcases:
1. Multi-agent system (sequential and loop workflows)
2. Custom tools (syntax checker, complexity analyzer, security scanner)
3. Sessions & Memory (state management, conversation history)
4. Observability (logging, tracing, metrics)
5. Context engineering (summarization, compaction)
"""
import json
from agent import (
    MultiAgentOrchestrator,
    SessionManager,
    MemoryBank,
    ToolRegistry,
    ContextCompactor,
)


def demo_sequential_workflow():
    """
    Demo 1: Sequential Multi-Agent Workflow
    
    Demonstrates: Sequential agents working together
    """
    print("\n" + "=" * 70)
    print("DEMO 1: SEQUENTIAL MULTI-AGENT WORKFLOW")
    print("=" * 70)
    
    # Sample buggy code
    code = """
def calculate_average(numbers):
    sum = 0
    for i in range(len(numbers)):
        sum = sum + numbers[i]
    return sum / len(numbers)

def process_data(data):
    result = []
    for item in data:
        if item != None:
            result.append(item * 2)
    return result
"""
    
    # Create orchestrator with observability
    orchestrator = MultiAgentOrchestrator(
        enable_tracing=True,
        enable_metrics=True,
    )
    
    print("\n🤖 Executing sequential workflow: Review → Debug → Fix\n")
    
    # Execute sequential workflow
    result = orchestrator.execute_sequential_workflow(
        code=code,
        language="python",
        session_id="demo_session_1",
    )
    
    if result.get("success"):
        print(f"✅ Workflow completed in {result['execution_time_seconds']:.2f}s")
        print(f"\n📊 Steps executed: {len(result['steps'])}")
        
        for step in result['steps']:
            print(f"\n  Step {step['step']}: {step['agent']}")
            if step['agent'] == "CodeReviewer":
                review = step['result'].get('review', {})
                issues = review.get('issues', [])
                print(f"    - Found {len(issues)} issues")
            elif step['agent'] == "Debugger":
                debug = step['result'].get('debug', {})
                print(f"    - Root cause: {debug.get('root_cause', 'N/A')}")
            elif step['agent'] == "AutoFixer":
                print(f"    - Code fixed successfully")
    
    # Get metrics
    print("\n📈 Metrics Summary:")
    metrics = orchestrator.get_metrics_summary()
    if metrics.get('counters'):
        for metric, value in metrics['counters'].items():
            print(f"  {metric}: {value}")
    
    # Get traces
    print("\n🔍 Trace Log (last 3 events):")
    traces = orchestrator.get_trace_log()
    for trace in traces[-3:]:
        print(f"  [{trace['type']}] {json.dumps(trace['data'])}")


def demo_loop_workflow():
    """
    Demo 2: Loop-based Iterative Refinement
    
    Demonstrates: Loop agents for iterative improvement
    """
    print("\n" + "=" * 70)
    print("DEMO 2: LOOP-BASED ITERATIVE REFINEMENT")
    print("=" * 70)
    
    # Code to refine
    code = """
def divide(a, b):
    return a / b

x = divide(10, 0)
"""
    
    orchestrator = MultiAgentOrchestrator(
        enable_tracing=True,
        enable_metrics=True,
    )
    
    print("\n🔄 Executing loop workflow: Iterative quality improvement\n")
    
    result = orchestrator.execute_loop_workflow(
        code=code,
        max_iterations=3,
        quality_threshold=0.85,
        language="python",
        session_id="demo_session_2",
    )
    
    if result.get("success"):
        print(f"✅ Loop workflow completed")
        print(f"\n📊 Iterations: {result['num_iterations']}")
        print(f"   Initial quality: {result['initial_quality']:.2f}")
        print(f"   Final quality: {result['final_quality']:.2f}")
        print(f"   Improvement: {(result['final_quality'] - result['initial_quality']):.2f}")
        
        for iteration in result['iterations']:
            print(f"\n  Iteration {iteration['iteration']}:")
            print(f"    Quality score: {iteration['quality_score']:.2f}")
            print(f"    Issues found: {iteration['num_issues']}")
            print(f"    Status: {iteration.get('status', 'processing')}")


def demo_custom_tools():
    """
    Demo 3: Custom Tools
    
    Demonstrates: Custom tools for code analysis
    """
    print("\n" + "=" * 70)
    print("DEMO 3: CUSTOM TOOLS")
    print("=" * 70)
    
    code = """
import os
password = "hardcoded123"

def process():
    eval("dangerous code")
    os.system("rm -rf /")
"""
    
    # Create tool registry
    registry = ToolRegistry()
    
    print("\n🔧 Available tools:")
    for tool in registry.list_tools():
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Run syntax checker
    print("\n\n1️⃣ Syntax Checker:")
    result = registry.execute_tool("syntax_checker", code=code, language="python")
    if result.success:
        print(f"   Valid: {result.output.get('valid', False)}")
        if not result.output.get('valid'):
            print(f"   Error: {result.output.get('message')}")
    
    # Run complexity analyzer
    print("\n2️⃣ Complexity Analyzer:")
    result = registry.execute_tool("complexity_analyzer", code=code)
    if result.success:
        metrics = result.output
        print(f"   Lines of code: {metrics.get('code_lines')}")
        print(f"   Cyclomatic complexity: {metrics.get('cyclomatic_complexity')}")
        print(f"   Max nesting depth: {metrics.get('max_nesting_depth')}")
    
    # Run security scanner
    print("\n3️⃣ Security Scanner:")
    result = registry.execute_tool("security_scanner", code=code, language="python")
    if result.success:
        findings = result.output.get('findings', [])
        print(f"   Vulnerabilities found: {len(findings)}")
        for finding in findings[:3]:  # Show first 3
            print(f"   - Line {finding['line']}: [{finding['severity']}] {finding['message']}")


def demo_session_and_memory():
    """
    Demo 4: Sessions and Memory
    
    Demonstrates: State management and long-term memory
    """
    print("\n" + "=" * 70)
    print("DEMO 4: SESSIONS AND MEMORY")
    print("=" * 70)
    
    # Create session manager
    session_mgr = SessionManager()
    
    # Create a session
    session_id = session_mgr.create_session()
    print(f"\n📝 Created session: {session_id}")
    
    # Save interactions
    print("\n💾 Saving interactions...")
    session_mgr.save_interaction(session_id, {
        "type": "code_review",
        "result": "Found 3 issues",
    })
    session_mgr.save_interaction(session_id, {
        "type": "debug",
        "result": "Fixed null pointer issue",
    })
    
    # Update context
    session_mgr.update_context(session_id, {
        "language": "python",
        "project": "web_app",
        "user_preferences": {"verbose": True},
    })
    
    # Get history
    history = session_mgr.get_history(session_id)
    print(f"   Interactions: {len(history)}")
    
    # Get context
    context = session_mgr.get_context(session_id)
    print(f"   Context: {json.dumps(context, indent=4)}")
    
    # Demo memory bank
    print("\n\n🧠 Long-term Memory Bank:")
    memory_bank = MemoryBank()
    
    # Store memories
    memory_bank.store_memory("common_bugs", {
        "pattern": "null_pointer",
        "description": "Accessing object without null check",
        "severity": "high",
    })
    
    memory_bank.store_memory("common_bugs", {
        "pattern": "division_by_zero",
        "description": "Dividing without zero check",
        "severity": "high",
    })
    
    # Retrieve common patterns
    patterns = memory_bank.get_common_patterns("common_bugs", top_n=3)
    print(f"   Common bug patterns:")
    for pattern in patterns:
        print(f"   - {pattern['pattern']}: {pattern['count']} occurrences")


def demo_context_engineering():
    """
    Demo 5: Context Engineering
    
    Demonstrates: Context compaction and optimization
    """
    print("\n" + "=" * 70)
    print("DEMO 5: CONTEXT ENGINEERING")
    print("=" * 70)
    
    # Long code that needs compaction
    long_code = """
# This is a comment
def function1():
    # Another comment
    x = 1
    
    # More comments
    y = 2
    
    
    return x + y

def function2():
    # Yet another comment
    a = 10
    
    
    b = 20
    return a * b

def function3():
    pass
"""
    
    compactor = ContextCompactor(max_tokens=4000)
    
    # Estimate tokens
    tokens = compactor.estimate_tokens(long_code)
    print(f"\n📏 Original code tokens: ~{tokens}")
    
    # Compact code
    print("\n🗜️ Compacting code...")
    compacted = compactor.compact_code(long_code, preserve_structure=False)
    compacted_tokens = compactor.estimate_tokens(compacted)
    print(f"   Compacted tokens: ~{compacted_tokens}")
    print(f"   Reduction: {((tokens - compacted_tokens) / tokens * 100):.1f}%")
    
    # Summarize code
    print("\n📝 Code summary:")
    summary = compactor.summarize_code_block(long_code, language="python")
    print(f"   {summary}")
    
    # Optimize prompt context
    print("\n⚙️ Optimizing prompt context...")
    optimized = compactor.optimize_prompt_context(
        prompt="Review this code for issues:",
        code=long_code,
        additional_context=["This is a backend service", "Focus on performance"],
    )
    print(f"   Estimated total tokens: {optimized['estimated_tokens']}")


def main():
    """Run all demos."""
    print("\n")
    print("█" * 70)
    print(" " * 15 + "ENHANCED AGENT DEMONSTRATION")
    print(" " * 10 + "Kaggle Agents Intensive Capstone Project")
    print("█" * 70)
    
    print("\n✨ This demo showcases all required competition features:")
    print("   1. Multi-agent system (sequential & loop workflows)")
    print("   2. Custom tools (syntax, complexity, security)")
    print("   3. Sessions & Memory (state management)")
    print("   4. Observability (tracing & metrics)")
    print("   5. Context engineering (compaction)")
    
    try:
        demo_sequential_workflow()
    except Exception as e:
        print(f"\n❌ Demo 1 error: {e}")
    
    try:
        demo_loop_workflow()
    except Exception as e:
        print(f"\n❌ Demo 2 error: {e}")
    
    try:
        demo_custom_tools()
    except Exception as e:
        print(f"\n❌ Demo 3 error: {e}")
    
    try:
        demo_session_and_memory()
    except Exception as e:
        print(f"\n❌ Demo 4 error: {e}")
    
    try:
        demo_context_engineering()
    except Exception as e:
        print(f"\n❌ Demo 5 error: {e}")
    
    print("\n" + "█" * 70)
    print(" " * 20 + "DEMO COMPLETED")
    print("█" * 70 + "\n")


if __name__ == "__main__":
    main()

