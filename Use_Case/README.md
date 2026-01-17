# Lightweight Agent 使用指南

本文档介绍如何使用 `lightweight-agent` 包来构建智能代理（Agent）应用。

## 安装

```bash
pip install lightweight-agent
```

## 环境配置

在使用之前，需要配置 LLM API 密钥。创建 `.env` 文件或设置环境变量：

```bash
# OpenAI 配置
LLM_API_KEY=your-openai-api-key
LLM_API_BASE=https://api.openai.com/v1
MODEL=gpt-4

# 或者使用 Anthropic
# LLM_API_KEY=your-anthropic-api-key
# LLM_API_BASE=https://api.anthropic.com
# MODEL=claude-3-sonnet-20240229
```

## 快速开始

### 1. ReAct Agent（基础代理）

`ReActAgent` 是一个基于 ReAct（Reasoning and Acting）模式的智能代理，可以自主调用工具完成任务。

#### 基本使用

```python
import asyncio
import os
from pathlib import Path
from lightweight_agent import OpenAIClient, ReActAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage
)
import dotenv

dotenv.load_dotenv()

async def main():
    # 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "agent_work"
    work_dir.mkdir(exist_ok=True)
    
    # 创建 ReAct Agent
    agent = ReActAgent(
        client=client,
        working_dir=str(work_dir),
    )
    
    # 运行任务
    async for message in agent.run("创建一个文本文件，然后修改它"):
        message_type, *content = message
        
        if message_type == AgentMessageType.SYSTEM:
            print_system_prompt(content[0])
        elif message_type == AgentMessageType.USER:
            print_user_message(content[0])
        elif message_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print_assistant_message(content[0], content[1], content[2])
        elif message_type == AgentMessageType.ASSISTANT:
            print_assistant_message(content=content[0], token_usage=content[1])
            print_token_usage(content[2])
        elif message_type == AgentMessageType.TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.MAXIMUM:
            print_token_usage(content[1])
            print(content[0])

if __name__ == "__main__":
    asyncio.run(main())
```

#### 内置工具

`ReActAgent` 默认包含以下工具：

- **read_file**: 读取文件内容
- **write_file**: 写入文件
- **edit_file**: 编辑文件（支持搜索替换）
- **list_directory**: 列出目录内容
- **run_python_file**: 运行 Python 文件

#### 自定义工具

你可以注册自定义工具：

```python
from lightweight_agent.tools.base import Tool
from lightweight_agent.tools.registry import ToolRegistry

class CustomTool(Tool):
    @property
    def name(self) -> str:
        return "custom_tool"
    
    @property
    def description(self) -> str:
        return "A custom tool description"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "Parameter description"
                }
            },
            "required": ["param1"]
        }
    
    async def execute(self, **kwargs) -> str:
        # 实现工具逻辑
        return "Tool execution result"

# 注册工具
agent.register_tool(CustomTool(agent.session))
```

#### 路径权限控制

可以限制 Agent 的文件访问权限：

```python
agent = ReActAgent(
    client=client,
    working_dir=str(work_dir),
    allowed_paths=["/path/to/allowed"],  # 允许访问的路径
    blocked_paths=["/path/to/blocked"],  # 禁止访问的路径
)
```

### 2. TodoBasedAgent（TODO 列表代理）

`TodoBasedAgent` 继承自 `ReActAgent`，增加了 TODO 列表管理功能，适合需要任务规划和跟踪的场景。

#### 基本使用

```python
import asyncio
import os
from pathlib import Path
from lightweight_agent import OpenAIClient, TodoBasedAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage
)
import dotenv

dotenv.load_dotenv()

async def main():
    # 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "todo_agent_work"
    work_dir.mkdir(exist_ok=True)
    
    # 创建 TodoBasedAgent
    agent = TodoBasedAgent(
        client=client,
        working_dir=str(work_dir),
    )
    
    # 运行任务
    async for message in agent.run("使用 matplotlib 画一个随机图形"):
        message_type, *content = message
        
        if message_type == AgentMessageType.SYSTEM:
            print_system_prompt(content[0])
        elif message_type == AgentMessageType.USER:
            print_user_message(content[0])
        elif message_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print_assistant_message(content[0], content[1], content[2])
        elif message_type == AgentMessageType.ASSISTANT:
            print_assistant_message(content=content[0], token_usage=content[1])
            print_token_usage(content[2])
        elif message_type == AgentMessageType.TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.MAXIMUM:
            print_token_usage(content[1])
            print(content[0])
    
    # 查看 TODO 列表摘要
    print("\n=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")
    
    # 查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")

if __name__ == "__main__":
    asyncio.run(main())
```

