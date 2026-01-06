"""ReAct Agent 使用示例"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径，以便导入lightweight_agent
# 必须在所有导入之前执行
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lightweight_agent.agent.pretty_print import print_system_prompt, print_user_message, print_assistant_message, \
    print_token_usage, print_tool_result
from src.lightweight_agent.agent.react_agent import AgentMessageType
from src.lightweight_agent import AnthropicClient, ReActAgent, OpenAIClient
import dotenv
dotenv.load_dotenv()



async def main():
    """演示 ReAct Agent 的使用"""
    print("=== ReAct Agent 使用示例 ===\n")
    """演示Anthropic流式响应"""

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")#.strip("/v1")
    model = os.getenv("MODEL")

    # 初始化客户端（从环境变量读取配置）
    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "agent_work"
    work_dir.mkdir(exist_ok=True)
    
    print(f"工作目录: {work_dir}\n")

    agent = ReActAgent(
        client=client,
        working_dir=str(work_dir),
    )
    async for message in agent.run("创建一个随意txt文件 然后修改它"):
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
    # 运行完整示例
    asyncio.run(main())
    
    # 运行简单示例
    # asyncio.run(simple_example())

