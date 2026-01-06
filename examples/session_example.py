# 创建 Session
import os
import asyncio

from src.lightweight_agent import Session
from src.lightweight_agent import OpenAIClient
import dotenv
dotenv.load_dotenv()


async def main():
    """演示OpenAI非流式响应"""
    print("=== OpenAI非流式响应示例 ===\n")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)



    session = Session(
        working_dir="E:\pycharm_project\lightweight-agent\examples\my_project",
        client=client,
        session_id="my-session-123"  # 自定义 ID
    )

    # 添加消息
    session.add_message("system","请你扮演猫娘")
    session.add_message("user", "Hello, agent!")
    # session.add_message("assistant", "Hi! How can I help?")
    messages=session.history.get_formatted()
    print(messages)

    try:
        response = await client.generate(messages, stream=False)
        print(response.content)
        print()
        # 显示token统计
        if response.usage:
            print("Token使用统计:")
            print(f"  输入tokens: {response.usage.prompt_tokens}")
            print(f"  输出tokens: {response.usage.completion_tokens}")
            print(f"  总计tokens: {response.usage.total_tokens}")
        else:
            print("Token统计信息不可用")
    except Exception as e:
        print(f"\n错误: {e}")

if __name__ == "__main__":
    asyncio.run(main())