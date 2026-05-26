import json
from pathlib import Path

import pytest

from lightweight_agent.tools.builtin.batch_edit_tool import BatchEditTool


class FakeSession:
    def __init__(self, root: Path):
        self.root = root

    def validate_path(self, path: str) -> Path:
        resolved = Path(path).resolve()
        if not str(resolved).startswith(str(self.root.resolve())):
            raise ValueError("outside root")
        return resolved


@pytest.mark.asyncio
async def test_batch_edit_returns_nearest_match_diagnostic_without_replacing(tmp_path):
    file_path = tmp_path / "paper.tex"
    original = "Intro line\nThis paper proposes a simple method.\nConclusion line\n"
    file_path.write_text(original, encoding="utf-8")

    tool = BatchEditTool(FakeSession(tmp_path))
    raw = await tool.execute(
        file_path=str(file_path),
        edits=[
            {
                "old_string": "This paper propose a simple method.",
                "new_string": "This paper proposes a robust method.",
            }
        ],
    )

    result = json.loads(raw)
    assert result["status"] == "failed"
    assert result["success_count"] == 0
    assert file_path.read_text(encoding="utf-8") == original

    diagnostic = result["results"][0]["diagnostic"]
    assert diagnostic["nearest_match_line"] == 2
    assert "This paper proposes a simple method." in diagnostic["nearest_match_context"]
    assert "Do not retry from memory" in diagnostic["hint"]


@pytest.mark.asyncio
async def test_batch_edit_success_does_not_include_diagnostic(tmp_path):
    file_path = tmp_path / "paper.tex"
    file_path.write_text("old text\n", encoding="utf-8")

    tool = BatchEditTool(FakeSession(tmp_path))
    raw = await tool.execute(
        file_path=str(file_path),
        edits=[{"old_string": "old text", "new_string": "new text"}],
    )

    result = json.loads(raw)
    assert result["status"] == "success"
    assert "diagnostic" not in result["results"][0]
    assert file_path.read_text(encoding="utf-8") == "new text\n"
