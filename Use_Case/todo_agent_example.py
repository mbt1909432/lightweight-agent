"""TODO-based Agent Usage Example"""
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
from lightweight_agent import OpenAIClient
from lightweight_agent.agent import TodoBasedAgent
from lightweight_agent.agent.react_agent import AgentMessageType
import dotenv

dotenv.load_dotenv()


async def main():
    """Demonstrate TODO-based Agent usage"""
    print("=== TODO-based Agent Usage Example ===\n")

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
    work_dir = Path(__file__).parent / "todo_agent_work"
    work_dir.mkdir(exist_ok=True)

    print(f"Working directory: {work_dir}\n")

    # Create TODO-based Agent
    # TodoBasedAgent automatically registers TODO-related tools
    # (create_todo_list, update_todo_status, save_important_artifacts)
    agent = TodoBasedAgent(
        client=client,
        working_dir=str(work_dir),
    )

    # Run task - TODO agent will automatically:
    # 1. Explore working directory
    # 2. Create TODO list
    # 3. Execute TODO items
    # 4. Save important artifacts
    with open(fr"E:\pycharm_project\lightweight-agent\Use_Case\code.txt",'r',encoding='utf-8') as f:
        content=f.read()
    async for message in agent.run(f"用python画可视化顶会实验图，一个python脚本只能有一个图，并生成png:{content}"):
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
    # Optional: View TODO list and artifacts
    print("\n=== TODO List Summary ===")
    summary = agent.get_todo_summary()
    print(f"Total: {summary['total']}, "
          f"Pending: {summary['pending']}, "
          f"In Progress: {summary['in_progress']}, "
          f"Completed: {summary['completed']}, "
          f"Failed: {summary['failed']}")

    print("\n=== Saved Artifacts ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("No saved artifacts")


if __name__ == "__main__":
    asyncio.run(main())

