import importlib
import json
import sys
import time
from typing import Any, Dict
from typing import Callable, Dict, Any, List
import uuid
from researchinc.utils.logging_config import setup_logging
from researchinc.service.code_executor import CodeExecutor
from researchinc.service.llm import LLM
from researchinc.service.prompts import get_system_prompt
from researchinc.service.project_manager import ProjectManager
from researchinc.service.tools import ToolManager
import os

logger = setup_logging()

MODEL_ID = os.getenv("MODEL_ID", "claude-3-7-sonnet-latest")

class AgentService:
    def __init__(self, callback: Callable[[Dict[str, Any]], None] = None):
        self.task = None
        self.authorized_imports = []
        self.callback = callback

    async def initialize(self,task:str, project_id:str):
        self.project_manager = ProjectManager(initial_task=task, system_prompt="Initializing...", 
            project_id=project_id, callback=self.callback)
        await self.project_manager.log(message="Initializing Agent")

        # Initialize components
        try:
            self.llm = LLM(model_id=MODEL_ID)
        except ValueError as e:
            await self.project_manager.log(message=f"Failed to initialize LLM: {e}", type="error", status="error")
            return
        
        self.project_manager.add_message("user", task)

        # Init CodeExecutor with empty dict first
        self.code_executor = CodeExecutor(initial_globals={})

        # Init ToolManager, which needs state and code executor
        self.tool_manager = ToolManager(
            project_manager=self.project_manager,
            code_executor=self.code_executor,
            allowed_imports=self.authorized_imports,
        )

        # Generate the real system prompt
        tool_definitions = self.tool_manager.get_tool_definitions()
        system_prompt = get_system_prompt(tool_definitions, self.authorized_imports)
        self.project_manager.system_prompt = system_prompt  # Update state

        # Prepare and set initial globals for code execution
        initial_globals = self._prepare_initial_globals()
        self.project_manager.set_initial_globals(initial_globals)  # Set in state
        self.code_executor.globals_locals = initial_globals  # Update executor directly

        await self.project_manager.log(message="Agent initialized successfully.", type="info", status="ready")
        await self.project_manager.log(message=self.project_manager.get_plan(), type="plan", status="ready")

    def _prepare_initial_globals(self) -> Dict[str, Any]:
        """Prepares the initial global scope for the CodeExecutor."""
        initial_globals = {}
        # Import allowed modules
        for import_name in self.authorized_imports:
            try:
                module = importlib.import_module(import_name)
                initial_globals[import_name] = module
                logger.info(f"Made module '{import_name}' available to code execution.")
            except ImportError:
                logger.warning(
                    f"Could not import module '{import_name}' for code execution."
                )

        # Add callable *custom* tools
        callable_tools = self.tool_manager.get_callable_tools_for_eval()
        initial_globals.update(callable_tools)
        logger.info(
            f"Made tools {list(callable_tools.keys())} available to code execution."
        )

        return initial_globals

    async def handle_command(self, event: Dict[str, Any]):
        try:
            if event.get("type") == "request":
              await self.start_agent_loop(event)
        except Exception as e:
            await self.project_manager.log(message="Error received from agent: " + str(e), type="error")
    
    async def start_agent_loop(self, command: Dict[str, Any]):
        task = command.get("content",None)
        project_id = command.get("project_id",None)
        await self.initialize(task, project_id)
        await self.run()

    async def run(self, max_iterations=20):
        await self.project_manager.log(message="Agent starting run loop...")
        iterations = 0

        while not self.project_manager.check_done() and iterations < max_iterations:
            iterations += 1
            await self.project_manager.log(message="Iteration start: " + str(iterations))

            # 1. Get state for LLM
            messages = self.project_manager.get_history()
            system_prompt = self.project_manager.get_system_prompt()
            tool_definitions = self.tool_manager.get_tool_definitions()

            # 2. Call LLM (Streaming)
            await self.project_manager.log(message="Calling LLM")
            llm_call_id = None
            final_message = None
            stream_generator = self.llm.generate_response_stream(
                messages, system_prompt, tool_definitions
            )

            # Consume the stream and output chunks
            try:
                while True:
                    chunk = next(stream_generator)
                    await self.project_manager.log(message=chunk["content"], type=chunk["type"])

                    if chunk["type"] == "error":
                        await self.project_manager.log_error(message=chunk["content"])
                    # Keep track of the ID from the first chunk
                    if llm_call_id is None and "id" in chunk:
                        llm_call_id = chunk["id"]

            except StopIteration as e:
                # The generator is exhausted, capture the return value
                # The return value is a tuple (llm_call_id, final_message_object)
                if e.value:
                    llm_call_id_from_return, final_message = e.value
                    # Ensure we have the ID, either from chunks or return value
                    if llm_call_id is None:
                        llm_call_id = llm_call_id_from_return
                else:
                    # Handle case where StopIteration has no value (e.g., an error occurred before yielding anything)
                    # If llm_call_id wasn't set from an error chunk, generate one for consistency? Or rely on logger?
                    # For now, assume an error chunk was yielded if e.value is None
                    if llm_call_id is None:
                        llm_call_id = "error-no-id"  # Fallback ID
                    final_message = None  # Ensure final_message is None on stream error

            # Add LLM call ID to status message for clarity
            await self.project_manager.log(message="LLM stream finished.", type="message", status="complete")

            # Check if the stream failed or returned empty content
            if final_message is None or final_message.content is None:
                await self.project_manager.log(message="LLM stream failed or returned empty content. Terminating.", type="error", status="error")
                break

            # Add assistant's *complete* response message to history before processing
            # Important: Use final_message here, which is the complete Anthropic message object
            self.project_manager.add_assistant_message(final_message.content)

            # 3. Process LLM response blocks from the final message
            executed_tool_this_turn = False
            for block in final_message.content:
                if block.type == "tool_use":
                    tool_name = block.name
                    tool_input = block.input
                    tool_use_id = block.id  # Keep the tool_use_id from Anthropic
                    executed_tool_this_turn = True

                    await self.project_manager.log(message=f"Executing tool: {tool_name} with args: {tool_input}", type="tool_call", status="inprogress")
                    if tool_name == "execute_python":
                        await self.project_manager.log(message=tool_input.get("code", ""), type="code_execution", status="inprogress")

                    # Execute the tool
                    result = await self.tool_manager.execute_tool(tool_name, tool_input)

                    # Determine if result indicates an error
                    is_error = False
                    result_content_for_llm = result
                    if isinstance(result, str) and result.lower().startswith("error:"):
                        is_error = True
                    # Check dict format from execute_python_impl
                    if isinstance(result, dict) and result.get("error"):
                        is_error = True
                        result_content_for_llm = f"Error during execution: {result['error']}"  # Pass error string to LLM

                    # Format tool result as JSON, including LLM call ID
                    result_output = {
                        "id": llm_call_id,  # Add ID
                        "type": "tool_result",
                        "tool": tool_name,
                        "success": not is_error,
                    }

                    # Format the result content based on its type
                    if isinstance(result, dict):
                        if "stdout" in result:
                            result_output["stdout"] = result.get("stdout")
                        if "error" in result:
                            result_output["error"] = result.get("error")
                    else:
                        result_output["content"] = str(result)

                    await self.project_manager.log(message=result_output, type="tool_result", status="complete")

                    # Add tool result message to state for the *next* LLM call
                    # Use the original tool_use_id provided by Anthropic
                    self.project_manager.add_tool_result(
                        tool_use_id=tool_use_id,
                        result=result_content_for_llm,  # Send stringified/error detail to LLM
                        is_error=is_error,
                    )

            if (
                not executed_tool_this_turn
                and final_message.stop_reason == "stop_sequence"  # Use final_message
            ):
                await self.project_manager.log(message="LLM finished turn without using a tool. Task may be stalled.", type="warning", status="inprogress")

            await self.project_manager.log(message="Iteration finished: " + str(iterations))

        # Loop finished
        # Add ID 'final' to these terminal messages
        await self.project_manager.log(message="Execution complete", type="info", status="complete")
        if self.project_manager.check_done():
            final_answer = self.project_manager.get_final_answer()
            await self.project_manager.log(message=final_answer, type="findings", status="complete")
        elif iterations >= max_iterations:
            await self.project_manager.log(message="Task exceeded maximum iterations.", type="message", status="incomplete")
        else:
            await self.project_manager.log(message="Agent loop exited unexpectedly.", type="message", status="error")

        return self.project_manager.get_final_answer()
