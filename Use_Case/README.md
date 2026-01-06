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

本目录包含两个完整示例：

1. **base_agent_example.py**: ReAct Agent 基础使用示例
2. **todo_agent_example.py**: TodoBasedAgent 使用示例

运行示例：

```bash
# 运行 ReAct Agent 示例
python base_agent_example.py

# 运行 TodoBasedAgent 示例
python todo_agent_example.py
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

