"""ReAct Agent Core Implementation"""
import json
from enum import Enum, auto
from typing import Optional, Dict, Any, List

from .. import OpenAIClient
from ..session.session import Session
from ..clients.base import BaseClient
from ..tools.registry import ToolRegistry
from ..tools.base import Tool
from ..tools.builtin import ReadTool, WriteTool, EditTool, ListDirTool, RunPythonFileTool, RunNodeFileTool
from ..tools.extensions import SkillTool
from ..models import GenerateResponse, TokenUsage
from .prompt_builder import build_system_prompt
from .pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage
)

# Optional: Anthropic is an optional dependency. ReAct loop should still work with OpenAI-only installs.
try:
    from ..clients.anthropic_client import AnthropicClient  # type: ignore
except Exception:  # pragma: no cover
    AnthropicClient = None  # type: ignore

class AgentMessageType(Enum):
    SYSTEM=auto()
    USER=auto()
    ASSISTANT=auto()
    ASSISTANT_WITH_TOOL_CALL=auto()
    TOOL_RESPONSE=auto()
    ERROR_TOOL_RESPONSE=auto()
    TOKEN=auto()
    MAXIMUM=auto()


class ReActAgent:
    """ReAct Agent - Reasoning and Acting Loop"""
    
    def __init__(
        self,
        client: BaseClient,
        working_dir: Optional[str],
        allowed_paths: Optional[List[str]] = None,
        blocked_paths: Optional[List[str]] = None,
        session_id: Optional[str] = None,
        system_prompt:Optional[str] = None,
        vision_client: Optional[BaseClient] = None
    ):
        """
        Initialize ReAct Agent
        
        :param client: LLM client instance
        :param working_dir: Default working directory (optional)
        :param allowed_paths: List of allowed paths
        :param blocked_paths: List of blocked paths
        :param session_id: Session ID (optional, auto-generated UUID if not provided)
        :param system_prompt: Custom system prompt (optional)
        :param vision_client: Optional separate client for vision tools (if not provided, uses client)
        """
        self.client = client
        self._session = Session(
                working_dir=working_dir,
                client=client,
                allowed_paths=allowed_paths,
                blocked_paths=blocked_paths,
                session_id=session_id,
                vision_client=vision_client
            )

        # Tool registry
        self._tool_registry = ToolRegistry()
        self._register_default_tools()

        # Default system prompt
        self.system_prompt = system_prompt if system_prompt else build_system_prompt(
            session=self.session,
            tools=self._tool_registry.get_all()
        )

    @property
    def session(self) -> Session:
        """Get Session instance (raises error if not initialized)"""
        if self._session is None:
            raise ValueError("Session not initialized. Please provide working_dir or call run() with working_dir.")
        return self._session
    
    def _register_default_tools(self) -> None:
        """Register default tools"""
        tools = [
            ReadTool(self.session),
            WriteTool(self.session),
            EditTool(self.session),
            ListDirTool(self.session),
            RunPythonFileTool(self.session),
            RunNodeFileTool(self.session),
            SkillTool(self.session),
        ]
        for tool in tools:
            self._tool_registry.register(tool)
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool
        
        :param tool: Tool instance
        """
        if self._session is None:
            raise ValueError("Session not initialized. Cannot register tools without a session.")
        self._tool_registry.register(tool)
    
    def unregister_tool(self, name: str) -> None:
        """
        Unregister a tool
        
        :param name: Tool name
        """
        self._tool_registry.unregister(name)
    
    async def run(
        self,
        prompt: str,
        max_iterations=60,
        stream: bool = False
    ):
        """
        Execute ReAct loop, automatically iterating until no tool calls
        
        :param prompt: User prompt
        :param max_iterations: Maximum number of iterations (default: 60)
        :param stream: Whether to stream output (not supported yet, interface reserved)
        :return: Agent's final response (automatically exits when no tool calls)
        
        Note:
        - If LLM returns no tool call, automatically exit and return response
        - If LLM returns tool calls, execute tools and continue loop
        - Automatically loop until LLM returns non-tool-call response
        """
        # Add system prompt
        self.session.add_message("system", self.system_prompt)
        yield AgentMessageType.SYSTEM,self.system_prompt
        # print_system_prompt(self.system_prompt)
        
        # Add user message
        self.session.add_message("user", prompt)
        yield AgentMessageType.USER,prompt
        # print_user_message(prompt)
        
        # Initialize token usage tracking
        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        
        # ReAct loop: automatically iterate until no tool calls
        max_iterations = max_iterations  # Prevent infinite loop
        iteration = 0
        stop_flag=False

        while iteration < max_iterations and not stop_flag:
            iteration += 1

            # Get tool schemas
            tool_schemas = self._tool_registry.get_schemas()

            if isinstance(self.client, OpenAIClient):
                # Get message list (OpenAI format)
                messages = self.session.get_messages()
                try:
                    response = await self.client.client.chat.completions.create(
                        model=self.client.model,
                        messages=messages,
                        tools=tool_schemas,
                        tool_choice="auto"
                    )
                except Exception as e:
                    stop_flag = True
                    error_msg = f"API call failed: {str(e)}"
                    raise RuntimeError(error_msg) from e

                if response is None:
                    stop_flag = True
                    raise RuntimeError("API returned empty response")

                if isinstance(response, str):
                    stop_flag = True
                    raise RuntimeError(f"API returned unexpected string response (possibly error page): {response[:200]}...")

                # Extract token usage from response
                round_usage = None
                if hasattr(response, 'usage') and response.usage:
                    # Create TokenUsage for this round
                    round_usage = TokenUsage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens
                    )
                    # Accumulate to total usage
                    total_usage.prompt_tokens += response.usage.prompt_tokens
                    total_usage.completion_tokens += response.usage.completion_tokens
                    total_usage.total_tokens += response.usage.total_tokens
                
                message = response.choices[0].message
                tool_calls = message.tool_calls
                
                if tool_calls:
                    tool_calls_dict = []
                    for tool_call in tool_calls:
                        tool_calls_dict.append({
                            "id": tool_call.id,
                            "type": tool_call.type,
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        })
                    
                    assistant_content = message.content if message.content else ""
                    self.session.add_message(
                        role="assistant",
                        content=assistant_content,
                        tool_calls=tool_calls_dict
                    )
                    yield AgentMessageType.ASSISTANT_WITH_TOOL_CALL, assistant_content,tool_calls_dict,round_usage
                    
                    for tool_call in tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        tool_call_id = tool_call.id
                        
                        tool = self._tool_registry.get(function_name)
                        if tool:
                            tool_call_result = await tool.execute(**function_args)
                            result_content = json.dumps(tool_call_result, ensure_ascii=False)
                            self.session.add_message(
                                role="tool",
                                content=result_content,
                                tool_call_id=tool_call_id
                            )
                            yield AgentMessageType.TOOL_RESPONSE, tool_call_id, tool_call_result
                        else:
                            error_content = json.dumps(
                                {"error": f"Tool '{function_name}' not found"},
                                ensure_ascii=False
                            )
                            self.session.add_message(
                                role="tool",
                                content=error_content,
                                tool_call_id=tool_call_id
                            )
                            yield AgentMessageType.ERROR_TOOL_RESPONSE, tool_call_id, error_content
                    
                    continue
                else:
                    assistant_content = message.content if message.content else ""
                    self.session.add_message(
                        role="assistant",
                        content=assistant_content
                    )
                    stop_flag = True
                    yield AgentMessageType.ASSISTANT, assistant_content, round_usage, total_usage

            elif AnthropicClient is not None and isinstance(self.client, AnthropicClient):
                # Anthropic tool-use loop (Claude)
                # Build Anthropic tools schema from existing OpenAI-style tool schemas
                anthropic_tools: List[Dict[str, Any]] = []
                for schema in tool_schemas:
                    fn = schema.get("function") if isinstance(schema, dict) else None
                    if fn and isinstance(fn, dict):
                        anthropic_tools.append(
                            {
                                "name": fn.get("name"),
                                "description": fn.get("description", ""),
                                "input_schema": fn.get("parameters", {"type": "object", "properties": {}}),
                            }
                        )

                # We maintain an Anthropic-format message list for this run, independent of Session's OpenAI-format history.
                # Session is still updated for logging/debugging and for tool execution results.
                if iteration == 1:
                    anthropic_messages: List[Dict[str, Any]] = [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                    # Store on the instance for subsequent iterations of this run
                    self._anthropic_messages = anthropic_messages  # type: ignore[attr-defined]
                else:
                    anthropic_messages = getattr(self, "_anthropic_messages", [])  # type: ignore[attr-defined]

                try:
                    response = await self.client.client.messages.create(
                        model=self.client.model,
                        max_tokens=1024,
                        system=self.system_prompt,
                        tools=anthropic_tools,
                        messages=anthropic_messages,
                    )
                except Exception as e:
                    stop_flag = True
                    error_msg = f"API call failed: {str(e)}"
                    raise RuntimeError(error_msg) from e

                # Extract token usage
                round_usage = None
                if hasattr(response, "usage") and response.usage:
                    round_usage = TokenUsage(
                        prompt_tokens=getattr(response.usage, "input_tokens", 0),
                        completion_tokens=getattr(response.usage, "output_tokens", 0),
                        total_tokens=getattr(response.usage, "input_tokens", 0) + getattr(response.usage, "output_tokens", 0),
                    )
                    total_usage.prompt_tokens += round_usage.prompt_tokens
                    total_usage.completion_tokens += round_usage.completion_tokens
                    total_usage.total_tokens += round_usage.total_tokens

                stop_reason = getattr(response, "stop_reason", None)
                content_blocks = getattr(response, "content", []) or []

                # Helper to normalize block access across SDK versions (object-like vs dict-like)
                def _block_get(block: Any, key: str, default=None):
                    if isinstance(block, dict):
                        return block.get(key, default)
                    return getattr(block, key, default)

                if stop_reason == "tool_use":
                    # Build a readable assistant text (concatenate any text blocks)
                    assistant_text = ""
                    tool_calls_dict = []
                    for block in content_blocks:
                        if _block_get(block, "type") == "text":
                            assistant_text += _block_get(block, "text", "") or ""
                        elif _block_get(block, "type") == "tool_use":
                            tool_use_id = _block_get(block, "id")
                            tool_name = _block_get(block, "name")
                            tool_input = _block_get(block, "input", {}) or {}
                            tool_calls_dict.append(
                                {
                                    "id": tool_use_id,
                                    "type": "function",
                                    "function": {"name": tool_name, "arguments": json.dumps(tool_input, ensure_ascii=False)},
                                }
                            )

                    # Update session + yield tool-call message
                    self.session.add_message("assistant", assistant_text, tool_calls=tool_calls_dict)
                    yield AgentMessageType.ASSISTANT_WITH_TOOL_CALL, assistant_text, tool_calls_dict, round_usage

                    # Append assistant content blocks to Anthropic message history (as-is)
                    anthropic_messages.append({"role": "assistant", "content": content_blocks})

                    # Execute tool calls and build tool_result blocks
                    tool_results_blocks: List[Dict[str, Any]] = []
                    for tc in tool_calls_dict:
                        tool_call_id = tc["id"]
                        function_name = tc["function"]["name"]
                        function_args = json.loads(tc["function"]["arguments"])

                        tool = self._tool_registry.get(function_name)
                        if tool:
                            tool_call_result = await tool.execute(**function_args)
                            self.session.add_message(
                                role="tool",
                                content=json.dumps(tool_call_result, ensure_ascii=False),
                                tool_call_id=tool_call_id,
                            )
                            yield AgentMessageType.TOOL_RESPONSE, tool_call_id, tool_call_result

                            tool_results_blocks.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_call_id,
                                    "content": [{"type": "text", "text": json.dumps(tool_call_result, ensure_ascii=False)}],
                                }
                            )
                        else:
                            error_obj = {"error": f"Tool '{function_name}' not found"}
                            self.session.add_message(
                                role="tool",
                                content=json.dumps(error_obj, ensure_ascii=False),
                                tool_call_id=tool_call_id,
                            )
                            yield AgentMessageType.ERROR_TOOL_RESPONSE, tool_call_id, json.dumps(error_obj, ensure_ascii=False)
                            tool_results_blocks.append(
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_call_id,
                                    "content": [{"type": "text", "text": json.dumps(error_obj, ensure_ascii=False)}],
                                }
                            )

                    # Feed tool results back to Claude and continue loop
                    anthropic_messages.append({"role": "user", "content": tool_results_blocks})
                    self._anthropic_messages = anthropic_messages  # type: ignore[attr-defined]
                    continue

                # Default: no tool call, end turn / max_tokens / etc.
                assistant_text = ""
                for block in content_blocks:
                    if _block_get(block, "type") == "text":
                        assistant_text += _block_get(block, "text", "") or ""

                self.session.add_message("assistant", assistant_text)
                stop_flag = True
                yield AgentMessageType.ASSISTANT, assistant_text, round_usage, total_usage

            else:
                stop_flag = True
                raise NotImplementedError(f"Client type {type(self.client)} not yet supported in ReAct loop")

        if not stop_flag:
            yield AgentMessageType.MAXIMUM, "Reached maximum iterations. Please check the task.", total_usage