#### TODO 工具

`TodoBasedAgent` 额外包含以下工具：

- **create_todo_list**: 创建 TODO 列表
- **update_todo_status**: 更新 TODO 项状态
- **save_important_artifacts**: 保存重要产物

#### TODO 管理 API

```python
# 获取 TODO 列表
todo_list = agent.get_todo_list()

# 检查是否所有 TODO 已完成
all_completed = agent.is_all_todos_completed()

# 获取 TODO 摘要
summary = agent.get_todo_summary()
# 返回: {
#     "total": 5,
#     "pending": 1,
#     "in_progress": 1,
#     "completed": 3,
#     "failed": 0,
#     "all_completed": False
# }

# 获取保存的产物
artifacts = agent.get_artifacts()

# 获取交付摘要
delivery_summary = agent.get_delivery_summary()
```

### 3. CitationAgent（引用代理）

`CitationAgent` 继承自 `TodoBasedAgent`，专门用于将 BibTeX 引用插入到 LaTeX 文档中。它自动提取 BibTeX 条目并在语义合适的位置插入引用。

#### 基本使用

```python
import asyncio
import os
from pathlib import Path
from lightweight_agent import OpenAIClient
from lightweight_agent.agent.extension.citation_agent import CitationAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage
)
import dotenv

dotenv.load_dotenv()

async def main():
    # 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "citation_agent_work"
    work_dir.mkdir(exist_ok=True)
    
    # 创建 CitationAgent
    agent = CitationAgent(
        client=client,
        working_dir=str(work_dir)
    )
    
    # 运行任务
    # 工作目录应包含：
    # - paper.tex (LaTeX 文档)
    # - references.txt 或 references.bib (BibTeX 条目源文件)
    async for message in agent.run("从 references.txt 提取所有 BibTeX 条目并插入到 paper.tex"):
        message_type, *content = message
        
        if message_type == AgentMessageType.SYSTEM:
            print_system_prompt(content[0])
        elif message_type == AgentMessageType.USER:
            print_user_message(content[0])
        elif message_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print_assistant_message(content[0], content[1], content[2])
        elif message_type == AgentMessageType.ASSISTANT:
            print_assistant_message(content=content[0], token_usage=content[1])
            print_token_usage(content[2])
        elif message_type == AgentMessageType.TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.MAXIMUM:
            print_token_usage(content[1])
            print(content[0])
    
    # 查看 TODO 列表摘要
    print("\n=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")
    
    # 查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 引用工具

`CitationAgent` 额外包含以下工具：

- **bibtex_extract**: 从文本文件中提取 BibTeX 条目
- **bibtex_insert**: 将 BibTeX 条目插入到 LaTeX 文档的合适位置
- **bibtex_save**: 保存提取的 BibTeX 条目到文件

#### 工作流程

CitationAgent 会自动执行以下步骤：

1. **创建 TODO 列表**：规划任务步骤
2. **探索目录**：使用 `list_directory` 查看工作目录
3. **读取文件**：读取所有相关文件（.tex, .bib, .txt）
4. **提取 BibTeX 条目**：使用 `bibtex_extract` 从源文件提取引用
5. **插入引用**：
   - 手动阶段：使用 `edit_file` 在合适位置插入引用
   - 自动阶段：使用 `bibtex_insert` 自动分发和格式化引用
6. **保存产物**：保存修改后的 LaTeX 文件

#### 特性

- **自动 TODO 管理**：基于 TODO 列表的系统化工作流程
- **两阶段引用插入**：手动定位 + 自动分发
- **文件命名保护**：保存时保留原始文件名
- **完整 BibTeX 处理**：提取并插入所有 BibTeX 条目

### 4. FigureAgent（图片代理）

`FigureAgent` 继承自 `TodoBasedAgent`，专门用于将图片插入到 LaTeX 文档中。它能够自动扫描图片目录，根据图片类型和描述信息，在语义合适的位置插入图片。

#### 基本使用

```python
import asyncio
import os
from pathlib import Path
from lightweight_agent import OpenAIClient
from lightweight_agent.agent.extension.figure_agent import FigureAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage,
)
import dotenv

dotenv.load_dotenv()

