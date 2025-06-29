import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"

from multiagent_tracing.supervisor.supervisor import graph

app = FastAPI(title="Supervisor Agent API", description="Coordinates research and writing sub-agents")

class Message(BaseModel):
    role: str
    content: str

class InvokeRequest(BaseModel):
    assistant_id: str = "supervisor"
    input: Dict[str, List[Message]]

class InvokeResponse(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/invoke", response_model=InvokeResponse)
async def invoke_supervisor(request: InvokeRequest):
    """Invoke the supervisor agent graph."""
    try:
        from langchain_core.messages import HumanMessage, AIMessage
        
        # Convert the input messages to LangChain message objects
        messages = []
        for msg in request.input["messages"]:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            else:
                messages.append(AIMessage(content=msg.content))
        
        # Invoke the supervisor graph
        result = await graph.ainvoke({"messages": messages})
        
        # Format the response - convert LangChain messages back to dicts
        response_messages = []
        for msg in result["messages"]:
            if hasattr(msg, 'content') and hasattr(msg, 'type'):
                # This is a LangChain message object
                role = "user" if msg.type == "human" else "assistant"
                response_messages.append({
                    "role": role,
                    "content": msg.content
                })
            elif isinstance(msg, dict):
                response_messages.append({
                    "role": msg.get("role", "assistant"),
                    "content": msg.get("content", "")
                })
            else:
                # Fallback for unknown message types
                response_messages.append({
                    "role": "assistant",
                    "content": str(msg) if msg else ""
                })
        
        return InvokeResponse(messages=response_messages)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "agent": "supervisor",
        "sub_agents": {
            "research_agent": "http://127.0.0.1:2025",
            "writer_agent": "http://127.0.0.1:2024"
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Supervisor Agent API",
        "description": "Coordinates research and writing sub-agents",
        "endpoints": {
            "invoke": "POST /invoke - Main endpoint to interact with the supervisor",
            "health": "GET /health - Health check and sub-agent status"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000) 