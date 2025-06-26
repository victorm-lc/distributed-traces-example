import os
from fastapi import FastAPI, Request
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from langsmith.middleware import TracingMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import uvicorn
from typing import Dict, Any
import asyncio

app = FastAPI()

# Add LangSmith's TracingMiddleware for automatic distributed tracing
app.add_middleware(TracingMiddleware)

# Initialize server LLM with LangSmith tracing (automatically traced)
server_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.3,  # Lower temperature for more consistent server responses
    max_tokens=200
)

@traceable(name="server-llm-research")
async def research_with_llm(query: str) -> str:
    """Use LLM to research and provide detailed information about the query"""
    
    print(f"🔬 Server LLM: Researching query...")
    
    messages = [
        SystemMessage(content="""You are a knowledgeable research assistant. When given a query, provide:
1. A clear, informative explanation 
2. Key concepts and definitions
3. Practical examples or use cases
4. Best practices or recommendations

Keep your response structured and helpful, around 150-200 words."""),
        HumanMessage(content=f"Please provide detailed information about: {query}")
    ]
    
    # This LLM call will be automatically traced by LangSmith
    response = await server_llm.ainvoke(messages)
    research_content = response.content
    
    print(f"📚 Server LLM research result: {research_content[:100]}...")
    return research_content

@traceable(name="server-llm-summarize")
async def summarize_with_llm(content: str) -> Dict[str, Any]:
    """Use LLM to create a summary and extract key insights"""
    
    print(f"📝 Server LLM: Creating summary and insights...")
    
    messages = [
        SystemMessage(content="""You are a content summarizer. Given detailed content, provide:
1. A 2-3 sentence summary
2. 3 key takeaways (as bullet points)
3. A single recommended action

Format your response clearly with sections."""),
        HumanMessage(content=f"Please summarize this content and provide key insights: {content}")
    ]
    
    # Another LLM call that will be traced
    response = await server_llm.ainvoke(messages)
    summary_content = response.content
    
    print(f"💡 Server LLM summary: {summary_content[:100]}...")
    
    # Parse the response into structured format (simplified for demo)
    lines = summary_content.split('\n')
    summary = summary_content  # In practice, you'd parse this more carefully
    
    return {
        "summary": summary,
        "processing_timestamp": asyncio.get_event_loop().time(),
        "word_count": len(content.split())
    }

@traceable(name="server-process")
async def process_data(data: str):
    """Process data on server side with LLM-powered research and summarization"""
    
    # This will automatically be part of the distributed trace
    current_run = get_current_run_tree()
    if current_run:
        print(f"🔗 Server processing within trace: {current_run.trace_id}")
    
    print(f"⚙️ Server: Processing incoming data: {data}")
    
    # Step 1: Research the topic using LLM
    research_result = await research_with_llm(data)
    
    # Step 2: Simulate some processing time
    await asyncio.sleep(0.1)
    
    # Step 3: Summarize and extract insights using LLM
    summary_result = await summarize_with_llm(research_result)
    
    # Step 4: Combine results
    final_result = {
        "query": data,
        "research": research_result,
        "summary": summary_result,
        "processing_notes": "Processed with dual LLM calls: research + summarization"
    }
    
    print(f"✅ Server: Processing completed successfully")
    return final_result

@traceable(name="server-health-check")
async def health_check_with_llm():
    """Health check that includes a simple LLM call to verify everything is working"""
    
    messages = [
        SystemMessage(content="You are a system health checker. Respond with a brief, positive status message about system readiness."),
        HumanMessage(content="Please confirm the system is ready to process requests.")
    ]
    
    try:
        response = await server_llm.ainvoke(messages)
        return {
            "status": "healthy", 
            "llm_status": "operational",
            "message": response.content
        }
    except Exception as e:
        return {
            "status": "degraded",
            "llm_status": "error", 
            "message": f"LLM health check failed: {str(e)}"
        }

@app.post("/process")
async def process_endpoint(request: Request, payload: dict):
    """Server endpoint that properly handles incoming trace context with LLM processing"""
    
    # Extract LangSmith headers for trace continuation
    headers = dict(request.headers)
    
    # Log the incoming headers (optional, for debugging)
    langsmith_headers = {k: v for k, v in headers.items() if k.startswith('langsmith') or k == 'baggage'}
    if langsmith_headers:
        print(f"📥 Received trace headers: {langsmith_headers}")
    else:
        print("⚠️ No trace headers received")
    
    # With TracingMiddleware, the trace context is automatically handled
    # The @traceable decorator on process_data will continue the trace
    result = await process_data(payload["data"])
    return {"result": result}

@app.get("/health")
async def health_check():
    """Enhanced health check that includes LLM verification"""
    health_result = await health_check_with_llm()
    return health_result

@app.get("/")
async def root():
    return {
        "service": "LLM-Powered Distributed Tracing Server",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "process": "/process (POST)",
            "root": "/ (GET)"
        },
        "features": [
            "Automatic distributed tracing with LangSmith",
            "LLM-powered research and summarization",
            "Structured response formatting",
            "Health checks with LLM verification"
        ]
    }

if __name__ == "__main__":
    # Ensure LangSmith is configured
    if not os.getenv("LANGSMITH_TRACING"):
        os.environ["LANGSMITH_TRACING"] = "true"
    
    print("🚀 Starting LLM-Powered Distributed Tracing Server")
    print("=" * 60)
    print("🌐 Server running on http://localhost:8000")
    print("🏥 Health check available at http://localhost:8000/health") 
    print("⚙️ Process endpoint available at http://localhost:8000/process")
    print("🧠 Features: LLM research, summarization, and distributed tracing")
    
    uvicorn.run(app, host="0.0.0.0", port=8000) 