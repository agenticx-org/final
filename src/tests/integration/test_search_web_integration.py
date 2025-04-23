from datetime import timedelta
import datetime
import uuid
from researchinc.service.agent import AgentService
from typing import Any, Dict
import pytest

@pytest.mark.asyncio
async def test_search_web_integration():

    event_history = []
    async def callback(event: Dict[str, Any]):
        print(f"Event: {event}")
        event_history.append(event)
    agent = AgentService(callback)
    await agent.start_agent_loop(command={"type":"request","project_id":"123","content":"Open my google chrome browser and search for 'researchinc' and click on the first result."})