async def main():
    # 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "figure_agent_work"
    work_dir.mkdir(exist_ok=True)
    
    # 创建 FigureAgent
    agent = FigureAgent(
        client=client,
        working_dir=str(work_dir),
    )
    
    # 运行任务
    task = (
        "扫描图片目录中的所有图片，并将它们插入到 LaTeX 文档的语义合适位置。"
        "对于 main_result 和 ablation 图片，如果存在 planning_results.json，使用其中的精确插入指令。"
        "对于 motivation 和 algorithm 图片，读取对应的 prompt.txt 文件获取图片描述，然后基于描述生成合适的标题并插入到合适的位置（motivation 插入 Introduction，algorithm 插入 Methodology）。"
        "确保所有图片都有合适的标题和标签。"
    )
    
    async for message in agent.run(task, max_iterations=300):
        message_type, *content = message
        
        if message_type == AgentMessageType.SYSTEM:
            print_system_prompt(content[0])
        elif message_type == AgentMessageType.USER:
            print_user_message(content[0])
        elif message_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print_assistant_message(content[0], content[1], content[2])
        elif message_type == AgentMessageType.ASSISTANT:
            print_assistant_message(content=content[0], token_usage=content[1])
            print_token_usage(content[2])
        elif message_type == AgentMessageType.TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.MAXIMUM:
            print_token_usage(content[1])
            print(content[0])
    
    # 查看 TODO 列表摘要
    print("\n=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")
    
    # 查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 图片工具

`FigureAgent` 额外包含以下工具：

- **figure_insert**: 将图片插入到 LaTeX 文档的合适位置
- **figure_scan**: 扫描图片目录，识别图片类型和描述信息

#### 工作流程

FigureAgent 会自动执行以下步骤：

1. **创建 TODO 列表**：规划图片插入任务
2. **扫描图片目录**：使用 `figure_scan` 识别所有图片及其类型
3. **读取相关文件**：
   - 对于 main_result/ablation 图片：读取 `planning_results.json` 获取精确插入指令
   - 对于 motivation/algorithm 图片：读取对应的 `prompt.txt` 获取图片描述
4. **插入图片**：使用 `figure_insert` 在语义合适的位置插入图片
5. **生成标题和标签**：根据图片描述自动生成合适的标题和标签
6. **保存产物**：保存修改后的 LaTeX 文件

#### 特性

- **智能图片分类**：自动识别 main_result、ablation、motivation、algorithm 等图片类型
- **语义位置匹配**：根据图片类型自动选择插入位置（Introduction、Methodology、Results 等）
- **描述信息读取**：从 `prompt.txt` 文件读取图片描述，生成合适的标题
- **精确插入指令**：支持从 `planning_results.json` 读取精确的插入位置指令

### 5. PolishAgent（润色代理）

`PolishAgent` 继承自 `TodoBasedAgent`，专门用于对论文草稿进行「打样级」润色与结构自洽检查。它能够删除 TODO 和占位符，统一语气，检查数值一致性，并确保全文逻辑自洽。

#### 基本使用

```python
import asyncio
import os
from pathlib import Path
from lightweight_agent import OpenAIClient
from lightweight_agent.agent.extension.polish_agent import PolishAgent
from lightweight_agent.agent.react_agent import AgentMessageType
from lightweight_agent.agent.pretty_print import (
    print_system_prompt,
    print_user_message,
    print_assistant_message,
    print_tool_result,
    print_token_usage,
)
import dotenv

dotenv.load_dotenv()

async def main():
    # 初始化客户端
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    
    # 创建工作目录
    work_dir = Path(__file__).parent / "polish_agent_work"
    work_dir.mkdir(exist_ok=True)
    
    # 创建 PolishAgent
    agent = PolishAgent(
        client=client,
        working_dir=str(work_dir),
    )
    
    # 运行任务
    task = (
        "在当前工作目录中，找到论文主文件，对论文进行打样级润色："
        "删除所有 TODO / 占位符 / 开发过程注释，"
        "统一语气为正式学术写作风格，"
        "检查摘要、结论与正文描述中的数值是否与表格/图表完全一致，"
        "并根据当前示例数据调整文字描述，使全文结构完整、逻辑自洽。文章内容必须和标题相符"
    )
    
    async for message in agent.run(task, max_iterations=300):
        message_type, *content = message
        
        if message_type == AgentMessageType.SYSTEM:
            print_system_prompt(content[0])
        elif message_type == AgentMessageType.USER:
            print_user_message(content[0])
        elif message_type == AgentMessageType.ASSISTANT_WITH_TOOL_CALL:
            print_assistant_message(content[0], content[1], content[2])
        elif message_type == AgentMessageType.ASSISTANT:
            print_assistant_message(content=content[0], token_usage=content[1])
            print_token_usage(content[2])
        elif message_type == AgentMessageType.TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.ERROR_TOOL_RESPONSE:
            print_tool_result(content[0], content[1])
        elif message_type == AgentMessageType.MAXIMUM:
            print_token_usage(content[1])
            print(content[0])
    
    # 查看 TODO 列表摘要
    print("\n=== TODO 列表摘要 ===")
    summary = agent.get_todo_summary()
    print(f"总计: {summary['total']}, "
          f"待处理: {summary['pending']}, "
          f"进行中: {summary['in_progress']}, "
          f"已完成: {summary['completed']}, "
          f"失败: {summary['failed']}")
    
    # 查看保存的产物
    print("\n=== 保存的产物 ===")
    artifacts = agent.get_artifacts()
    if artifacts:
        for artifact in artifacts:
            print(f"- {artifact.get('name', 'Unknown')}: {artifact.get('description', '')}")
    else:
        print("没有保存的产物")

if __name__ == "__main__":
    asyncio.run(main())
```

