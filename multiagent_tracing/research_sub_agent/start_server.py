#!/usr/bin/env python3
"""Start the Research Sub-Agent FastAPI server."""

import uvicorn
from multiagent_tracing.research_sub_agent.server import app

if __name__ == "__main__":
    print("Starting Research Sub-Agent server on http://127.0.0.1:2025")
    uvicorn.run(app, host="127.0.0.1", port=2025) 