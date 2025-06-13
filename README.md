# LangSmith Distributed Traces Patterns

A comprehensive collection of patterns and strategies for implementing distributed tracing with LangSmith across various architectures and use cases. This repository provides practical notebooks demonstrating different approaches to trace complex LLM applications spanning multiple services, processes, and environments.

## 🎯 Purpose

LLM applications are increasingly distributed across multiple services, from simple client-server setups to complex multi-agent workflows. Traditional observability tools fall short when dealing with the unique challenges of LLM applications - long-running conversations, streaming responses, tool calls, and dynamic agent behaviors. This repository provides battle-tested patterns for distributed tracing with LangSmith to help you:

- **Debug complex multi-service workflows** with full visibility across your stack
- **Monitor production performance** of distributed LLM applications
- **Optimize latency and costs** by understanding bottlenecks across services  
- **Implement proper context propagation** in various architectural patterns
- **Handle edge cases** like async operations, streaming, and concurrent processing

## 📋 Tracing Strategies Overview

### 1. **Basic Cross-Service Tracing**
**Pattern**: Client-server communication with header-based context propagation and middleware integration
**When to use**: Microservices, API gateways, web frameworks (FastAPI, Express)
**Key concepts**: `langsmith-trace` headers, `TracingMiddleware`, automatic context extraction

### 2. **OpenTelemetry Integration**
**Pattern**: Standards-based tracing using OpenTelemetry protocol with LangSmith
**When to use**: Polyglot environments, existing OTel infrastructure, vendor-neutral observability
**Key concepts**: OTel exporters, semantic conventions, hybrid native/OTel approaches

### 3. **Async & Streaming Patterns**
**Pattern**: Context propagation in async workflows, streaming responses, and concurrent processing
**When to use**: Real-time applications, streaming LLM responses, batch processing, parallel execution
**Key concepts**: Asyncio compatibility, context isolation, streaming trace updates

### 4. **Multi-Agent Workflows**
**Pattern**: Complex agent orchestration and tool usage tracing in LangGraph applications
**When to use**: Multi-agent systems, agentic workflows, complex state-based applications
**Key concepts**: Agent communication, state transitions, hierarchical tracing

### 5. **Production Patterns**
**Pattern**: Performance optimization, sampling strategies, and monitoring for production systems
**When to use**: High-throughput systems, cost-sensitive environments, production monitoring
**Key concepts**: Sampling strategies, performance optimization, error handling, dashboards

### 6. **Troubleshooting & Edge Cases**
**Pattern**: Debugging context issues, trace nesting problems, and handling complex scenarios
**When to use**: Debugging distributed issues, custom frameworks, legacy integrations
**Key concepts**: Manual context propagation, error recovery, performance debugging

## 🏗️ Repository Structure

```
├── README.md
├── requirements.txt
├── setup/
│   ├── environment_setup.ipynb
│   └── common_utilities.py
├── notebooks/
│   ├── 01_basic_cross_service_tracing.ipynb
│   ├── 02_opentelemetry_integration.ipynb
│   ├── 03_async_streaming_patterns.ipynb
│   ├── 04_multi_agent_workflows.ipynb
│   ├── 05_production_patterns.ipynb
│   └── 06_troubleshooting_edge_cases.ipynb
├── examples/
│   ├── fastapi_middleware/
│   ├── multi_service_app/
│   ├── langgraph_agent/
│   └── production_monitoring/
└── docs/
    ├── best_practices.md
    └── common_patterns.md
```

## 🚀 Getting Started

1. **Environment Setup**: Start with `setup/environment_setup.ipynb` to configure your LangSmith environment and understand basic concepts.

2. **Choose Your Pattern**: Based on your architecture, select the most relevant notebook:
   - **Simple distributed apps**: `01_basic_cross_service_tracing.ipynb`
   - **OpenTelemetry integration**: `02_opentelemetry_integration.ipynb`
   - **Async/streaming systems**: `03_async_streaming_patterns.ipynb`
   - **Multi-agent workflows**: `04_multi_agent_workflows.ipynb`
   - **Production systems**: `05_production_patterns.ipynb`
   - **Debugging issues**: `06_troubleshooting_edge_cases.ipynb`

3. **Implementation**: Each notebook contains:
   - **Problem description** and use case scenarios
   - **Complete working code** with step-by-step explanations
   - **Multiple examples** covering different variations
   - **Best practices** and common gotchas
   - **Performance considerations** and optimization tips
   - **Links to production examples** and further reading

## 🔧 Prerequisites

- Python 3.8+
- LangSmith API key
- Basic understanding of distributed systems concepts
- Familiarity with LangChain/LangGraph (for relevant patterns)

## 🧠 Key Concepts

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
| Basic Cross-Service | Microservices, web APIs, simple distributed systems | Complex multi-agent workflows |
| OpenTelemetry | Polyglot systems, existing OTel infrastructure | LangSmith-only simple applications |
| Async & Streaming | Real-time apps, streaming responses, concurrent processing | Simple synchronous workflows |
| Multi-Agent Workflows | LangGraph applications, complex agent systems | Basic LLM API calls |
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

## 🏷️ Tags

`langsmith` `distributed-tracing` `observability` `llm-ops` `microservices` `opentelemetry` `langgraph` `production`

---

*This repository is maintained by the LangChain team. For support questions, please refer to the [LangSmith documentation](https://docs.smith.langchain.com) or open an issue.*
