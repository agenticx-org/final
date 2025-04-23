from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, AsyncGenerator
import json
import asyncio
import random
import re
from researchinc.service.agent import AgentService
from researchinc.utils.logging_config import setup_logging

logger = setup_logging()

websocket_router = APIRouter()

@websocket_router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Establish a WebSocket connection with a client
    """
    await websocket.accept()

    async def send_message(message):
        await websocket.send_text(json.dumps(message))

    agent = AgentService(callback=send_message)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message: {data}")
            json_data = json.loads(data)
            if json_data.get("type",None) == "request":
                await agent.start_agent_loop(command=json_data)
    except Exception as e:
        logger.error(f"Error: {e}")
