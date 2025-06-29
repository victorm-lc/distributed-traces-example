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
from langchain_core.messages import HumanMessage, AIMessage

from langgraph.graph import MessagesState, StateGraph, START
import requests
from langsmith.run_helpers import get_current_run_tree

# Configuration for sub-agent URLs
RESEARCH_AGENT_URL = os.getenv("RESEARCH_AGENT_URL", "http://127.0.0.1:2025")
WRITING_AGENT_URL = os.getenv("WRITING_AGENT_URL", "http://127.0.0.1:2026")

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
def call_research_agent(state: SupervisorState):
    # Get trace headers to propagate context to sub-agent
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
        print(f"Supervisor sending headers to research agent: {headers}")
    else:
        print("Supervisor: No run tree available")
    
    # Get the last user message for the research agent
    last_message = state["messages"][-1]
    content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    response = requests.post(
        f"{RESEARCH_AGENT_URL}/invoke",
        json={
            "assistant_id": "research_agent",
            "input": {
                "messages": [{"role": "user", "content": content}]
            }
        },
        headers=headers  # Pass trace headers
    )

    result = response.json()
    
    # Get the assistant's response from the research agent
    research_response = result["messages"][-1]["content"]
    
    # Append the research agent's response to existing messages
    return {
        "messages": state["messages"] + [AIMessage(content=f"Research findings: {research_response}")],
        "next_agent": None,  # Clear the routing flag so we return to supervisor
        "is_satisfied": False  # Let supervisor decide if more work is needed
    }



# call the seperately writer agent as a sub-agent via API
def call_writer_agent(state: SupervisorState):
    # Get trace headers to propagate context to sub-agent
    headers = {}
    if run_tree := get_current_run_tree():
        headers.update(run_tree.to_headers())
        print(f"Supervisor sending headers to writer agent: {headers}")
    else:
        print("Supervisor: No run tree available")
    
    # Get the last message content for the writing agent
    # This could be either the user's original request or research results
    last_message = state["messages"][-1]
    content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    response = requests.post(
        f"{WRITING_AGENT_URL}/invoke",
        json={
            "assistant_id": "writer_agent",
            "input": {
                "messages": [{"role": "user", "content": content}]
            }
        },
        headers=headers  # Pass trace headers
    )
    
    result = response.json()
    
    # Get the assistant's response from the writer agent
    writer_response = result["messages"][-1]["content"] 

    # Append the writing agent's response to existing messages
    return {
        "messages": state["messages"] + [AIMessage(content=f"Final report: {writer_response}")],
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
4. After your subagents have provided their responses (marked with "Research findings:" or "Final report:" prefix), 
   synthesize their work and provide a final response to the user
5. DO NOT call any more tools after agents have completed their work - provide a final answer

Look at the conversation history. If you see messages prefixed with "Research findings:" or "Final report:", 
those are completed responses from your team. Synthesize them into a final answer."""



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
    print(f"\nSupervisor sees {len(state['messages'])} messages in conversation")
    if state["messages"]:
        last_msg = state["messages"][-1]
        print(f"Last message type: {type(last_msg)}")
        content = last_msg.content if hasattr(last_msg, 'content') else str(last_msg)
        print(f"Last message preview: {content[:200]}...")
    
    response = await model.ainvoke(messages_with_prompt)

    print(f"Supervisor response has tool_calls: {bool(response.tool_calls)}")
    
    if response.tool_calls:
        tool_name = response.tool_calls[0]["name"]
        print(f"Supervisor calling tool: {tool_name}")
        if tool_name == "transfer_to_research_agent":
            return {"next_agent": "research_agent", "is_satisfied": False}
        elif tool_name == "transfer_to_writer_agent":
            return {"next_agent": "writer_agent", "is_satisfied": False}
    
    # No tool calls means supervisor is providing final answer
    print(f"Supervisor providing final response")
    return {"messages": state["messages"] + [response], "is_satisfied": True}


# create a conditional edge to route the supervisor's output to the next agent or end the workflow
def route_supervisor_output(state: SupervisorState) -> Literal["research_agent", "writer_agent", "__end__"]:
    """Determine the next node based on the supervisor's output."""
    
    print(f"\nRouting decision: is_satisfied={state.get('is_satisfied')}, next_agent={state.get('next_agent')}")
    
    if state.get("is_satisfied"):
        print("Ending workflow - supervisor is satisfied")
        return "__end__"
    elif state.get("next_agent") == "research_agent":
        print("Routing to research agent")
        return "research_agent"
    elif state.get("next_agent") == "writer_agent":
        print("Routing to writer agent")  
        return "writer_agent"
    else:
        # Default to end if no next agent and not explicitly continuing
        print("No next agent specified - ending workflow")
        return "__end__"

# Build the graph with input schema filtering
# The input parameter filters what fields are visible in LangGraph Studio
builder = StateGraph(SupervisorState, input=SupervisorInputState, output=SupervisorInputState)
builder.add_node("supervisor", supervisor)
builder.add_conditional_edges("supervisor", route_supervisor_output)
builder.add_node("research_agent", call_research_agent)
builder.add_node("writer_agent", call_writer_agent)
builder.add_edge(START, "supervisor")
builder.add_edge("research_agent", "supervisor")
builder.add_edge("writer_agent", "supervisor")

graph = builder.compile(
    checkpointer=None,  # No checkpointing for simplicity
    interrupt_before=[],  # No interrupts
    interrupt_after=[]
)








