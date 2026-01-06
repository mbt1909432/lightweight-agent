"""OpenAI非流式响应示例"""
import asyncio
import os
import sys

# 添加项目根目录到路径，以便导入lightweight_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lightweight_agent import OpenAIClient
import dotenv
dotenv.load_dotenv()


async def main():
    """演示OpenAI非流式响应"""
    print("=== OpenAI非流式响应示例 ===\n")
    api_key=os.getenv("LLM_API_KEY")
    base_url=os.getenv("LLM_API_BASE")
    model=os.getenv("MODEL")
    
    # 初始化客户端（从环境变量读取配置）
    try:
        client = OpenAIClient(api_key=api_key,base_url=base_url,model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return
    
    # 非流式生成响应
    messages = [
        {"role": "system", "content": "你叫ciro"},
        {"role": "user", "content": "请问我叫什么？"}
    ]

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

