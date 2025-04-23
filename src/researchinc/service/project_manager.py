import json
from researchinc.utils.logging_config import setup_logging
from typing import Any, Callable, Dict, List, Optional
from researchinc.repositories.project_repository import ProjectRepository
import uuid
logger = setup_logging()

# Templates
PLAN_TEMPLATE = """
# Research Agent Progress Tracking

## Completed Milestones
- [ ] Initial Task Analysis

## Current Research Focus
### Step 1
- [ ] Define initial approach

*(Agent will update this structure)*
"""

FINDINGS_TEMPLATE = """
# Research Findings

## Summary
*(Agent should summarize key findings here)*

## Details
*(Agent should list detailed results, observations, or data points)*

## Confidence Score
*(Agent should assess confidence, e.g., High/Medium/Low)*
"""

class ProjectManager:
    """Manages the agent's state: history, plan, findings, execution scope."""

    def __init__(self, initial_task: str, system_prompt: str, project_id: str, callback: Callable[[Dict[str, Any]], None]):
        self.callback = callback
        self.project_id = project_id
        self.project_repository = ProjectRepository()
        self.project = self.project_repository.get_or_create(project_id)
        self.message_history = [{"role":"user","content":initial_task}]
        self.project.system_prompt = system_prompt
        self.project.plan = PLAN_TEMPLATE
        self.project.findings = FINDINGS_TEMPLATE
        self.execution_globals: Dict[str, Any] = {}
        self._is_done: bool = False
        self.project.final_answer = None

    async def save(self):
        self.project_repository.put(self.project)

    async def log(self, message: str = "", type: str = "info",  status: str = "inprogress"):
        # Convert dictionary messages to JSON strings
        if isinstance(message, dict):
            message = json.dumps(message)
        logger.info(message)

    def add_message(self, role: str, content: Any):
        """Adds a message (or list of content blocks) to the history."""
        if not content:
            logger.warning(f"Attempted to add empty message for role {role}")
            return
        # Ensure content is list for assistant, handle tool results correctly
        if role == "assistant":
            if not isinstance(content, list):
                content = [{"type": "text", "text": str(content)}]
        elif role == "user":
            # Handle tool result additions specifically via add_tool_result
            if (
                isinstance(content, list)
                and content
                and content[0].get("type") == "tool_result"
            ):
                # Already formatted correctly
                pass
            elif not isinstance(content, list):
                content = [{"type": "text", "text": str(content)}]  # Simple user text

        self.message_history.append({"role": role, "content": content})

    def add_assistant_message(self, content_blocks: List[Dict[str, Any]]):
        """Adds the assistant's response (potentially multiple blocks) to history."""
        if content_blocks:
            self.add_message(role="assistant", content=content_blocks)

    def add_tool_result(self, tool_use_id: str, result: Any, is_error: bool = False):
        """Adds a tool result message linked to a tool_use request."""
        content_block = {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "is_error": is_error,
        }
        # Content must be string or list of blocks (e.g. text block) for Anthropic
        if isinstance(result, (dict, list)):
            # Convert complex results to string (JSON) for the LLM
            content_block["content"] = json.dumps(result, indent=2)
        else:
            content_block["content"] = str(result)

        # Add as a user message containing the single tool result block
        self.add_message(role="user", content=[content_block])

    def get_history(self) -> List[Dict[str, Any]]:
        return self.message_history

    def get_system_prompt(self) -> str:
        return self.system_prompt

    async def update_plan(self, plan_markdown: str):
        self.project.plan = plan_markdown
        await self.callback({
            "type": "plan",
            "content": plan_markdown,
            "content_type":"md"
        })

    def get_plan(self) -> str:
        return self.project.plan

    async def update_findings(self, findings_markdown: str):
        self.project.findings = findings_markdown
        await self.callback({
            "type": "findings",
            "content": findings_markdown,
            "content_type":"md"
        })

    def get_findings(self) -> str:
        return self.project.findings

    def update_globals(self, new_globals: Dict[str, Any]):
        self.execution_globals.update(new_globals)

    def get_globals(self) -> Dict[str, Any]:
        return self.execution_globals

    def set_initial_globals(self, initial_globals: Dict[str, Any]):
        self.execution_globals = initial_globals
        logger.info("Initial execution globals set.")

    async def set_done(self, final_answer: Any):
        self._is_done = True
        self.final_answer = final_answer
        await self.callback({
            "type": "done",
            "content": final_answer,
            "content_type":"text"
        })
        logger.info(f"Agent marked as done. Final Answer: {final_answer}")

    def check_done(self) -> bool:
        return self._is_done

    def get_final_answer(self) -> Optional[Any]:
        return self.project.final_answer
    

    async def log_error(self, message: str):
        await self.callback({
            "type": "error",
            "content": message,
            "content_type":"text"
        })

