"""ReAct Agent Core Implementation"""
import json
from enum import Enum, auto
from typing import Optional, Dict, Any, List

from .. import OpenAIClient
from ..session.session import Session
from ..clients.base import BaseClient
from ..tools.registry import ToolRegistry
from ..tools.base import Tool
from ..tools.builtin import ReadTool, WriteTool, EditTool, ListDirTool, RunPythonFileTool
from ..models import GenerateResponse, TokenUsage
from .prompt_builder import build_system_prompt
from .pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage
)

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
        system_prompt:Optional[str] = None
    ):
        """
        Initialize ReAct Agent
        
        :param client: LLM client instance
        :param working_dir: Default working directory (optional)
        :param allowed_paths: List of allowed paths
        :param blocked_paths: List of blocked paths
        :param session_id: Session ID (optional, auto-generated UUID if not provided)
        :param system_prompt: Custom system prompt (optional)
        """
        self.client = client
        self._session = Session(
                working_dir=working_dir,
                client=client,
                allowed_paths=allowed_paths,
                blocked_paths=blocked_paths,
                session_id=session_id
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
            RunPythonFileTool(self.session)
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
        max_iterations=20,
        stream: bool = False
    ):
        """
        Execute ReAct loop, automatically iterating until no tool calls
        
        :param prompt: User prompt
        :param max_iterations: Maximum number of iterations (default: 20)
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

            # Get message list
            messages = self.session.get_messages()

            # Get tool schemas
            tool_schemas = self._tool_registry.get_schemas()

            if isinstance(self.client, OpenAIClient):
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
            
            else:
                stop_flag = True
                raise NotImplementedError(f"Client type {type(self.client)} not yet supported in ReAct loop")

        if not stop_flag:
            yield AgentMessageType.MAXIMUM, "Reached maximum iterations. Please check the task.", total_usage

