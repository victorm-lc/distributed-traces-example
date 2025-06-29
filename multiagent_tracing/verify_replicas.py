#!/usr/bin/env python3
"""
Simple script to verify that replica tracing is working correctly.
"""

import os
from langsmith.run_helpers import traceable, tracing_context

# Ensure tracing is enabled
os.environ["LANGSMITH_TRACING"] = "true"

@traceable(name="test_replicas", project_name="test-main-project")
def test_replicas():
    """Test function to verify replicas work."""
    print("Testing replica functionality...")
    
    # Test with replicas
    with tracing_context(
        project_name="test-sub-project",
        replicas=[("test-main-project", None)]
    ):
        print("This should appear in both test-sub-project and test-main-project")
        result = 2 + 2
        print(f"Result: {result}")
    
    return "Replica test complete"

if __name__ == "__main__":
    print("Running replica test...")
    result = test_replicas()
    print(result)
    print("\nCheck LangSmith for:")
    print("1. 'test-main-project' - Should show the complete trace")
    print("2. 'test-sub-project' - Should show the inner trace") 