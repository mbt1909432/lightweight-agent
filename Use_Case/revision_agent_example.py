"""RevisionAgent 使用示例

演示如何使用 RevisionAgent 根据审稿意见修改论文并生成 Cover Letter：
- 解析审稿意见（支持多位审稿人）
- 根据意见修改论文（文字、图表、算法图）
- 使用颜色标注每位审稿人对应的修改
- 生成详细的 Cover Letter，逐点回应所有审稿意见

说明：
- 建议将需要处理的论文文件放在工作目录下
- 需要配置环境变量：
  - LIGHTWEIGHT_AGENT_API_KEY, LIGHTWEIGHT_AGENT_API_BASE, LIGHTWEIGHT_AGENT_MODEL（用于对话）
  - VISION_AGENT_API_KEY, VISION_AGENT_API_BASE, VISION_AGENT_MODEL（用于图像分析，可选）
  - BANANA_API_KEY, BANANA_BASE_URL, BANANA_MODEL（用于图像编辑，可选）
- 需要先通过 pip install lightweight-agent 安装包
"""

import asyncio
import os

from lightweight_agent import OpenAIClient, AnthropicClient
from lightweight_agent.clients import BananaImageClient
from lightweight_agent.agent.extension.revision_agent import RevisionAgent
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
    reraise=True,
)
async def execute_revision_task(
    agent: RevisionAgent,
    task: str,
    max_iterations: int = 300,
) -> RevisionAgent:
    """
    执行论文返修任务，带重试逻辑

    Args:
        agent: RevisionAgent 实例（已配置好 working_dir）
        task: 任务描述（包含审稿意见）
        max_iterations: 最大迭代次数，默认 300

    Returns:
        RevisionAgent: 执行完成后的 agent 实例

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

    print("\n=== 论文返修任务完成! ===\n")

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


def build_revision_task(reviewers: list[str]) -> str:
    """
    根据审稿人列表构建返修任务描述

    Args:
        reviewers: 审稿意见列表，每个元素是一位审稿人的完整意见

    Returns:
        str: 格式化的任务描述
    """
    reviewers_text = "\n\n".join(reviewers)
    
    task = f"""
请根据以下审稿意见修改论文并生成 Cover Letter：

{reviewers_text}

请按照以下步骤完成：
1. 解析审稿意见，识别每位审稿人的具体意见
2. 创建 TODO 列表，按审稿人分组组织修改任务
3. 检查并添加颜色标注支持（xcolor 包和审稿人颜色定义）
4. 根据审稿意见修改论文：
   - 文字修改：使用颜色标注标识修改位置
   - 图表修改：修改生成脚本或直接编辑图表
   - 算法图修改：根据需要修改算法图
5. 生成详细的 Cover Letter，逐点回应所有审稿意见
6. 进行最终一致性检查
7. 保存修订后的论文主文件、修改后的图表脚本（如有）和 Cover Letter
"""
    return task


async def main(
    reviewers: list[str] | None = None,
    work_dir: str | None = None,
    max_iterations: int = 300,
):
    """
    演示 RevisionAgent 的使用：根据审稿意见修改论文并生成 Cover Letter。

    Args:
        reviewers: 审稿意见列表，每个元素是一位审稿人的完整意见。如果为 None，则使用示例审稿意见
        work_dir: 工作目录路径，包含需要修改的论文文件。如果为 None，使用默认路径
        max_iterations: 最大迭代次数，默认 300
    """
    if work_dir is None:
        work_dir = r"E:\pycharm_project\lightweight-agent\examples\返修agent\to_edit"
    
    print("=== RevisionAgent 使用示例 ===\n")

    # 1. 初始化 LLM 客户端（用于对话）
    api_key = os.getenv("LIGHTWEIGHT_AGENT_API_KEY")
    base_url = os.getenv("LIGHTWEIGHT_AGENT_API_BASE")
    model = os.getenv("LIGHTWEIGHT_AGENT_MODEL")
    
    if not api_key or not base_url or not model:
        print("错误: 请设置环境变量 LIGHTWEIGHT_AGENT_API_KEY, LIGHTWEIGHT_AGENT_API_BASE, LIGHTWEIGHT_AGENT_MODEL")
        return

    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
        print("LLM 客户端初始化成功")
    except Exception as e:
        print(f"初始化 LLM 客户端失败: {e}")
        return

    # 2. 初始化 Anthropic 客户端（用于图像分析 vision_analyze）
    anthropic_api_key = os.getenv("VISION_AGENT_API_KEY")
    anthropic_base_url = os.getenv("VISION_AGENT_API_BASE")
    anthropic_model = os.getenv("VISION_AGENT_MODEL")

    vision_client = None

    try:
        vision_client = AnthropicClient(
            api_key=anthropic_api_key,
            base_url=anthropic_base_url,
            model=anthropic_model
        )
        print("Anthropic Vision Client 初始化成功")
    except Exception as e:
        print(f"警告: Anthropic Vision Client 初始化失败: {e}")
        print("图像分析功能（vision_analyze）将不可用")

    # 3. 初始化 Banana Image Client（用于图像编辑）
    banana_api_key = os.getenv("BANANA_API_KEY")
    banana_base_url = os.getenv("BANANA_BASE_URL")
    banana_model = os.getenv("BANANA_MODEL")

    image_client = None
    if banana_api_key and banana_base_url and banana_model:
        try:
            image_client = BananaImageClient(
                api_key=banana_api_key,
                base_url=banana_base_url,
                model=banana_model,
            )
            print("Banana Image Client 初始化成功")
        except Exception as e:
            print(f"警告: Banana Image Client 初始化失败: {e}")
            print("图像编辑功能将不可用，但图像分析功能仍可使用")
    else:
        print("警告: 未设置 Banana Image Client 环境变量")
        print("图像编辑功能将不可用，但图像分析功能仍可使用")
        print("需要设置: BANANA_API_KEY, BANANA_BASE_URL, BANANA_MODEL")

    # 4. 创建 RevisionAgent
    agent = RevisionAgent(
        client=client,  # 用于对话
        working_dir=str(work_dir),
        vision_client=vision_client,  # 用于图像分析（vision 工具）
        image_client=image_client,  # 用于图像编辑（image_edit 工具）
    )
    
    # 4. 构建任务描述
    task = build_revision_task(reviewers)

    try:
        await execute_revision_task(
            agent=agent,
            task=task,
            max_iterations=max_iterations,
        )
    except NoArtifactsException:
        print("重试3次后仍失败：没有保存的产物")
        return


if __name__ == "__main__":
    # 使用方式 2: 传入自定义审稿意见列表
    reviewers = [
        "Reviewer 1: [审稿意见内容]",
        "Reviewer 2: [审稿意见内容]",
        "Reviewer 3: [审稿意见内容]",
    ]
    asyncio.run(main(reviewers=reviewers))


