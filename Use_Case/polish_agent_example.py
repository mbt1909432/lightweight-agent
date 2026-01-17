"""PolishAgent 使用示例

演示如何使用 PolishAgent 对论文草稿进行「打样级」润色与结构自洽检查。
"""

import asyncio
import os
from pathlib import Path

from lightweight_agent import OpenAIClient
from lightweight_agent.agent.extension.polish_agent import PolishAgent
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_token_usage,
    print_tool_result,
)
from lightweight_agent.agent.react_agent import AgentMessageType
from tenacity import retry, stop_after_attempt, retry_if_exception_type, wait_fixed
import dotenv


dotenv.load_dotenv()


class NoArtifactsException(Exception):
    """自定义异常类，用于触发重试逻辑（当没有保存的产物时）"""
    pass


@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(NoArtifactsException),
    wait=wait_fixed(1.0),
    reraise=True
)
async def execute_polish_task(
    agent: PolishAgent,
    task: str,
    max_iterations: int = 300
) -> PolishAgent:
    """
    执行打样润色任务，带重试逻辑
    
    Args:
        agent: PolishAgent 实例（已配置好 working_dir）
        task: 任务描述
        max_iterations: 最大迭代次数，默认 300
    
    Returns:
        PolishAgent: 执行完成后的 agent 实例
    
    Raises:
        NoArtifactsException: 重试指定次数后仍没有保存的产物
    """
    async for message in agent.run(task, max_iterations=max_iterations):
        if message[0] == AgentMessageType.SYSTEM:
            print("SYSTEM")
            content = message[1]
            print_system_prompt(content)
        elif message[0] == AgentMessageType.USER:
            print("USER")
            content = message[1]
            print_user_message(content)
        elif message[0] == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print("ASSISTANT_WITH_TOOL_CALL")
            print_assistant_message(message[1], message[2], message[3])
        elif message[0] == AgentMessageType.ASSISTANT:
            print("ASSISTANT")
            print_assistant_message(content=message[1], token_usage=message[2])
            print_token_usage(message[3])
        elif message[0] == AgentMessageType.TOOL_RESPONSE:
            print("TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif message[0] == AgentMessageType.ERROR_TOOL_RESPONSE:
            print("ERROR_TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif message[0] == AgentMessageType.MAXIMUM:
            print("MAXIMUM")
            print_token_usage(message[2])
            print(message[1])

    print("\n=== Polish 打样润色任务完成! ===\n")

    # 检查是否有保存的产物
    if not agent.get_artifacts():
        raise NoArtifactsException("没有保存的产物，需要重新执行")

    # 可选：查看 TODO 列表摘要
    print("=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(
        f"总计: {summary['total']}, "
        f"待处理: {summary['pending']}, "
        f"进行中: {summary['in_progress']}, "
        f"已完成: {summary['completed']}, "
        f"失败: {summary['failed']}"
    )

    # 可选：查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")


async def main():
    """演示 PolishAgent 的使用：对论文草稿做打样级润色与自洽性检查。"""
    print("=== PolishAgent 使用示例 ===\n")

    # 1. 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
        print("✓ LLM 客户端初始化成功")
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return

    # 2. 准备一个论文工作目录
    work_dir =fr"E:\pycharm_project\lightweight-agent\Use_Case\polish"
    
    print(f"工作目录: {work_dir}\n")
    print("提示: 请在工作目录中放置论文主文件（例如 latex.tex 或 paper.md）\n")

    # 3. 创建 PolishAgent
    agent = PolishAgent(
        client=client,
        working_dir=str(work_dir),
    )

    # 4. 定义打样润色任务
    task = (
        "在当前工作目录中，找到论文主文件，对论文进行打样级润色："
        "删除所有 TODO / 占位符 / 开发过程注释，"
        "统一语气为正式学术写作风格，"
        "检查摘要、结论与正文描述中的数值是否与表格/图表完全一致，"
        "并根据当前示例数据调整文字描述，使全文结构完整、逻辑自洽。文章内容必须和标题相符"
    )

    try:
        await execute_polish_task(
            agent=agent,
            task=task
        )
    except NoArtifactsException:
        print("重试3次后仍失败：没有保存的产物")
        return


if __name__ == "__main__":
    asyncio.run(main())

