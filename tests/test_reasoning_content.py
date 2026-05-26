from lightweight_agent.session.history import MessageHistory


def test_assistant_reasoning_content_is_preserved_for_tool_followup():
    history = MessageHistory()

    history.add(
        role="assistant",
        content="",
        tool_calls=[
            {
                "id": "call_1",
                "type": "function",
                "function": {"name": "write_file", "arguments": '{"path":"ok.txt"}'},
            }
        ],
        reasoning_content="Need to create the requested file.",
    )

    assert history.get_formatted() == [
        {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": "call_1",
                    "type": "function",
                    "function": {"name": "write_file", "arguments": '{"path":"ok.txt"}'},
                }
            ],
            "reasoning_content": "Need to create the requested file.",
        }
    ]


def test_reasoning_content_is_omitted_when_absent():
    history = MessageHistory()

    history.add(role="assistant", content="done")

    assert history.get_formatted() == [{"role": "assistant", "content": "done"}]
