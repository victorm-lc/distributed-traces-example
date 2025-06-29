# LangSmith Distributed Traces Patterns

Practical examples demonstrating distributed tracing patterns with LangSmith for multi-service LLM applications.

## 🎯 Purpose 

This repository shows how to implement distributed tracing with LangSmith across different LLM application architectures:

- **Debug multi-service workflows** with complete trace visibility
- **Monitor distributed agent systems** with proper context propagation
- **Handle complex scenarios** like multi-project tracing and cross-platform deployments

## 📋 Tracing Strategies Overview

### 1. **Basic Cross-Service Tracing** ⭐ *Now with LLM Integration*
**Pattern**: Client-server communication with header-based context propagation and middleware integration, featuring real ChatOpenAI calls
**When to use**: Microservices, API gateways, web frameworks (FastAPI, Express) with LLM processing
**Key concepts**: `langsmith-trace` headers, `TracingMiddleware`, automatic context extraction, LLM call tracing
**Demo features**:
- **Client-side**: LLM preprocessing and response analysis
- **Server-side**: LLM research and summarization  
- **Full tracing**: Token usage, costs, latency across distributed LLM calls

### 2. **Multi-Agent Cross-Platform Tracing** ⭐ *Now with LangGraph Integration*
**Pattern**: Distributed tracing across multi-agent systems where sub-agents are deployed on different platforms, requiring both cross-platform context propagation AND multi-project trace visibility.

**The Challenge**: When a supervisor agent (Platform Team, deployed on LangGraph Platform) orchestrates sub-agents (Product Teams, deployed elsewhere), organizations face a dual challenge:
- **Cross-platform tracing**: Sub-agents deployed on external services don't automatically appear in LangSmith traces
- **Multi-project visibility**: Teams need both supervisor visibility (complete traces) AND sub-agent team visibility (only their portions) in separate projects

**Current Limitation**: Distributed tracing context propagation forces all trace data to go to one project (the parent's), preventing sub-agents from simultaneously tracing to their own projects while maintaining cross-platform trace continuity.

**When to use**: 
- Platform teams running supervisor agents on LangGraph Platform that route to externally-deployed sub-agents
- Organizations where different teams own and deploy different parts of an agent workflow
- Production systems requiring both end-to-end visibility and team-specific trace isolation
- Hybrid deployments with agents across different platforms and LangSmith projects

**Key concepts**: Cross-platform context propagation, multi-project trace splitting, dual tracing contexts
**Demo features** (`multi_agent_tracing/cross_platform_dual_tracing/`):
- **Supervisor Agent**: LangGraph Platform-deployed agent that routes requests to sub-agents
- **Sub-Agents**: FastAPI-deployed agents owned by different product teams  
- **Cross-platform propagation**: Proper trace linking when supervisor calls external sub-agents
- **Dual project tracing**: Supervisor sees complete workflow, sub-agent teams see only their portions
- **Team isolation**: Each team gets relevant trace data in their own LangSmith project


## 🚀 Getting Started

1. **Environment Setup**: Set up your environment variables:
   ```bash
   # LangSmith Configuration
   export LANGSMITH_API_KEY=your_langsmith_api_key_here
   export LANGSMITH_PROJECT=distributed-traces-demo
   export LANGSMITH_TRACING=true
   
   # OpenAI Configuration  
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Prerequisites

- Python 3.8+
- LangSmith API key
- Basic understanding of distributed systems concepts

## 🧠 Key Concepts

**Context Propagation**: Distributed tracing relies on propagating trace context across service boundaries via HTTP headers (`langsmith-trace`, `baggage`)

**Trace Hierarchy**: 
- **Trace**: Top-level request spanning multiple services
- **Spans/Runs**: Individual operations within a trace
- **Context**: Information linking spans across service boundaries

## 🤝 Contributing

Found a pattern we're missing? Encountered a unique use case? Contributions are welcome! Please:

1. Follow the existing notebook structure
2. Include complete, runnable examples
3. Document performance implications
4. Add links to relevant LangSmith documentation

## 📚 Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

