"""
Run script for the Litigation Simulator API.

This script starts the FastAPI application with Uvicorn server.
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get host and port from environment variables
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

if __name__ == "__main__":
    print(f"Starting Litigation Simulator API on {HOST}:{PORT}")
    uvicorn.run(
        "api-endpoints:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    ) 