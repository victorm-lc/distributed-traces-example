# LangSmith Distributed Traces Patterns

A comprehensive collection of patterns and strategies for implementing distributed tracing with LangSmith across various architectures and use cases. This repository provides practical notebooks demonstrating different approaches to trace complex LLM applications spanning multiple services, processes, and environments.

## 🤔 Why Distributed Tracing for LLM Applications?

Traditional observability tools focus on HTTP requests and database queries. LLM applications introduce unique challenges:

- **Non-deterministic behavior**: Same prompt → different responses
- **Complex workflows**: RAG pipelines, multi-agent systems, tool usage
- **Variable performance**: Simple chat (500ms) vs complex reasoning (30s) 
- **LLM-specific data**: Prompts, completions, token usage, costs
- **Streaming responses**: Partial outputs over time

**Without distributed tracing**: Scattered logs across services, no visibility into LLM reasoning steps, hard to debug multi-agent workflows

**With LangSmith distributed tracing**: Complete request flow, LLM-specific insights, agent decision tracking, performance optimization across services

## 🎯 Purpose 

LLM applications are increasingly distributed across multiple services, from simple client-server setups to complex multi-agent workflows. Traditional observability tools fall short when dealing with the unique challenges of LLM applications - long-running conversations, streaming responses, tool calls, and dynamic agent behaviors. This repository provides battle-tested patterns for distributed tracing with LangSmith to help you:

- **Debug complex multi-service workflows** with full visibility across your stack
- **Monitor production performance** of distributed LLM applications
- **Optimize latency and costs** by understanding bottlenecks across services  
- **Implement proper context propagation** in various architectural patterns
- **Handle edge cases** like async operations, streaming, and concurrent processing

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
**Pattern**: Distributed tracing across LangGraph agents deployed as separate services or when agents invoke external services
**When to use**: 
- Agents deployed as microservices that call each other
- LangGraph workflows that invoke external APIs or databases
- Multi-tenant systems where different agents run in isolated environments
- Cross-organization agent collaboration
**Key concepts**: Service-to-service context propagation, external tool tracing, cross-deployment visibility
**Demo features**:
- **Service architecture**: FastAPI service hosting LangGraph agents
- **External calls**: Agents making HTTP requests to other services
- **Context propagation**: Maintaining trace continuity across service boundaries
- **Tool tracing**: Custom tools that call external APIs with proper trace linking


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

### LangGraph vs Distributed Tracing Decision Tree

**Use LangSmith's Built-in Tracing When:**
- Your LangGraph agents run in a single process/service
- All tools and resources are accessible from the same runtime
- You need to trace agent state transitions, tool calls, and decision flows
- Your multi-agent system is contained within one deployment

**Use Distributed Tracing When:**
- Your agents are deployed as separate microservices
- Agents need to call external APIs or databases
- You have cross-service communication between agents
- You need to trace requests across multiple deployment boundaries
- You're integrating with existing distributed systems

### Context Propagation
Distributed tracing relies on propagating context across service boundaries. LangSmith supports this through:
- **HTTP headers** (`langsmith-trace`, `baggage`)
- **Environment context** (`tracing_context`, `withRunTree`)
- **Manual propagation** for complex scenarios

### Trace Hierarchy
Understanding parent-child relationships in distributed traces:
- **Trace**: Top-level request spanning multiple services
- **Spans/Runs**: Individual operations within a trace
- **Context**: Information linking spans across service boundaries

### Performance Considerations
- **Native format**: Optimal for LangSmith-only environments
- **OpenTelemetry**: Better for polyglot/interop scenarios
- **Sampling**: Critical for high-throughput production systems

## 📊 When to Use Each Pattern

| Pattern | Best For | Avoid When |
|---------|----------|------------|
| Basic Cross-Service | Microservices, web APIs, simple distributed systems | Single-process applications |
| Multi-Agent Workflows | Agents deployed as separate services, cross-service agent communication | Single-process LangGraph applications (use built-in LangSmith tracing) |
| OpenTelemetry | Polyglot systems, existing OTel infrastructure | LangSmith-only simple applications |
| Async & Streaming | Real-time apps, streaming responses, concurrent processing | Simple synchronous workflows |
| Production Patterns | High-scale production, performance-sensitive systems | Development/testing environments |
| Troubleshooting | Debugging complex issues, custom implementations | Standard use cases with working patterns |

## 🎯 Success Metrics

Track these metrics to measure the effectiveness of your distributed tracing:

- **Trace Completeness**: % of requests with full trace coverage
- **Context Propagation Success**: % of spans properly linked
- **Performance Impact**: Added latency from tracing overhead
- **Debug Time Reduction**: Time saved in debugging distributed issues
- **Production Visibility**: Coverage of production error scenarios

## 🤝 Contributing

Found a pattern we're missing? Encountered a unique use case? Contributions are welcome! Please:

1. Follow the existing notebook structure
2. Include complete, runnable examples
3. Document performance implications
4. Add links to relevant LangSmith documentation

## 📚 Additional Resources

- [LangSmith Distributed Tracing Docs](https://docs.smith.langchain.com/observability/how_to_guides/distributed_tracing)
- [OpenTelemetry Integration Guide](https://docs.smith.langchain.com/observability/how_to_guides/trace_with_opentelemetry)
- [LangGraph Tracing Examples](https://docs.smith.langchain.com/observability/how_to_guides/trace_with_langgraph)
- [Production Best Practices](https://docs.smith.langchain.com/observability/concepts)

