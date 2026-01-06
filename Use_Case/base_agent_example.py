"""ReAct Agent Usage Example"""
import asyncio
import os
from pathlib import Path

from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_token_usage,
    print_tool_result
)
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent import ReActAgent, OpenAIClient
import dotenv

dotenv.load_dotenv()


async def main():
    """Demonstrate ReAct Agent usage"""
    print("=== ReAct Agent Usage Example ===\n")

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    # Initialize client (read from environment variables)
    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return
    
    # Create working directory
    work_dir = Path(__file__).parent / "agent_work"
    work_dir.mkdir(exist_ok=True)
    
    print(f"Working directory: {work_dir}\n")

    agent = ReActAgent(
        client=client,
        working_dir=str(work_dir),
    )
    async for message in agent.run("Create a text file and then modify it"):
        if message[0]==AgentMessageType.SYSTEM:
            print("SYSTEM")
            content=message[1]
            print_system_prompt(content)
        elif message[0]==AgentMessageType.USER:
            print("USER")
            content=message[1]
            print_user_message(content)
        elif message[0]==AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print("ASSISTANT_WITH_TOOL_CALL")
            print_assistant_message(message[1],message[2], message[3])
        elif message[0]==AgentMessageType.ASSISTANT:
            print("ASSISTANT")
            print_assistant_message(content=message[1], token_usage=message[2])
            print_token_usage(message[3])
        elif message[0]==AgentMessageType.TOOL_RESPONSE:
            print("TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif message[0]==AgentMessageType.ERROR_TOOL_RESPONSE:
            print("ERROR_TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif message[0]==AgentMessageType.MAXIMUM:
            print("MAXIMUM")
            print_token_usage(message[2])
            print(message[1])


if __name__ == "__main__":
    asyncio.run(main())

