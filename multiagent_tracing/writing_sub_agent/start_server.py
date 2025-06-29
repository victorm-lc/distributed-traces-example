#!/usr/bin/env python3
"""Start the Writing Sub-Agent FastAPI server."""

import uvicorn
from multiagent_tracing.writing_sub_agent.server import app

if __name__ == "__main__":
    print("Starting Writing Sub-Agent server on http://127.0.0.1:2024")
    uvicorn.run(app, host="127.0.0.1", port=2024) 