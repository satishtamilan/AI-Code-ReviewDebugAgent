"""
Example usage of the Code Review and Debug Agent.
"""
from agent import CodeReviewAgent, DebugAgent
import json


def example_code_review():
    """Demonstrate code review functionality."""
    print("=" * 60)
    print("Example: Code Review")
    print("=" * 60)
    
    # Sample code with issues
    code_to_review = """
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
    
    # Initialize the agent
    agent = CodeReviewAgent()
    
    # Review the code
    print("\nReviewing code...\n")
    result = agent.review_code(code_to_review, language="python")
    
    if result.get("success"):
        print("✓ Review completed successfully!\n")
        print(result["formatted_report"])
        print("\nFull review details:")
        print(json.dumps(result["review"], indent=2))
    else:
        print(f"✗ Review failed: {result.get('error')}")
    
    # Get statistics
    stats = agent.get_summary_statistics()
    print("\n" + "=" * 60)
    print("Review Statistics:")
    print(json.dumps(stats, indent=2))


def example_debug():
    """Demonstrate debugging functionality."""
    print("\n" + "=" * 60)
    print("Example: Debug Code")
    print("=" * 60)
    
    # Sample code with a bug
    buggy_code = """
def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)
print(result)
"""
    
    error_message = "ZeroDivisionError: division by zero"
    stack_trace = """
  File "example.py", line 5, in <module>
    result = divide_numbers(10, 0)
  File "example.py", line 2, in divide_numbers
    return a / b
ZeroDivisionError: division by zero
"""
    
    # Initialize the agent
    agent = DebugAgent()
    
    # Debug the code
    print("\nDebugging code...\n")
    result = agent.debug_code(
        code=buggy_code,
        error_message=error_message,
        stack_trace=stack_trace,
        expected_behavior="Return the division result",
        actual_behavior="Raises ZeroDivisionError",
        language="python"
    )
    
    if result.get("success"):
        print("✓ Debug completed successfully!\n")
        debug_info = result["debug"]
        print(f"Root Cause: {debug_info.get('root_cause')}")
        print(f"\nExplanation: {debug_info.get('explanation')}")
        print(f"\nFixed Code:\n{debug_info.get('fixed_code')}")
        print(f"\nFix Explanation: {debug_info.get('fix_explanation')}")
    else:
        print(f"✗ Debug failed: {result.get('error')}")


def example_auto_fix():
    """Demonstrate auto-fix functionality."""
    print("\n" + "=" * 60)
    print("Example: Auto-Fix")
    print("=" * 60)
    
    code_with_issue = """
def find_max(numbers):
    max = numbers[0]
    for num in numbers:
        if num > max:
            max = num
    return max
"""
    
    issue = "Code doesn't handle empty list - will raise IndexError"
    
    # Initialize the agent
    agent = DebugAgent()
    
    # Auto-fix the code
    print("\nAuto-fixing code...\n")
    result = agent.auto_fix(
        code=code_with_issue,
        issue_description=issue,
        language="python"
    )
    
    if result.get("success"):
        print("✓ Auto-fix completed successfully!\n")
        print("Original Code:")
        print(result["original_code"])
        print("\nFixed Code:")
        print(result["fixed_code"])
    else:
        print(f"✗ Auto-fix failed: {result.get('error')}")


def main():
    """Run all examples."""
    print("\n")
    print("█" * 60)
    print(" " * 10 + "Code Review & Debug Agent Examples")
    print("█" * 60)
    
    try:
        example_code_review()
    except Exception as e:
        print(f"\n✗ Code review example failed: {e}")
    
    try:
        example_debug()
    except Exception as e:
        print(f"\n✗ Debug example failed: {e}")
    
    try:
        example_auto_fix()
    except Exception as e:
        print(f"\n✗ Auto-fix example failed: {e}")
    
    print("\n" + "█" * 60)
    print("Examples completed!")
    print("█" * 60 + "\n")


if __name__ == "__main__":
    main()