#### 润色工具

`PolishAgent` 额外包含以下工具：

- **polish_document**: 对文档进行打样级润色
- **check_consistency**: 检查文档中的数值一致性和逻辑自洽性

#### 工作流程

PolishAgent 会自动执行以下步骤：

1. **创建 TODO 列表**：规划润色任务步骤
2. **定位论文主文件**：在工作目录中查找 LaTeX 或 Markdown 主文件
3. **读取文档**：读取完整的论文内容
4. **删除占位符**：删除所有 TODO、占位符和开发过程注释
5. **统一语气**：将文档语气统一为正式学术写作风格
6. **检查一致性**：
   - 检查摘要、结论与正文中的数值是否与表格/图表一致
   - 检查全文逻辑自洽性
   - 确保文章内容与标题相符
7. **调整描述**：根据实际数据调整文字描述
8. **保存产物**：保存润色后的文档

#### 特性

- **打样级润色**：删除所有开发痕迹，统一为正式学术风格
- **数值一致性检查**：自动检查摘要、结论与正文中的数值是否与表格/图表一致
- **逻辑自洽性检查**：确保全文逻辑连贯，内容与标题相符
- **智能描述调整**：根据实际数据自动调整文字描述

## 消息类型

Agent 的 `run()` 方法返回一个异步生成器，产生不同类型的消息：

- **AgentMessageType.SYSTEM**: 系统提示消息
- **AgentMessageType.USER**: 用户输入消息
- **AgentMessageType.ASSISTANT**: 助手回复（无工具调用）
- **AgentMessageType.ASSISTANT_WITH_TOOL_CALL**: 助手回复（包含工具调用）
- **AgentMessageType.TOOL_RESPONSE**: 工具执行结果
- **AgentMessageType.ERROR_TOOL_RESPONSE**: 工具执行错误
- **AgentMessageType.TOKEN**: Token 使用统计
- **AgentMessageType.MAXIMUM**: 达到最大迭代次数

## 高级配置

### 自定义系统提示

```python
agent = ReActAgent(
    client=client,
    working_dir=str(work_dir),
    system_prompt="你是一个专业的 Python 开发助手..."
)
```

### 设置最大迭代次数

```python
async for message in agent.run("复杂任务", max_iterations=50):
    # 处理消息
    pass
```

### 使用 Anthropic 客户端

```python
from lightweight_agent import AnthropicClient

client = AnthropicClient(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    model="claude-3-sonnet-20240229"
)

agent = ReActAgent(client=client, working_dir=str(work_dir))
```

## 完整示例

本目录包含五个完整示例：

1. **base_agent_example.py**: ReAct Agent 基础使用示例
2. **todo_agent_example.py**: TodoBasedAgent 使用示例
3. **citation_agent_example.py**: CitationAgent 使用示例
4. **figure_agent_example.py**: FigureAgent 使用示例
5. **polish_agent_example.py**: PolishAgent 使用示例

运行示例：

```bash
# 运行 ReAct Agent 示例
python base_agent_example.py

# 运行 TodoBasedAgent 示例
python todo_agent_example.py

# 运行 CitationAgent 示例
python citation_agent_example.py

# 运行 FigureAgent 示例
python figure_agent_example.py

# 运行 PolishAgent 示例
python polish_agent_example.py
```

## 注意事项

1. **工作目录**: `working_dir` 必须是绝对路径
2. **路径权限**: Agent 只能访问 `working_dir` 和 `allowed_paths` 中的文件
3. **迭代限制**: 默认最大迭代次数为 20，可通过 `max_iterations` 参数调整
4. **异步操作**: 所有 Agent 操作都是异步的，需要使用 `async/await`
5. **环境变量**: 建议使用 `.env` 文件管理 API 密钥

## 更多信息

- 查看项目主 README 了解完整功能
- 查看源代码了解实现细节
- 查看 `tools/builtin/` 了解内置工具实现

