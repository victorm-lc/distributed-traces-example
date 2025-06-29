import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"

from multiagent_tracing.research_sub_agent.graph import graph

app = FastAPI(title="Research Sub-Agent API")

class Message(BaseModel):
    role: str
    content: str

class InvokeRequest(BaseModel):
    assistant_id: str
    input: Dict[str, List[Message]]

class InvokeResponse(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/invoke", response_model=InvokeResponse)
async def invoke_agent(request: InvokeRequest):
    """Invoke the research agent graph."""
    try:
        # Convert the input messages to the expected format
        messages = []
        for msg in request.input["messages"]:
            messages.append({"role": msg.role, "content": msg.content})
        
        # Invoke the graph
        result = await graph.ainvoke({"messages": messages})
        
        # Format the response
        response_messages = []
        for msg in result["messages"]:
            if hasattr(msg, 'content'):
                response_messages.append({
                    "role": "assistant" if hasattr(msg, 'tool_calls') else "user",
                    "content": msg.content
                })
            else:
                response_messages.append({
                    "role": msg.get("role", "assistant"),
                    "content": msg.get("content", "")
                })
        
        return InvokeResponse(messages=response_messages)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "research_agent"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=2025) 