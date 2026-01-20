"""ReActAgent 示例：调用 pptx 技能并使用 Node 脚本生成 PPTX（pip 安装版）"""

import asyncio
import os
from pathlib import Path

import dotenv
from lightweight_agent import OpenAIClient, ReActAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_assistant_message,
    print_system_prompt,
    print_token_usage,
    print_tool_result,
    print_user_message,
)

dotenv.load_dotenv()

# demo_skills 目录内含 pptx 技能与 html2pptx.js
WORKDIR = Path(__file__).resolve().parent / "demo_skills"


def _ensure_workdir(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Working dir not found: {path}. "
            "请先确认 demo_skills 目录存在，或根据实际路径调整 WORKDIR。"
        )
    return path


async def main() -> None:
    """演示使用已安装的 lightweight-agent 调用 pptx 技能"""
    workdir = _ensure_workdir(WORKDIR)

    api_key = os.getenv("LIGHTWEIGHT_AGENT_API_KEY") or os.getenv("LLM_API_KEY")
    base_url = os.getenv("LIGHTWEIGHT_AGENT_API_BASE") or os.getenv("LLM_API_BASE")
    model = os.getenv("LIGHTWEIGHT_AGENT_MODEL") or os.getenv("MODEL") or "gpt-4o-mini"

    if not api_key:
        raise RuntimeError("缺少 LLM API Key，请在 .env 中设置 LIGHTWEIGHT_AGENT_API_KEY 或 LLM_API_KEY。")

    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    agent = ReActAgent(
        client=client,
        working_dir=str(workdir),
    )

    task = (
        "你是演示文稿助手。"
        "1) 调用 skill 工具加载 pptx 技能，严格遵守其中的 HTML 编写规则。"
        "2) 生成一份 6 页以内的简明演示，主题示例：`轻量级 Agent 框架概览`。"
        "3) 将 HTML 写入工作目录（例如 slides.html）。"
        "4) 使用 run_node_file 工具调用 scripts/html2pptx.js，把 HTML 转成 slides.pptx。"
        "5) 最后回复生成的文件路径、关键步骤与潜在验证方式。"
    )

    print("=== ReActAgent PPTX 技能示例（pip 安装版）===\n")
    print(f"工作目录: {workdir}\n")
    print(f"任务: {task}\n")
    print("开始执行...\n")

    async for message in agent.run(task, max_iterations=120):
        msg_type = message[0]

        if msg_type == AgentMessageType.SYSTEM:
            print("SYSTEM")
            print_system_prompt(message[1])
        elif msg_type == AgentMessageType.USER:
            print("USER")
            print_user_message(message[1])
        elif msg_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print("ASSISTANT_WITH_TOOL_CALL")
            print_assistant_message(message[1], message[2], message[3])
        elif msg_type == AgentMessageType.ASSISTANT:
            print("ASSISTANT")
            print_assistant_message(content=message[1], token_usage=message[2])
            print_token_usage(message[3])
        elif msg_type == AgentMessageType.TOOL_RESPONSE:
            print("TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif msg_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print("ERROR_TOOL_RESPONSE")
            print_tool_result(message[1], message[2])
        elif msg_type == AgentMessageType.MAXIMUM:
            print("MAXIMUM")
            print_token_usage(message[2])
            print(message[1])

    print("\n=== PPTX 生成任务完成 ===\n")


if __name__ == "__main__":
    asyncio.run(main())

