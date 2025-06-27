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

### 2. **Multi-Agent Workflows** ⭐ *Now with LangGraph Integration*
**Pattern**: Distributed tracing across complex multi-agent systems with multi-project trace visibility and cross-platform deployments

#### 2a. **Multi-Project Distributed Tracing Pattern** (`multi_agent_tracing/dual_project_tracing/`)
**The Challenge**: When a supervisor agent (Platform Team) orchestrates sub-agents (Product Teams), organizations need:
- **Supervisor visibility**: Complete end-to-end traces including all sub-agent executions in the supervisor's project
- **Sub-agent team visibility**: Each product team sees only their sub-agent's trace data in their own project  
- **Dual tracing**: The same trace spans appear in multiple LangSmith projects simultaneously

**Current Limitation**: Distributed tracing context propagation forces all trace data to go to one project (the parent's), preventing sub-agents from simultaneously tracing to their own projects.

**When to use**: 
- Platform teams running supervisor agents that route to product team sub-agents
- Organizations where different teams own different parts of an agent workflow
- Scenarios requiring both end-to-end visibility and team-specific trace isolation
- Production systems with distributed ownership of agent components

**Key concepts**: Multi-project trace propagation, dual tracing contexts, project-specific trace visibility
**Demo features**:
- **Supervisor project**: Complete workflow traces including all sub-agent activities
- **Sub-agent projects**: Product teams see only their agent's portion of distributed traces
- **Context propagation**: Maintaining trace relationships while splitting across projects
- **Team isolation**: Each team gets relevant trace data in their own LangSmith project

#### 2b. **Cross-Platform Agent Orchestration Pattern** (`multi_agent_tracing/cross_platform/`)
**The Challenge**: When Agent A (deployed on LangGraph Platform) calls Agent B (deployed elsewhere), Agent B's activities don't automatically appear in LangSmith traces.

**When to use**:
- LangGraph Platform agents that invoke external agent services
- Hybrid deployments with agents across different platforms
- Integration with existing agent services not on LangGraph Platform
- Maintaining trace continuity across deployment boundaries

**Key concepts**: Cross-platform context propagation, external agent tracing, trace nesting across deployments
**Demo features**:
- **Agent A**: LangGraph Platform-deployed supervisor agent
- **Agent B**: Externally deployed sub-agent (FastAPI service)
- **Context propagation**: Proper trace linking when Agent A calls Agent B
- **Nested visibility**: Agent B's activities appear nested under the main workflow in LangSmith


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

