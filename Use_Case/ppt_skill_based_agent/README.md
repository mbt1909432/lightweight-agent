# PPTX Skill Agent（pip 安装版示例）

本示例展示如何在已通过 `pip install lightweight-agent` 安装的环境中，使用 `ReActAgent` 调用 `pptx` 技能并通过 Node 脚本生成 PPTX 文件。示例脚本：`ppt_skill_based_agent_example.py`。

## 运行前准备
- 安装 Python 依赖（已从 PyPI 安装即可）：`pip install lightweight-agent`
- 配置 LLM 环境变量（推荐写入项目根目录的 `.env`）：
  - `LIGHTWEIGHT_AGENT_API_KEY`（或 `LLM_API_KEY`）
  - `LIGHTWEIGHT_AGENT_API_BASE`（或 `LLM_API_BASE`，可选）
  - `LIGHTWEIGHT_AGENT_MODEL`（或 `MODEL`，默认示例用 `gpt-4o-mini`）
- 准备技能工作目录 `Use_Case/ppt_skill_based_agent/demo_skills`（已随示例复制）：
  1. 若不存在，可从 `examples/claude_skill测试/skills学习/demo_skills` 重新复制。
  2. 安装 Node 依赖（需要 Node 18+）：  
     ```bash
     cd Use_Case/ppt_skill_based_agent/demo_skills
     npm install
     # 如网络受限，可选择指定 registry：npm install --registry=https://registry.npmmirror.com
     ```
  3. 若使用 Playwright 的场景需要浏览器内核，可选执行：`npx playwright install chromium`

## 示例脚本做了什么
1) 在 `demo_skills` 目录创建 `ReActAgent`，读取可用技能。  
2) 使用 `skill` 工具加载 `pptx` 指南，按照规则生成幻灯片 HTML（如 `slides.html`）。  
3) 调用 `run_node_file` 执行 `scripts/html2pptx.js`，将 HTML 转换为 `slides.pptx`。  
4) 打印执行过程、工具调用与 Token 统计。

## 运行方式
```bash
cd Use_Case/ppt_skill_based_agent
python ppt_skill_based_agent_example.py
```

如需更换工作目录或输出文件名，可修改脚本中的 `WORKDIR` 及任务描述。调整 API Key 或模型时，更新对应的环境变量即可。*** End Patch рестораор## Test Output

