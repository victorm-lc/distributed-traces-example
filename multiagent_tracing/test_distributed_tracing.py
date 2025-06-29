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
        processes.append(start_server("multiagent_tracing/writing_sub_agent/start_server.py", "Writing Agent (port 2026)"))
        processes.append(start_langgraph_supervisor("Supervisor Agent (port 8123)"))
        
        print("\nAll servers started! Waiting a moment for initialization...")
        time.sleep(3)
        
        # Test the distributed tracing
        print("\n" + "="*80)
        print("TESTING DISTRIBUTED TRACING")
        print("="*80)
        
        # Step 1: Create a thread
        print("\nStep 1: Creating thread...")
        thread_response = requests.post(
            "http://127.0.0.1:8123/threads",
            json={},
            headers={"Content-Type": "application/json"}
        )
        
        if thread_response.status_code != 200:
            print(f"ERROR: Failed to create thread - {thread_response.status_code}")
            print(thread_response.text[:500])
            return
            
        thread_data = thread_response.json()
        thread_id = thread_data["thread_id"]
        print(f"✅ Created thread: {thread_id}")
        
        # Step 2: Execute the supervisor workflow
        print("\nStep 2: Executing supervisor workflow...")
        
        response = requests.post(
            f"http://127.0.0.1:8123/threads/{thread_id}/runs/wait",
            json={
                "assistant_id": "supervisor_agent",
                "input": {
                    "messages": [
                        {
                            "type": "human",
                            "content": "what's some good news for today?"
                        }
                    ]
                }
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ SUCCESS! Supervisor workflow completed!")
            print("-" * 50)
            
            result = response.json()
            messages = result.get("messages", [])
            
            # Display the complete conversation
            print(f"\n💬 Complete conversation ({len(messages)} messages):")
            print("="*60)
            
            for i, msg in enumerate(messages, 1):
                msg_type = msg.get("type", "unknown")
                content = msg.get("content", "")
                
                print(f"\n{i}. [{msg_type.upper()}]:")
                if len(content) > 300:
                    print(content[:300] + "...\n[truncated]")
                else:
                    print(content)
                print("-" * 40)
            
            print("\n" + "="*80)
            print("🔍 DISTRIBUTED TRACING RESULTS")  
            print("="*80)
            print("\n✅ Check your LangSmith dashboard - traces should show as COMPLETED!")
            print("\nProjects to check:")
            print("1. 'supervisor-distributed-traces' - Complete workflow with sub-agent calls")
            print("2. 'research-distributed-traces' - Research agent activity only") 
            print("3. 'writing-distributed-traces' - Writing agent activity only")
            print("\n🎯 The supervisor project shows the full distributed trace!")
            
        else:
            print(f"\n❌ ERROR: Request failed with status {response.status_code}")
            print(response.text[:500])
            
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