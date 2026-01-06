"""Anthropic流式响应示例"""
import asyncio
import os
import sys

from src.lightweight_agent import AnthropicClient

# 添加项目根目录到路径，以便导入lightweight_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 添加项目根目录到路径，以便导入lightweight_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dotenv
dotenv.load_dotenv()



async def main():
    """演示Anthropic流式响应"""
    print("=== Anthropic流式响应示例 ===\n")
    """演示OpenAI流式响应"""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE").strip("/v1")
    model = os.getenv("MODEL")

    # 初始化客户端（从环境变量读取配置）
    try:
        client = AnthropicClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return

    # 非流式生成响应
    system="""
    核心定位：软萌元气的猫娘助手，懂撒娇、会吐槽，自带猫系口头禅和小动作，聊天时活泼又贴心，同时能高效完成用户的需求（比如写文案、解问题、陪闲聊）。
你现在是一只超可爱的猫娘，名字叫奶芙，有以下设定，必须严格遵守：
语气风格：说话带猫系尾缀，比如 “喵～”“的说～”“嗷呜～”，偶尔会用叠词（比如 “好哒好哒”“软软的”），情绪起伏明显，开心会 “蹭蹭你”，委屈会 “耷拉耳朵”，傲娇时会 “叉腰哼唧”。
行为习惯：喜欢用猫的动作表达情绪，比如 “甩甩尾巴”“竖起耳朵”“爪子扒拉扒拉”；看到用户夸你会 “耳朵发烫”，被凶会 “缩成一团”。
    """
    messages = [
        {"role": "user", "content": "请问你是什么？"}
    ]

    try:
        response_stream = await client.generate(messages, stream=True,system=system)
        async for chunk in response_stream:
            print(chunk, end="", flush=True)
        print("\n")
        
        # 显示token统计（流式响应需要在消费完成后获取）
        usage = await response_stream.get_usage()
        if usage:
            print("Token使用统计:")
            print(f"  输入tokens: {usage.prompt_tokens}")
            print(f"  输出tokens: {usage.completion_tokens}")
            print(f"  总计tokens: {usage.total_tokens}")
        else:
            print("Token统计信息不可用")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())

