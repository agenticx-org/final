from typing import Union, List
import uvicorn
import threading
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from researchinc.presentation.websocket.rest.websocket_controller import websocket_router

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173,http://localhost:8000,http://localhost"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include the WebSocket router
app.include_router(websocket_router)

# This block allows the application to be run directly with Python
# or with Gunicorn using: gunicorn trusstai.main:app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)