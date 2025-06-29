#!/usr/bin/env python3
"""
Multi-Agent Distributed Tracing Demo Runner
Cross-platform script to run the distributed tracing demo
"""

import os
import sys
import subprocess
import shutil

def main():
    print("🚀 Multi-Agent Distributed Tracing Demo")
    print("======================================")
    print()
    
    # Check if LANGSMITH_API_KEY is set
    if not os.environ.get("LANGSMITH_API_KEY"):
        print("❌ ERROR: LANGSMITH_API_KEY environment variable is not set!")
        print("Please set it with: export LANGSMITH_API_KEY=your_api_key")
        sys.exit(1)
    
    # Ensure LANGSMITH_TRACING is enabled
    os.environ["LANGSMITH_TRACING"] = "true"
    
    print("✅ LangSmith API key detected")
    print()
    
    # Check if langgraph CLI is available
    print("📦 Checking dependencies...")
    if not shutil.which("langgraph"):
        print("Installing langgraph-cli[inmem]...")
        subprocess.run([sys.executable, "-m", "pip", "install", "langgraph-cli[inmem]"], check=True)
    
    print()
    print("🔧 Starting services...")
    print()
    
    # Run the test script
    subprocess.run([sys.executable, "multiagent_tracing/test_distributed_tracing.py"])

if __name__ == "__main__":
    main() 