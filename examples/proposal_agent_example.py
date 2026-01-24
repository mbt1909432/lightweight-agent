"""ProposalAgent 使用示例

演示如何使用 ProposalAgent 对论文草稿进行「打样阶段 / proposal 版本」的全面增强：
- 理论分析补全、相关工作扩展、表格美化、清理 TODO/占位符、自洽性检查

说明：
- 该示例参考 `examples/polish_agent_example.py` 的结构与打印方式
- 建议将需要处理的论文文件（如 `sample.tex`）放在 `examples/proposal/` 目录下
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径，以便导入 lightweight_agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.lightweight_agent import OpenAIClient
from src.lightweight_agent.agent.extension.proposal_agent import ProposalAgent
from src.lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_token_usage,
    print_tool_result,
)
from src.lightweight_agent.agent.react_agent import AgentMessageType
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
    reraise=True,
)
async def execute_proposal_task(
    agent: ProposalAgent,
    task: str,
    max_iterations: int = 300,
) -> ProposalAgent:
    """
    执行 proposal 打样增强任务，带重试逻辑

    Args:
        agent: ProposalAgent 实例（已配置好 working_dir）
        task: 任务描述
        max_iterations: 最大迭代次数，默认 300

    Returns:
        ProposalAgent: 执行完成后的 agent 实例

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

    print("\n=== Proposal 打样增强任务完成! ===\n")

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

    return agent


async def main():
    """演示 ProposalAgent 的使用：对论文草稿做 proposal 阶段的增强与自洽性检查。"""

    work_dir = Path(__file__).parent / "proposal"
    print("=== ProposalAgent 使用示例 ===\n")

    # 1. 初始化客户端
    api_key = os.getenv("LIGHTWEIGHT_AGENT_API_KEY")
    base_url = os.getenv("LIGHTWEIGHT_AGENT_API_BASE")
    model = os.getenv("LIGHTWEIGHT_AGENT_MODEL")
    print(api_key)
    print(base_url)
    print(model)

    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return

    # 2. 创建 ProposalAgent
    agent = ProposalAgent(
        client=client,
        working_dir=str(work_dir),
    )

    # 3. 定义 proposal 打样增强任务
    task = (
        "在当前工作目录中，找到论文主文件，对论文进行 proposal 阶段的全面增强："
        "补全理论分析（形式化建模/必要的定理与证明框架）、"
        "扩展 Related Work（不需要插入任何引用）、"
        "美化所有 LaTeX 表格（booktabs + 隔行变色 + 最佳结果高亮）、"
        "删除所有 TODO / 占位符 / 开发过程注释，"
        "并检查摘要、结论与正文描述中的数值是否与表格/图表完全一致，"
        "根据当前已有数据调整文字描述，使全文结构完整、逻辑自洽。"
        "最后必须保存重要产物（增强后的主文件及说明）。"
    )

    try:
        await execute_proposal_task(
            agent=agent,
            task=task,
        )
    except NoArtifactsException:
        print("重试3次后仍失败：没有保存的产物")
        return


if __name__ == "__main__":
    asyncio.run(main())


