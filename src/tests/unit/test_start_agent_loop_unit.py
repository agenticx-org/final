from researchinc.service.agent import AgentService
from typing import Any, Dict
import pytest

@pytest.mark.asyncio
async def test_start_agent_loop_unit():
    event_history = []
    async def callback(event: Dict[str, Any]):
        print(f"Event: {event}")
        event_history.append(event)
    agent = AgentService(callback)
    await agent.start_agent_loop(command={"type":"request","project_id":"123","content":"What is 2+2?"})
    assert len(event_history) > 1
    for event in event_history:
        assert event["type"] in ["plan","findings","done"]
        assert event["content_type"] in ["md","text"]
        assert len(event["content"]) > 0
    last = len(event_history)-1
    assert event_history[last]["type"] == "done"
    assert event_history[last]["content_type"] == "text"
    assert len(event_history[last]["content"]) > 0
    assert event_history[last]["content"] == "The sum of 2+2 is 4."