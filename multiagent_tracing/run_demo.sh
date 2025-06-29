#!/bin/bash

# Multi-Agent Distributed Tracing Demo Runner
# This script starts all necessary services and runs the demo

echo "🚀 Multi-Agent Distributed Tracing Demo"
echo "======================================"
echo ""

# Check if LANGSMITH_API_KEY is set
if [ -z "$LANGSMITH_API_KEY" ]; then
    echo "❌ ERROR: LANGSMITH_API_KEY environment variable is not set!"
    echo "Please set it with: export LANGSMITH_API_KEY=your_api_key"
    exit 1
fi

# Ensure LANGSMITH_TRACING is enabled
export LANGSMITH_TRACING=true

echo "✅ LangSmith API key detected"
echo ""

# Install dependencies if needed
echo "📦 Checking dependencies..."
if ! command -v langgraph &> /dev/null; then
    echo "Installing langgraph-cli[inmem]..."
    pip install langgraph-cli[inmem]
fi

echo ""
echo "🔧 Starting services..."
echo ""

# Run the Python test script
python multiagent_tracing/test_distributed_tracing.py 