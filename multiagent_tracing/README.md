# Multi-Agent Distributed Tracing Example

This example demonstrates **distributed tracing across multi-agent systems** using LangSmith, where a supervisor agent orchestrates sub-agents running as separate services on different ports.

## 🎯 What This Demonstrates

**Cross-Service Multi-Agent Tracing**: Shows how to maintain trace continuity when a supervisor agent makes HTTP calls to sub-agents deployed as separate services, enabling full observability across distributed agent workflows.

**Key Features**:
- **Supervisor Agent**: Orchestrates workflow and routes requests to specialized sub-agents
- **Research Agent**: Performs web searches using Tavily to gather information  
- **Writer Agent**: Generates reports and documentation
- **Distributed Tracing**: Complete trace visibility across all HTTP service calls
- **Context Propagation**: Proper trace linking when supervisor calls external sub-agents

## 🏗️ Architecture

This system consists of three distributed services that communicate via HTTP:

```
┌─────────────────┐    HTTP POST     ┌──────────────────┐
│  Supervisor     │ ───────────────► │  Research Agent  │
│  Agent          │                  │  (Port 2025)     │
│  (Port 2026)    │                  └──────────────────┘
└─────────────────┘                           │
         │                                    │
         │            HTTP POST               │
         └────────────────────────────────────┼─────────────────┐
                                              │                 │
                                   ┌──────────────────┐        │
                                   │  Writer Agent    │        │
                                   │  (Port 2024)     │        │
                                   └──────────────────┘        │
                                                               │
                                                               ▼
                                                    LangSmith Traces
                                                (Complete observability)
```

**Components:**
- **Supervisor Agent (Port 2026)**: Orchestrates the workflow and routes requests to specialized sub-agents
- **Research Agent (Port 2025)**: Performs web searches using Tavily to gather information  
- **Writer Agent (Port 2024)**: Generates reports and documentation from research data
- **LangSmith**: Provides tracing across all HTTP service calls and subagents back up to supervisor agent

## 🛠️ Prerequisites

1. **Environment Variables**:
   ```bash
   # LangSmith Configuration
   export LANGSMITH_API_KEY=your_langsmith_api_key_here
   export LANGSMITH_PROJECT=multiagent-tracing-demo
   export LANGSMITH_TRACING=true
   
   # OpenAI Configuration  
   export OPENAI_API_KEY=your_openai_api_key_here
   
   # Tavily Configuration (for research agent)
   export TAVILY_API_KEY=your_tavily_api_key_here
   ```

2. **Install Project**: Install the project as an editable package from the project root:
   ```bash
   # Install the project and all dependencies
   pip install -e .
   
   # Or if you prefer using requirements.txt:
   pip install -r requirements.txt
   pip install -e .
   ```


## 🔧 Running the System

You'll need **3 separate terminals** to run this distributed system:

### Terminal 1: Research Agent (Port 2025)

```bash
cd multiagent_tracing/research_sub_agent
python start_server.py
```

Wait for the message: `Server is ready and listening on port 2025`

### Terminal 2: Writer Agent (Port 2024)

```bash
cd multiagent_tracing/writing_sub_agent
python start_server.py
```

Wait for the message: `Server is ready and listening on port 2024`

### Terminal 3: Supervisor Agent (Port 2026)

```bash
cd multiagent_tracing/supervisor
langgraph dev --port 2026
```

Wait for the message: `Server is ready and listening on port 2026`

## 🧪 Testing the System

LangGraph Studio

1. Open LangGraph Studio
2. Send a message like: `"Research the latest developments in AI agents and write a summary report"`


## 📊 Expected Workflow

1. **User Query**: "Research X and write a summary report"
2. **Supervisor**: Analyzes request and decides to route to research agent first
3. **Research Agent**: Uses Tavily to search for information about X
4. **Supervisor**: Receives research results and routes to writer agent
5. **Writer Agent**: Creates a formatted report from the research
6. **Supervisor**: Returns final report to user

## 🔍 Observing Distributed Traces

In LangSmith, you'll see:

1. **Complete Trace Hierarchy**: 
   - Root trace from supervisor
   - Child spans from HTTP calls to sub-agents
   - Nested spans within each agent (LLM calls, tool usage)

2. **Cross-Service Context**: 
   - Trace ID propagated across all HTTP calls
   - Complete workflow visibility despite distributed deployment

3. **Performance Metrics**:
   - End-to-end latency
   - Individual agent processing times
   - LLM token usage across all services

