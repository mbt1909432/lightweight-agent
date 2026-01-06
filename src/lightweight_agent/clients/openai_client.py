"""OpenAI Client Implementation"""
from typing import AsyncIterator, Optional, Union, List, Dict, Any
from openai import AsyncOpenAI
from openai._exceptions import APIError as OpenAIAPIError, APIConnectionError

from .base import BaseClient
from ..exceptions import APIError, NetworkError, ValidationError
from ..utils import validate_prompt
from ..models import GenerateResponse, StreamingResponse, TokenUsage


class OpenAIClient(BaseClient):
    """OpenAI async client"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize OpenAI client
        
        :param api_key: API key, default read from environment variable
        :param base_url: API base URL, default read from environment variable
        :param model: Model name, default read from environment variable
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key,base_url=base_url,max_retries=4)
    
    async def generate(
        self,
        messages: List[Dict[str, Any]],
        stream: bool = False,
        temperature=0.6,
        **kwargs
    ) -> Union[GenerateResponse, StreamingResponse]:
        """
        Generate response
        
        :param messages: Message list
        :param stream: Whether to stream response
        :param temperature: Temperature parameter
        :return: StreamingResponse for streaming, GenerateResponse for non-streaming
        """
        try:
            # Build request parameters
            request_params = {
                'model': self.model,
                'messages': messages,
                'stream': stream,
                "temperature":temperature,
                **kwargs
            }
            
            if stream:
                response = await self.client.chat.completions.create(**request_params)
                return await self._handle_streaming_response(response)
            else:
                response = await self.client.chat.completions.create(**request_params)
                content = response.choices[0].message.content or ""
                print(response)

                if response.usage:
                    usage = TokenUsage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens
                    )
                
                return GenerateResponse(content=content, usage=usage)
        
        except APIConnectionError as e:
            raise NetworkError(f"Network error when calling OpenAI API: {str(e)}") from e
        except OpenAIAPIError as e:
            raise APIError(f"OpenAI API error: {str(e)}") from e
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}") from e
    
    async def _handle_streaming_response(self, response) -> StreamingResponse:
        """
        Handle OpenAI streaming response
        
        :param response: OpenAI streaming response object
        :return: StreamingResponse object
        """
        usage = None
        
        async def stream_generator() -> AsyncIterator[str]:
            nonlocal usage
            async for chunk in response:
                if chunk.choices:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content

                if hasattr(chunk, 'usage'):
                    usage = TokenUsage(
                        prompt_tokens=chunk.usage["prompt_tokens"],
                        completion_tokens=chunk.usage["completion_tokens"],
                        total_tokens=chunk.usage["total_tokens"]
                    )


        async def get_usage():
            return usage
        
        return StreamingResponse(stream_generator(), usage_getter=get_usage)
    


