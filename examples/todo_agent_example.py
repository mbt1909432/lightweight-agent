"""TODO-based Agent 使用示例"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径，以便导入lightweight_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.lightweight_agent import OpenAIClient
from src.lightweight_agent.agent import TodoBasedAgent
import dotenv
dotenv.load_dotenv()


async def main():
    """演示 TODO-based Agent 的使用"""
    print("=== TODO-based Agent 使用示例 ===\n")

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    # 初始化客户端（从环境变量读取配置）
    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "todo_agent_work"
    work_dir.mkdir(exist_ok=True)
    
    print(f"工作目录: {work_dir}\n")
    
    # 创建 TODO-based Agent
    # TodoBasedAgent 会自动注册 TODO 相关工具（create_todo_list, update_todo_status, save_important_artifacts）
    agent = TodoBasedAgent(
        client=client,
        working_dir=str(work_dir),
    )
    
    # 运行任务 - TODO agent 会自动：
    # 1. 探索工作目录
    # 2. 创建 TODO 列表
    # 3. 执行 TODO 项
    # 4. 保存重要产物
    await agent.run("创建一个随意用python画个图用matpolit")
    
    # 可选：查看 TODO 列表和产物
    print("\n=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")
    
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")


if __name__ == "__main__":
    # 运行完整示例
    asyncio.run(main())
    
    # 运行简单示例
    # asyncio.run(simple_example())

