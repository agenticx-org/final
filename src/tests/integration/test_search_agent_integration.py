from datetime import timedelta
import datetime
import uuid
from researchinc.service.agent import AgentService
from typing import Any, Dict
import pytest

@pytest.mark.asyncio
async def test_search_agent_integration():
    event_history = []
    async def callback(event: Dict[str, Any]):
        print(f"Event: {event}")
        event_history.append(event)
    agent = AgentService(callback)
    await agent.start_agent_loop(command={"type":"request","project_id":"123","content":"Write me a report in markdown showing the top 5 and bottom five selling cars in the world."})