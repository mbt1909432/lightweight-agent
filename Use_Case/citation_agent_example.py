"""CitationAgent 使用示例"""
import asyncio
import os
from pathlib import Path

from lightweight_agent import OpenAIClient
from lightweight_agent.agent.extension.citation_agent import CitationAgent
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_token_usage,
    print_tool_result
)
from lightweight_agent.agent.react_agent import AgentMessageType
import dotenv

dotenv.load_dotenv()


async def main():
    """演示 CitationAgent 的使用：将 BibTeX 引用插入到 LaTeX 文档中"""
    print("=== CitationAgent 使用示例 ===\n")

    # 1. 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    try:
        client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    except Exception as e:
        print(f"初始化客户端失败: {e}")
        return

    # 2. 创建工作目录
    work_dir = Path(__file__).parent / "citation_agent_work"
    work_dir.mkdir(exist_ok=True)

    print(f"工作目录: {work_dir}\n")

    # 示例：工作目录应包含：
    # - paper.tex (LaTeX 文档)
    # - references.txt 或 references.bib (BibTeX 条目源文件)

    # 3. 创建 CitationAgent
    # CitationAgent 会自动：
    # - 注册引用工具 (bibtex_extract, bibtex_insert)
    # - 注册 TODO 工具 (create_todo_list, update_todo_status, save_important_artifacts)
    # - 注册基础工具 (read_file, edit_file, list_directory)
    # - 移除不必要的工具 (write_file, run_python_file)
    agent = CitationAgent(
        client=client,
        working_dir=str(work_dir)
    )

    # 4. 运行引用插入任务
    # Agent 会自动：
    # - 创建 TODO 列表
    # - 探索目录并读取文件
    # - 从源文件提取 BibTeX 条目
    # - 将引用插入到 LaTeX 文档
    # - 保存修改后的 LaTeX 文件
    task = "Extract all BibTeX entries from references.txt and insert them into paper.tex"

    print(f"任务: {task}\n")
    print("开始执行...\n")

    async for message in agent.run(task, max_iterations=300):
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

    print("\n=== 引用插入完成! ===\n")

    # 可选：查看 TODO 列表摘要
    print("=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")

    # 可选：查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")


if __name__ == "__main__":
    asyncio.run(main())

