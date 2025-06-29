#!/usr/bin/env python3
"""Start the Supervisor Agent FastAPI server."""

import uvicorn
from multiagent_tracing.supervisor.server import app

if __name__ == "__main__":
    print("Starting Supervisor Agent server on http://127.0.0.1:8000")
    print("Make sure research agent (port 2025) and writing agent (port 2026) are running!")
    uvicorn.run(app, host="127.0.0.1", port=8000) 