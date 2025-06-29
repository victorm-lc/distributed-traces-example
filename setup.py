"""Setup script for the distributed traces example project."""

from setuptools import setup, find_packages

setup(
    name="distributed-traces-example",
    version="0.1.0",
    description="Example project demonstrating distributed tracing with LangGraph",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "fastapi==0.115.14",
        "httpx==0.28.1",
        "langchain==0.3.26",
        "langchain-community==0.3.26",
        "langchain-openai==0.3.26",
        "langchain-tavily==0.2.4",
        "langgraph==0.5.0",
        "langgraph-cli==0.1.72",
        "langgraph-supervisor==0.0.27",
        "langsmith==0.4.4",
        "uvicorn==0.34.3",
    ],
) 