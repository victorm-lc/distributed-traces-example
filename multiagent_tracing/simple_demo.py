#!/usr/bin/env python3
"""
Simple demonstration of cross-platform dual tracing pattern.

This example shows how to implement distributed tracing where:
- A supervisor agent calls sub-agents via HTTP
- Sub-agents trace to BOTH their own project AND the supervisor's project
- Each team sees only relevant traces in their project

Run this script and check your LangSmith dashboard to see traces in multiple projects.

Note: This is a simplified demo that doesn't require langgraph dev. 
For production use with LangGraph Platform, see test_distributed_tracing.py
"""

import os
import asyncio
import threading
from typing import Dict, Any
from fastapi import FastAPI, Request
import uvicorn
import httpx
from langchain_openai import ChatOpenAI
from langsmith.run_helpers import traceable, tracing_context, get_current_run_tree

# Configuration - in production these would be in different codebases/deployments
SUPERVISOR_PROJECT = "demo-supervisor-project"
RESEARCH_PROJECT = "demo-research-project"
WRITING_PROJECT = "demo-writing-project"

# ============================================================================
# SUB-AGENT 1: Research Agent (simulating external deployment)
# ============================================================================

research_app = FastAPI()

@research_app.post("/research")
async def research_endpoint(request: Request, data: Dict[str, Any]):
    """Research agent endpoint with distributed tracing."""
    # Extract trace headers from supervisor
    parent_headers = {}
    if langsmith_trace := request.headers.get("langsmith-trace"):
        parent_headers["langsmith-trace"] = langsmith_trace
    if baggage := request.headers.get("baggage"):
        parent_headers["baggage"] = baggage
    
    # Use distributed tracing with replicas
    with tracing_context(
        parent=parent_headers if parent_headers else None,
        replicas=[
            (RESEARCH_PROJECT, None),    # Research team's project
            (SUPERVISOR_PROJECT, None)   # Supervisor's project
        ] if parent_headers else [],
        project_name=RESEARCH_PROJECT  # Default project for this agent
    ):
        # Simulate research work
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        research_result = llm.invoke(
            f"Research this topic briefly (1-2 sentences): {data['topic']}"
        )
        
        return {
            "research": research_result.content,
            "source": "research_agent"
        }

# ============================================================================
# SUB-AGENT 2: Writing Agent (simulating external deployment)
# ============================================================================

writing_app = FastAPI()

@writing_app.post("/write")
async def write_endpoint(request: Request, data: Dict[str, Any]):
    """Writing agent endpoint with distributed tracing."""
    # Extract trace headers from supervisor
    parent_headers = {}
    if langsmith_trace := request.headers.get("langsmith-trace"):
        parent_headers["langsmith-trace"] = langsmith_trace
    if baggage := request.headers.get("baggage"):
        parent_headers["baggage"] = baggage
    
    # Use distributed tracing with replicas
    with tracing_context(
        parent=parent_headers if parent_headers else None,
        replicas=[
            (WRITING_PROJECT, None),     # Writing team's project
            (SUPERVISOR_PROJECT, None)   # Supervisor's project
        ] if parent_headers else [],
        project_name=WRITING_PROJECT  # Default project for this agent
    ):
        # Simulate writing work
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        report = llm.invoke(
            f"Write a brief report (2-3 sentences) based on this research: {data['research']}"
        )
        
        return {
            "report": report.content,
            "source": "writing_agent"
        }

# ============================================================================
# SUPERVISOR AGENT (simulating LangGraph Platform deployment)
# ============================================================================

@traceable(name="supervisor_workflow", project_name=SUPERVISOR_PROJECT)
async def supervisor_workflow(topic: str) -> str:
    """Supervisor agent that orchestrates sub-agents."""
    print(f"\n📋 Supervisor: Processing request for topic: {topic}")
    
    # Step 1: Call research agent with trace propagation
    print("📚 Supervisor: Calling research agent...")
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
    
    async with httpx.AsyncClient() as client:
        research_response = await client.post(
            "http://localhost:8001/research",
            json={"topic": topic},
            headers=headers
        )
        research_data = research_response.json()
        print(f"✅ Research completed: {research_data['research'][:100]}...")
    
    # Step 2: Call writing agent with trace propagation
    print("✍️  Supervisor: Calling writing agent...")
    async with httpx.AsyncClient() as client:
        writing_response = await client.post(
            "http://localhost:8002/write",
            json={"research": research_data["research"]},
            headers=headers
        )
        writing_data = writing_response.json()
        print(f"✅ Report written: {writing_data['report'][:100]}...")
    
    return f"FINAL REPORT:\n\n{writing_data['report']}"

# ============================================================================
# SERVER RUNNERS
# ============================================================================

def run_research_server():
    """Run research agent server."""
    uvicorn.run(research_app, host="localhost", port=8001, log_level="error")

def run_writing_server():
    """Run writing agent server."""
    uvicorn.run(writing_app, host="localhost", port=8002, log_level="error")

# ============================================================================
# MAIN DEMO
# ============================================================================

async def main():
    """Run the complete demo."""
    print("🚀 Cross-Platform Dual Tracing Demo")
    print("=" * 50)
    
    # Start sub-agent servers in background threads
    research_thread = threading.Thread(target=run_research_server, daemon=True)
    writing_thread = threading.Thread(target=run_writing_server, daemon=True)
    
    research_thread.start()
    writing_thread.start()
    
    # Give servers time to start
    await asyncio.sleep(2)
    
    # Run supervisor workflow
    print("\n🎯 Starting supervisor workflow...")
    result = await supervisor_workflow("quantum computing breakthroughs in 2024")
    
    print("\n" + "=" * 50)
    print("📊 RESULTS")
    print("=" * 50)
    print(result)
    
    print("\n" + "=" * 50)
    print("🔍 CHECK YOUR LANGSMITH DASHBOARD")
    print("=" * 50)
    print(f"\n1. Project: '{SUPERVISOR_PROJECT}'")
    print("   - Should show COMPLETE trace with nested sub-agent calls")
    print("   - Useful for platform team to debug entire workflows")
    
    print(f"\n2. Project: '{RESEARCH_PROJECT}'")
    print("   - Should show ONLY research agent traces")
    print("   - Useful for research team to focus on their component")
    
    print(f"\n3. Project: '{WRITING_PROJECT}'")
    print("   - Should show ONLY writing agent traces")
    print("   - Useful for writing team to focus on their component")
    
    print("\n✨ This demonstrates how teams can maintain separate projects")
    print("   while still enabling end-to-end tracing for platform teams!")

if __name__ == "__main__":
    # Ensure LangSmith tracing is enabled
    os.environ["LANGSMITH_TRACING"] = "true"
    
    # Run the demo
    asyncio.run(main()) 