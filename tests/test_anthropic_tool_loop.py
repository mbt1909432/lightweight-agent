import json
from types import SimpleNamespace

import pytest

from lightweight_agent import AnthropicClient
from lightweight_agent.agent.react_agent import AgentMessageType, ReActAgent


def _response(*blocks, input_tokens=10, output_tokens=5, stop_reason="end_turn"):
    return SimpleNamespace(
        content=list(blocks),
        usage=SimpleNamespace(input_tokens=input_tokens, output_tokens=output_tokens),
        model="claude-sonnet-5",
        stop_reason=stop_reason,
    )


def test_converts_openai_react_history_to_anthropic_messages():
    system, messages = AnthropicClient._convert_messages([
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "read the file"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": "tool-1",
                "type": "function",
                "function": {"name": "Read", "arguments": '{"file_path":"/tmp/a.txt"}'},
            }],
        },
        {"role": "tool", "tool_call_id": "tool-1", "content": '{"content":"ok"}'},
    ])

    assert system == "system prompt"
    assert messages[1]["content"][0] == {
        "type": "tool_use",
        "id": "tool-1",
        "name": "Read",
        "input": {"file_path": "/tmp/a.txt"},
    }
    assert messages[2]["content"][0]["type"] == "tool_result"
    assert messages[2]["content"][0]["tool_use_id"] == "tool-1"


@pytest.mark.asyncio
async def test_react_agent_executes_native_anthropic_tool_loop(tmp_path):
    target = tmp_path / "paper.tex"
    target.write_text("paper content", encoding="utf-8")

    client = AnthropicClient(
        api_key="test-key",
        base_url="https://example.invalid",
        model="claude-sonnet-5",
    )
    calls = []

    async def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            return _response(
                SimpleNamespace(
                    type="tool_use",
                    id="tool-read",
                    name="Read",
                    input={"file_path": str(target)},
                ),
                stop_reason="tool_use",
            )
        return _response(SimpleNamespace(type="text", text="done"))

    client.client = SimpleNamespace(messages=SimpleNamespace(create=create))
    agent = ReActAgent(client=client, working_dir=str(tmp_path))

    events = [event async for event in agent.run("Read paper.tex", max_iterations=5)]

    assert any(event[0] == AgentMessageType.TOOL_RESPONSE for event in events)
    assert events[-1][0] == AgentMessageType.ASSISTANT
    assert events[-1][1] == "done"
    assert calls[0]["tools"]
    tool_results = [
        block
        for message in calls[1]["messages"]
        if isinstance(message.get("content"), list)
        for block in message["content"]
        if block.get("type") == "tool_result"
    ]
    assert len(tool_results) == 1
    assert tool_results[0]["tool_use_id"] == "tool-read"
    assert "paper content" in str(json.loads(tool_results[0]["content"]))
