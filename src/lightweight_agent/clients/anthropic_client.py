"""Anthropic Client Implementation"""
from types import SimpleNamespace
from typing import AsyncIterator, Optional, Union, List, Dict, Any, Tuple
from pathlib import Path
import json
from anthropic import AsyncAnthropic
from anthropic._exceptions import APIError as AnthropicAPIError, APIConnectionError

from .base import BaseClient
from ..exceptions import APIError, NetworkError, ValidationError
from ..utils import validate_prompt, create_anthropic_image_message
from ..models import GenerateResponse, StreamingResponse, TokenUsage


class AnthropicClient(BaseClient):
    """Anthropic async client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize Anthropic client
        
        :param api_key: API key, default read from environment variable
        :param base_url: API base URL, default read from environment variable
        :param model: Model name, default read from environment variable
        """
        
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        
        # Initialize Anthropic client
        client_kwargs = {'api_key': self.api_key,
                         'base_url':self.base_url,
                         'max_retries':3,
                         }

        self.client = AsyncAnthropic(**client_kwargs)

    @staticmethod
    def _convert_tools(tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
        """Convert OpenAI function tools to Anthropic tool definitions."""
        if tools is None:
            return None

        converted = []
        for tool in tools:
            function = tool.get("function", tool)
            converted.append({
                "name": function["name"],
                "description": function.get("description", ""),
                "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
            })
        return converted

    @staticmethod
    def _convert_tool_choice(
        tool_choice: Optional[Union[str, Dict[str, Any]]]
    ) -> Optional[Dict[str, Any]]:
        """Convert OpenAI tool_choice to Anthropic's format."""
        if tool_choice is None:
            return None
        if isinstance(tool_choice, str):
            if tool_choice == "none":
                return None
            if tool_choice in {"auto", "any"}:
                return {"type": tool_choice}
            return {"type": "tool", "name": tool_choice}

        choice_type = tool_choice.get("type")
        if choice_type == "function":
            function = tool_choice.get("function") or {}
            return {"type": "tool", "name": function.get("name")}
        return tool_choice

    @staticmethod
    def _convert_messages(messages: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        """Convert an OpenAI-style ReAct history to Anthropic messages."""
        system_parts: List[str] = []
        converted: List[Dict[str, Any]] = []

        pending_tool_results: List[Dict[str, Any]] = []

        def flush_tool_results() -> None:
            if pending_tool_results:
                converted.append({"role": "user", "content": list(pending_tool_results)})
                pending_tool_results.clear()

        for message in messages:
            role = message.get("role")
            content = message.get("content") or ""

            if role == "system":
                if content:
                    system_parts.append(str(content))
                continue

            if role == "assistant":
                flush_tool_results()
                blocks: List[Dict[str, Any]] = []
                if content:
                    blocks.append({"type": "text", "text": str(content)})
                for tool_call in message.get("tool_calls") or []:
                    function = tool_call.get("function") or {}
                    arguments = function.get("arguments") or "{}"
                    if isinstance(arguments, str):
                        try:
                            arguments = json.loads(arguments)
                        except json.JSONDecodeError:
                            arguments = {"raw_arguments": arguments}
                    blocks.append({
                        "type": "tool_use",
                        "id": tool_call["id"],
                        "name": function["name"],
                        "input": arguments,
                    })
                if blocks:
                    converted.append({"role": "assistant", "content": blocks})
                continue

            if role == "tool":
                pending_tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": message["tool_call_id"],
                    "content": str(content),
                })
                continue

            flush_tool_results()
            converted.append({"role": "user", "content": content})

        flush_tool_results()
        return "\n\n".join(system_parts), converted

    @staticmethod
    def _normalize_tool_response(response: Any) -> Any:
        """Return an OpenAI-shaped response consumed by the existing ReAct loop."""
        text_parts: List[str] = []
        tool_calls = []
        for block in response.content or []:
            block_type = getattr(block, "type", None)
            if block_type == "text" and getattr(block, "text", None):
                text_parts.append(block.text)
            elif block_type == "tool_use":
                tool_calls.append(SimpleNamespace(
                    id=block.id,
                    type="function",
                    function=SimpleNamespace(
                        name=block.name,
                        arguments=json.dumps(block.input or {}, ensure_ascii=False),
                    ),
                ))

        input_tokens = getattr(response.usage, "input_tokens", 0) or 0
        output_tokens = getattr(response.usage, "output_tokens", 0) or 0
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(
                content="".join(text_parts),
                tool_calls=tool_calls or None,
                reasoning_content=None,
            ))],
            usage=SimpleNamespace(
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            ),
            model=getattr(response, "model", None),
            stop_reason=getattr(response, "stop_reason", None),
            raw_response=response,
        )

    async def generate_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = "auto",
        temperature: Optional[float] = 0.6,
        max_tokens: int = 8192,
        **kwargs: Any,
    ) -> Any:
        """Call Anthropic Messages with native tool_use/tool_result semantics."""
        system, anthropic_messages = self._convert_messages(messages)
        request_params: Dict[str, Any] = {
            "model": self.model,
            "messages": anthropic_messages,
            "max_tokens": max_tokens,
            **kwargs,
        }
        if temperature is not None:
            request_params["temperature"] = temperature
        if system:
            request_params["system"] = system
        converted_tools = self._convert_tools(tools)
        if converted_tools:
            request_params["tools"] = converted_tools
            converted_choice = self._convert_tool_choice(tool_choice)
            if converted_choice:
                request_params["tool_choice"] = converted_choice

        try:
            response = await self.client.messages.create(**request_params)
            return self._normalize_tool_response(response)
        except APIConnectionError as e:
            raise NetworkError(f"Network error when calling Anthropic API: {str(e)}") from e
        except AnthropicAPIError as e:
            raise APIError(f"Anthropic API error: {str(e)}") from e
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}") from e
    
    def add_image_to_messages(
        self,
        messages: List[Dict[str, Any]],
        image_path: Union[str, Path],
        text: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Add image to messages list for vision API
        
        :param messages: Existing message list
        :param image_path: Path to image file
        :param text: Optional text prompt to accompany the image
        :return: Updated messages list with image message
        """
        image_message = create_anthropic_image_message(image_path, text)
        messages.append(image_message)
        return messages
    
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        system: str = "",
        max_tokens = 4096*2,
        **kwargs
    ) -> Union[GenerateResponse, StreamingResponse]:
        """
        Generate response
        
        :param messages: Message list (can include image messages created with add_image_to_messages)
        :param stream: Whether to stream response
        :param system: System prompt
        :param max_tokens: Maximum tokens
        :param kwargs: Other Anthropic API parameters (such as temperature, etc.)
        :return: StreamingResponse for streaming, GenerateResponse for non-streaming
        """
        
        try:
            # Build request parameters
            request_params = {
                'model': self.model,
                'system':system,
                'messages': messages,
                'stream': stream,
                "max_tokens":max_tokens,
                **kwargs
            }
            
            if stream:
                response = await self.client.messages.create(**request_params)
                return await self._handle_streaming_response(response)
            else:
                response = await self.client.messages.create(**request_params)
                content = ""
                if response.content and len(response.content) > 0:
                    for block in response.content:
                        block_text = getattr(block, "text", None)
                        if block_text:
                            content += block_text
                
                usage = None
                if hasattr(response, 'usage') and response.usage:
                    usage = TokenUsage(
                        prompt_tokens=response.usage.input_tokens,
                        completion_tokens=response.usage.output_tokens,
                        total_tokens=response.usage.input_tokens + response.usage.output_tokens
                    )
                
                return GenerateResponse(content=content, usage=usage)
        
        except APIConnectionError as e:
            raise NetworkError(f"Network error when calling Anthropic API: {str(e)}") from e
        except AnthropicAPIError as e:
            # Extract detailed error information
            error_details = str(e)
            if hasattr(e, 'status_code'):
                error_details += f" (Status: {e.status_code})"
            if hasattr(e, 'body') and e.body:
                try:
                    if isinstance(e.body, dict):
                        error_details += f" (Body: {json.dumps(e.body, ensure_ascii=False)})"
                    else:
                        error_details += f" (Body: {str(e.body)})"
                except:
                    pass
            if hasattr(e, 'message') and e.message:
                error_details += f" (Message: {e.message})"
            raise APIError(f"Anthropic API error: {error_details}") from e
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}") from e
    
    async def _handle_streaming_response(self, response) -> StreamingResponse:
        """
        Handle Anthropic streaming response
        
        :param response: Anthropic streaming response object
        :return: StreamingResponse object
        """
        usage = None
        
        async def stream_generator() -> AsyncIterator[str]:
            nonlocal usage
            async for event in response:
                if event.type == 'content_block_delta':
                    if event.delta.type == 'text_delta':
                        yield event.delta.text
                elif event.type == 'message_start':
                    pass
                elif event.type == 'content_block_start':
                    pass
                elif event.type == 'content_block_stop':
                    pass
                elif event.type == 'message_delta':
                    if hasattr(event, 'usage') and event.usage:
                        usage = TokenUsage(
                            prompt_tokens=event.usage.input_tokens,
                            completion_tokens=event.usage.output_tokens,
                            total_tokens=event.usage.input_tokens + event.usage.output_tokens
                        )
                elif event.type == 'message_stop':
                    pass
        
        async def get_usage():
            return usage
        
        return StreamingResponse(stream_generator(), usage_getter=get_usage)
