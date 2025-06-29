# Cross-Platform Dual Tracing Pattern

**⚠️ IMPORTANT LIMITATION**: As of LangSmith SDK 0.4.4, the replica functionality for distributed tracing has limitations. When using distributed tracing with `parent=headers`, traces will only appear in the parent's project, not in both the parent's and child's projects as intended. This is a known SDK limitation being addressed by the LangSmith team.

This example demonstrates the intended pattern for distributed tracing across multi-agent systems where:
- Sub-agents are deployed on different platforms (FastAPI, AWS Lambda, etc.)
- Each team needs visibility into their own traces
- The platform team needs visibility into the complete workflow

## 🎯 The Challenge

When a supervisor agent (deployed on LangGraph Platform) orchestrates sub-agents (deployed elsewhere), organizations face a dual challenge:

1. **Cross-platform tracing**: Sub-agents deployed on external services don't automatically appear in LangSmith traces
2. **Multi-project visibility**: Teams need both:
   - **Supervisor visibility**: Complete traces showing the entire workflow
   - **Sub-agent team visibility**: Only their portions in separate projects for focused debugging

## 🔧 The Solution

Using LangSmith SDK 0.4.4+, we can achieve this with distributed tracing and replicas:

### 1. Supervisor Propagates Trace Context

```python
# In supervisor agent
from langsmith.run_helpers import get_current_run_tree

def call_sub_agent(state):
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
    
    response = requests.post(
        "http://sub-agent-url/invoke",
        json={"input": state},
        headers=headers  # Propagate trace context
    )
```

### 2. Sub-Agents Use Distributed Tracing with Replicas

```python
# In sub-agent server
from langsmith.run_helpers import tracing_context

@app.post("/invoke")
async def invoke(request: Request):
    # Extract trace headers
    parent_headers = {}
    if langsmith_trace := request.headers.get("langsmith-trace"):
        parent_headers["langsmith-trace"] = langsmith_trace
    if baggage := request.headers.get("baggage"):
        parent_headers["baggage"] = baggage
    
    # Trace to BOTH projects
    with tracing_context(
        parent=parent_headers,
        project_name="sub-agent-project",     # Sub-agent's own project
        replicas=[
            ("supervisor-project", None)      # Also trace to supervisor's project
        ]
    ):
        # Execute sub-agent logic
        result = await process_request(...)
```

## 📊 Result

- **Supervisor Project**: Shows complete trace with all sub-agent activity nested under the main trace
- **Sub-Agent Projects**: Show only their specific traces, allowing teams to focus on their components

## 🚀 Running the Example

### Prerequisites

1. **Set up environment**:
   ```bash
   export LANGSMITH_API_KEY=your_api_key
   export LANGSMITH_TRACING=true
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demo

#### Option 1: Using the Run Scripts (Recommended)

```bash
# On macOS/Linux
./multiagent_tracing/run_demo.sh

# On Windows or any platform
python multiagent_tracing/run_demo.py
```

#### Option 2: Manual Setup

1. **Start the sub-agents** (in separate terminals):
   ```bash
   # Terminal 1: Research Agent
   python multiagent_tracing/research_sub_agent/start_server.py
   
   # Terminal 2: Writing Agent
   python multiagent_tracing/writing_sub_agent/start_server.py
   ```

2. **Start the supervisor with LangGraph dev**:
   ```bash
   # Terminal 3: Supervisor (using LangGraph dev server)
   cd multiagent_tracing/supervisor
   langgraph dev --port 8123
   ```

3. **Run the test**:
   ```bash
   # Terminal 4: Make a test request
   python multiagent_tracing/test_distributed_tracing.py
   ```

### Check Results

After running the demo, check your LangSmith dashboard:
- Navigate to the `supervisor-distributed-traces` project to see complete traces
- Navigate to `research-distributed-traces` or `writing-distributed-traces` to see sub-agent specific traces

## 🏗️ Architecture

```
┌─────────────────────────┐
│   Supervisor Agent      │ (LangGraph Platform)
│ Project: supervisor-... │
└───────┬─────────────────┘
        │ Propagates headers
        ├─────────────────┬─────────────────┐
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Research Agent│ │ Writing Agent │ │  Other Agent  │
│ (FastAPI)     │ │ (FastAPI)     │ │ (AWS Lambda)  │
└───────────────┘ └───────────────┘ └───────────────┘
        │                 │                 │
        │ Traces to both projects via replicas
        ▼                 ▼                 ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│Research Project│ │Writing Project│ │ Other Project │
└───────────────┘ └───────────────┘ └───────────────┘
```

## 🔑 Key Benefits

1. **Team Autonomy**: Each team monitors their own agents in their own projects
2. **Platform Visibility**: Platform team sees complete workflow for debugging
3. **Cost Attribution**: Trace costs can be attributed to appropriate teams
4. **Security**: Teams only see traces relevant to their components

## 📝 Notes

- The supervisor uses `langgraph dev` to simulate LangGraph Platform deployment
- Sub-agents use FastAPI to simulate external deployments
- The `simple_demo.py` provides a self-contained example without requiring langgraph dev

## 🔍 Troubleshooting

### Verifying Replica Functionality

If you want to verify that the replica functionality is working:

```bash
python multiagent_tracing/verify_replicas.py
```

This will create test traces in `test-main-project` and `test-sub-project` to confirm replicas are functioning.

### Common Issues

1. **No traces in sub-agent projects**: 
   - Ensure you're using `langsmith>=0.4.4`
   - Check that `LANGSMITH_TRACING=true` is set
   - Verify the sub-agents are receiving trace headers from supervisor

2. **Traces only appear in supervisor project**:
   - Make sure sub-agents set their own `project_name` in `tracing_context`
   - Confirm the `replicas` list includes the supervisor project

3. **Connection errors**:
   - Ensure all services are running (supervisor on 8123, research on 2025, writing on 2024)
   - Check that `langgraph dev` started successfully

## 🚧 Known Limitations

1. **Replica functionality in distributed tracing**: 
   - When using `tracing_context(parent=headers)`, the SDK currently only sends traces to the parent's project
   - The `replicas` parameter doesn't work as expected in distributed tracing scenarios
   - This is a known SDK limitation as of version 0.4.4