#!/usr/bin/env python3
"""
Test script to demonstrate distributed tracing across multi-agent system.

This script:
1. Starts all three agent servers (supervisor, research, writing)
2. Makes a request to the supervisor
3. Shows how traces propagate across agents and appear in multiple projects

Expected behavior:
- Supervisor project sees the complete trace including sub-agent activity
- Research agent project sees only research agent traces
- Writing agent project sees only writing agent traces
"""

import os
import time
import subprocess
import requests
import sys
import json
from typing import List

def start_server(script_path: str, name: str) -> subprocess.Popen:
    """Start a server in a subprocess."""
    print(f"Starting {name}...")
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(3)  # Give server time to start
    return process

def start_langgraph_supervisor(name: str) -> subprocess.Popen:
    """Start the supervisor using langgraph dev."""
    print(f"Starting {name} with langgraph dev...")
    process = subprocess.Popen(
        ["langgraph", "dev", "--port", "8123"],  # Using different port to avoid conflicts
        cwd="multiagent_tracing/supervisor",  # Run from supervisor directory
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    time.sleep(5)  # Give LangGraph more time to start
    return process

def stop_servers(processes: List[subprocess.Popen]):
    """Stop all server processes."""
    for process in processes:
        process.terminate()
        process.wait()

def test_distributed_tracing():
    """Test the distributed tracing across agents."""
    processes = []
    
    try:
        # Start all servers
        processes.append(start_server("multiagent_tracing/research_sub_agent/start_server.py", "Research Agent (port 2025)"))
        processes.append(start_server("multiagent_tracing/writing_sub_agent/start_server.py", "Writing Agent (port 2024)"))
        processes.append(start_langgraph_supervisor("Supervisor Agent (port 8123)"))
        
        print("\nAll servers started! Waiting a moment for initialization...")
        time.sleep(5)
        
        # Test the distributed tracing
        print("\n" + "="*80)
        print("TESTING DISTRIBUTED TRACING")
        print("="*80)
        
        # Make a request to the supervisor using LangGraph API format
        print("\nMaking request to supervisor agent via LangGraph API...")
        
        # Use LangGraph's streaming API
        response = requests.post(
            "http://127.0.0.1:8123/runs/stream",
            json={
                "assistant_id": "supervisor_agent",  # Graph name from langgraph.json
                "input": {
                    "messages": [
                        {
                            "type": "human",
                            "content": "Research the latest developments in quantum computing and write a brief report about it."
                        }
                    ]
                },
                "stream_mode": ["values"]
            },
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        if response.status_code == 200:
            print("\nSUCCESS! Receiving streamed response from supervisor:")
            print("-" * 40)
            
            # Process the streaming response
            final_messages = []
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]  # Remove "data: " prefix
                        try:
                            data = json.loads(data_str)
                            if isinstance(data, list) and len(data) > 0:
                                event = data[0]
                                if event.get("event") == "values":
                                    messages = event.get("data", {}).get("messages", [])
                                    if messages:
                                        final_messages = messages
                        except json.JSONDecodeError:
                            continue
            
            # Display the final messages
            for msg in final_messages[-3:]:  # Show last 3 messages
                msg_type = msg.get("type", "unknown")
                content = msg.get("content", "")
                print(f"Type: {msg_type}")
                print(f"Content: {content[:200]}...")
                print("-" * 40)
            
            print("\n" + "="*80)
            print("DISTRIBUTED TRACING RESULTS")
            print("="*80)
            print("\nCheck your LangSmith dashboard for traces in these projects:")
            print("1. 'supervisor-distributed-traces' - Should show COMPLETE trace including sub-agent calls")
            print("2. 'research-distributed-traces' - Should show ONLY research agent activity")
            print("3. 'writing-distributed-traces' - Should show ONLY writing agent activity")
            print("\nThe supervisor project should show the full workflow with nested traces from sub-agents.")
            print("Each sub-agent project should only show their specific traces.")
            
        else:
            print(f"\nERROR: Request failed with status {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n\nStopping all servers...")
        stop_servers(processes)
        print("All servers stopped.")

if __name__ == "__main__":
    print("Multi-Agent Distributed Tracing Demo")
    print("====================================")
    print("\nThis demo shows how to implement distributed tracing where:")
    print("- Supervisor agent (via LangGraph dev server) propagates trace context to sub-agents")
    print("- Sub-agents trace to BOTH their own project AND supervisor's project")
    print("- Each team sees only relevant traces in their project")
    print("\nMake sure you have LANGSMITH_API_KEY set in your environment!")
    print("\nNote: This requires 'langgraph dev' to be available (install with pip install langgraph-cli[inmem])")
    
    test_distributed_tracing() 