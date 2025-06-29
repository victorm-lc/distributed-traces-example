import os
from pydantic import Field
from typing import Literal, Optional

# Enable LangSmith tracing for @traceable decorators
os.environ["LANGSMITH_TRACING"] = "true"

# Set custom tracing project for this agent
# This ensures traces go to dedicated project instead of .env default
os.environ["LANGSMITH_PROJECT"] = "supervisor-distributed-traces"

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from langgraph.graph import MessagesState, StateGraph, START
import requests
from langsmith.run_helpers import get_current_run_tree

# Configuration for sub-agent URLs
RESEARCH_AGENT_URL = os.getenv("RESEARCH_AGENT_URL", "http://127.0.0.1:2025")
WRITING_AGENT_URL = os.getenv("WRITING_AGENT_URL", "http://127.0.0.1:2024")

class SupervisorInputState(MessagesState):
    """Public input state that will be visible in LangGraph Studio."""
    # Only contains the messages field from MessagesState
    # No internal routing fields are exposed
    pass

class SupervisorState(MessagesState):
    """Internal state for the supervisor agent with private routing fields."""
    next_agent: Optional[Literal["research_agent", "writer_agent"]] = None
    is_satisfied: Optional[bool] = Field(
        description="Whether the research is complete to answer the user's question.",
        default=False
    ) 


# call the seperately research agent as a sub-agent via API
def call_research_agent(state: MessagesState):
    # Get trace headers to propagate context to sub-agent
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
        print(f"Supervisor sending headers to research agent: {headers}")
    else:
        print("Supervisor: No run tree available")
    
    response = requests.post(
        f"{RESEARCH_AGENT_URL}/invoke",
        json={
            "assistant_id": "research_agent",
            "input": {
                "messages": [{"role": "user", "content": state["messages"][-1].content}]
            }
        },
        headers=headers  # Pass trace headers
    )

    result = response.json()
    
    # Get the assistant's response from the research agent
    research_response = result["messages"][-1]["content"]
    
    return {
        "messages": state["messages"] + [{"role": "assistant", "content": research_response}],
        "next_agent": None,  # Clear the routing flag so we return to supervisor
        "is_satisfied": False  # Let supervisor decide if more work is needed
    }



# call the seperately writer agent as a sub-agent via API
def call_writer_agent(state: MessagesState):
    # Get trace headers to propagate context to sub-agent
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
        print(f"Supervisor sending headers to writer agent: {headers}")
    else:
        print("Supervisor: No run tree available")
    
    response = requests.post(
        f"{WRITING_AGENT_URL}/invoke",
        json={
            "assistant_id": "writer_agent",
            "input": {
                "messages": [{"role": "user", "content": state["messages"][-1].content}]
            }
        },
        headers=headers  # Pass trace headers
    )
    
    result = response.json()
    
    # Get the assistant's response from the writer agent
    writer_response = result["messages"][-1]["content"] 

    return {
        "messages": state["messages"] + [{"role": "assistant", "content": writer_response}],
        "next_agent": None,  # Clear the routing flag so we return to supervisor
        "is_satisfied": False  # Let supervisor decide if more work is needed
    }


# Define tools to transfer to the sub-agents
@tool
def transfer_to_research_agent():
    """Research the topic"""
    return "Transferring to research agent"


@tool
def transfer_to_writer_agent():
    """Write the report"""  
    return "Transferring to writer agent"


# create a prompt for the supervisor agent
supervisor_prompt = """You are a Supervisor Agent managing a team of specialized agents.

Your team:
- research_agent: Finds and gathers information using web search
- writing_agent: Creates formatted reports and documentation

WORKFLOW:
1. When you receive a new user question, decide if you need to gather information or format content
2. Use transfer_to_research_agent if you need to research or gather information
3. Use transfer_to_writer_agent if you need to format or write a report
4. IMPORTANT: After your subagents have provided their responses, DO NOT call any more tools - instead respond directly to the user with the information you now have

Look at the conversation history. If you can see that your subagents have already provided information to answer the user's question, respond directly without calling any tools."""



async def supervisor(state: SupervisorState):
    """Call the LLM powering our "agent".
    """
    model = ChatOpenAI(model="gpt-4o").bind_tools([
        transfer_to_research_agent, 
        transfer_to_writer_agent
    ])
    
    # Add the supervisor prompt to guide the LLM's decision making
    messages_with_prompt = [{"role": "system", "content": supervisor_prompt}] + state["messages"]
    
    # Debug: Print what the supervisor is seeing
    print(f"Supervisor sees {len(state['messages'])} messages in conversation")
    print(f"Last message type: {type(state['messages'][-1])}")
    print(f"Last message content preview: {state['messages'][-1].content[:100] if hasattr(state['messages'][-1], 'content') else 'No content'}...")
    
    response = await model.ainvoke(messages_with_prompt)

    print(f"Supervisor response has tool_calls: {bool(response.tool_calls)}")
    
    if response.tool_calls:
        print(response.tool_calls)
        tool_name = response.tool_calls[0]["name"]
        print(tool_name)
        if tool_name == "transfer_to_research_agent":
            return {"next_agent": "research_agent", "messages": state["messages"], "is_satisfied": False}
        elif tool_name == "transfer_to_writer_agent":
            return {"next_agent": "writer_agent", "messages": state["messages"], "is_satisfied": False}
    
    print(f"didn't call any tools, Supervisor response: {response}")
    return {"messages": state["messages"] + [response], "is_satisfied": True}


# create a conditional edge to route the supervisor's output to the next agent or end the workflow
async def route_supervisor_output(state: SupervisorState) -> Literal["research_agent", "writer_agent", "__end__"]:
    """Determine the next node based on the supervisor's output."""

    if state.get("is_satisfied"):
        return "__end__"
    elif state.get("next_agent") == "research_agent":
        return "research_agent"
    elif state.get("next_agent") == "writer_agent":
        return "writer_agent"
    else:
        # If next_agent is None or not set, end the workflow
        return "supervisor"

# Build the graph with input schema filtering
# The input parameter filters what fields are visible in LangGraph Studio
builder = StateGraph(SupervisorState, input=SupervisorInputState)
builder.add_node("supervisor", supervisor)
builder.add_conditional_edges("supervisor", route_supervisor_output)
builder.add_node("research_agent", call_research_agent)
builder.add_node("writer_agent", call_writer_agent)
builder.add_edge(START, "supervisor")
builder.add_edge("research_agent", "supervisor")
builder.add_edge("writer_agent", "supervisor")

graph = builder.compile()








