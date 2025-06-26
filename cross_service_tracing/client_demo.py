import asyncio
import httpx
from typing import Dict, Any

# LangSmith and LangChain imports
from langsmith import traceable
from langsmith.run_helpers import get_current_run_tree
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage


# Initialize LLM with LangSmith tracing (automatically traced)
client_llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=150
)

@traceable(name="client-preprocess")
async def preprocess_user_input(user_input: str) -> str:
    """Preprocess user input using LLM before sending to server"""
    
    print(f"🧠 Client LLM: Preprocessing user input...")
    
    messages = [
        SystemMessage(content="You are a helpful assistant that prepares user queries for processing. Clean up the input, fix any grammar issues, and make it more specific if needed. Keep it concise."),
        HumanMessage(content=f"Please preprocess this user input: {user_input}")
    ]
    
    # This LLM call will be automatically traced by LangSmith
    response = await client_llm.ainvoke(messages)
    preprocessed_text = response.content
    
    print(f"✨ Client LLM result: {preprocessed_text}")
    return preprocessed_text

@traceable(name="client-analyze-response")
async def analyze_server_response(response_data: str) -> Dict[str, Any]:
    """Analyze server response using LLM"""
    
    print(f"🔍 Client LLM: Analyzing server response...")
    
    messages = [
        SystemMessage(content="You are an analyst that evaluates server responses. Provide a brief analysis including sentiment, key points, and a quality score (1-10)."),
        HumanMessage(content=f"Please analyze this server response: {response_data}")
    ]
    
    # Another LLM call that will be traced
    response = await client_llm.ainvoke(messages)
    analysis = response.content
    
    print(f"📊 Client analysis: {analysis}")
    
    # Extract a simple quality score for demo purposes
    try:
        # Simple extraction - in practice you'd use structured output
        score = 8  # Default score
        if "score" in analysis.lower():
            # Try to extract number after "score"
            import re
            score_match = re.search(r'score.*?(\d+)', analysis.lower())
            if score_match:
                score = int(score_match.group(1))
    except:
        score = 8
    
    return {
        "analysis": analysis,
        "quality_score": score
    }

@traceable(name="client-request")
async def make_client_request(data: str) -> Dict[str, Any]:
    """Client function that makes a request to our server with proper trace context"""
    
    # Get current trace context
    current_run = get_current_run_tree()
    print(f"📤 Client trace ID: {current_run.trace_id if current_run else 'None'}")
    
    # Prepare headers with trace context using the official LangSmith method
    headers = {"Content-Type": "application/json"}
    
    if current_run:
        # Use the official LangSmith method to generate trace headers
        # This is the key to making distributed tracing work!
        trace_headers = current_run.to_headers()
        headers.update(trace_headers)
        print(f"📤 Sending trace headers: {trace_headers}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/process",
                json={"data": data},
                headers=headers,
                timeout=30.0
            )
            result = response.json()
            print(f"📥 Server response: {result}")
            return result
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {"error": str(e)}

@traceable(name="client-workflow")
async def client_workflow(user_input: str = "I need help with understanding machine learning concepts"):
    """Main client workflow that demonstrates distributed tracing with LLM calls"""
    
    print("🔄 Starting client workflow with LLM calls...")
    
    # Step 1: Preprocess user input with client-side LLM
    preprocessed_data = await preprocess_user_input(user_input)
    
    # Step 2: Make server request (this will propagate trace context)
    server_result = await make_client_request(preprocessed_data)
    
    # Step 3: Analyze server response with client-side LLM
    if "error" not in server_result:
        analysis_result = await analyze_server_response(server_result['result'])
        
        final_result = {
            "original_input": user_input,
            "preprocessed_input": preprocessed_data,
            "server_result": server_result['result'],
            "analysis": analysis_result
        }
        
        print(f"✅ Workflow completed successfully!")
        print(f"🎯 Quality Score: {analysis_result['quality_score']}/10")
        return final_result
    else:
        print(f"❌ Workflow failed: {server_result['error']}")
        return server_result

@traceable(name="enhanced-workflow-with-context")
async def enhanced_workflow_with_context():
    """Enhanced workflow that shows proper context propagation with multiple LLM calls"""
    
    print("🚀 Starting enhanced workflow with multiple LLM calls...")
    
    # Different types of user inputs to process
    user_inputs = [
        "What are the benefits of distributed tracing?",
        "How do I optimize LLM performance?",
        "Explain async programming in Python"
    ]
    
    results = []
    for i, user_input in enumerate(user_inputs):
        print(f"\n📝 Processing request {i+1}: {user_input}")
        result = await client_workflow(user_input)
        results.append(result)
        await asyncio.sleep(0.1)  # Small delay between requests
    
    print(f"\n✅ Enhanced workflow completed with {len(results)} LLM-powered requests!")
    
    # Calculate average quality score across all requests
    quality_scores = [r.get('analysis', {}).get('quality_score', 0) for r in results if 'error' not in r]
    avg_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
    print(f"📊 Average quality score: {avg_score:.1f}/10")
    
    return {
        "results": results,
        "average_quality_score": avg_score,
        "total_requests": len(results)
    }

async def main():
    """Main function to run all demos"""
    
    print("🚀 Running LLM-Powered Distributed Tracing Demo")
    print("=" * 60)
    
    # Test 1: Basic workflow with LLM calls
    print("\n📋 Test 1: Basic Client-Server Workflow with LLM Processing")
    result1 = await client_workflow()
    
    # Test 2: Enhanced workflow with multiple LLM-powered requests
    print("\n📋 Test 2: Enhanced Workflow with Multiple LLM-Powered Requests")
    result2 = await enhanced_workflow_with_context()
    
    print("\n✅ All LLM-powered tests completed!")
    print("📊 Check your LangSmith dashboard to see the distributed traces with LLM calls!")
    print("🔗 Each trace should show:")
    print("   • Client LLM preprocessing → Server LLM processing → Client LLM analysis")
    print("   • Full token usage, latency, and cost tracking across services")
    print("   • Complete conversation flows with prompt/response visibility")

if __name__ == "__main__":
    asyncio.run(main())