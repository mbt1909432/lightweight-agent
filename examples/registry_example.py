"""ToolRegistry 使用示例"""
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any

from src.lightweight_agent import Session, OpenAIClient
from src.lightweight_agent.tools.registry import ToolRegistry
from src.lightweight_agent.tools.base import Tool
from src.lightweight_agent.tools.builtin import ReadTool, WriteTool, ListDirTool

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import dotenv
dotenv.load_dotenv()


# 创建一个自定义工具示例
class EchoTool(Tool):
    """简单的回显工具，用于演示自定义工具"""
    
    @property
    def name(self) -> str:
        return "echo"
    
    @property
    def description(self) -> str:
        return "Echo back the input message. Useful for testing and demonstration."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "The message to echo back"
                }
            },
            "required": ["message"]
        }
    
    async def execute(self, **kwargs) -> str:
        """执行回显"""
        message = kwargs.get("message", "")
        return json.dumps({
            "echoed_message": message,
            "length": len(message)
        }, ensure_ascii=False)


async def main():
    """演示 ToolRegistry 的使用"""
    print("=" * 60)
    print("ToolRegistry 使用示例")
    print("=" * 60)
    
    # 初始化客户端和会话
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")
    
    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    working_dir = str(Path(__file__).parent / "my_project")
    session = Session(
        working_dir=working_dir,
        client=client,
        session_id="registry-example-session"
    )
    
    # 1. 创建 ToolRegistry 实例
    print("\n1. 创建 ToolRegistry 实例")
    print("-" * 60)
    registry = ToolRegistry()
    print(f"初始注册表大小: {len(registry)}")
    
    # 2. 注册工具
    print("\n2. 注册工具")
    print("-" * 60)
    
    # 注册内置工具
    read_tool = ReadTool(session)
    write_tool = WriteTool(session)
    list_dir_tool = ListDirTool(session)
    
    registry.register(read_tool)
    print(f"✓ 注册工具: {read_tool.name}")
    
    registry.register(write_tool)
    print(f"✓ 注册工具: {write_tool.name}")
    
    registry.register(list_dir_tool)
    print(f"✓ 注册工具: {list_dir_tool.name}")
    
    # 注册自定义工具
    echo_tool = EchoTool(session)
    registry.register(echo_tool)
    print(f"✓ 注册自定义工具: {echo_tool.name}")
    
    print(f"\n当前注册表大小: {len(registry)}")

    print(registry.get_schemas())
    
    # 3. 检查工具是否存在
    # print("\n3. 检查工具是否存在")
    # print("-" * 60)
    # tools_to_check = ["Read", "Write", "Echo", "NonExistent"]
    # for tool_name in tools_to_check:
    #     exists = tool_name in registry
    #     print(f"工具 '{tool_name}': {'存在' if exists else '不存在'}")
    # # 4. 获取工具
    print("\n4. 获取工具")
    print("-" * 60)
    tool = registry.get("Read")
    if tool:
        print(f"✓ 获取到工具: {tool.name}")
        print(f"  描述: {tool.description}")


    tool = registry.get("NonExistent")
    if tool is None:
        print("✓ 不存在的工具返回 None")
    #
    # # 5. 获取所有工具
    # print("\n5. 获取所有工具")
    # print("-" * 60)
    # all_tools = registry.get_all()
    # print(f"已注册的工具列表 ({len(all_tools)} 个):")
    # for tool in all_tools:
    #     print(f"  - {tool.name}: {tool.description[:50]}...")
    #
    # # 6. 获取工具 schemas（用于 LLM function calling）
    # print("\n6. 获取工具 schemas")
    # print("-" * 60)
    # schemas = registry.get_schemas()
    # print(f"工具 schemas 数量: {len(schemas)}")
    # print("\n第一个工具的 schema:")
    # if schemas:
    #     first_schema = schemas[0]
    #     print(json.dumps(first_schema, indent=2, ensure_ascii=False))
    #
    # # 7. 测试工具执行
    # print("\n7. 测试工具执行")
    # print("-" * 60)
    #
    # # 测试 Echo 工具
    # echo_result = await echo_tool.execute(message="Hello, ToolRegistry!")
    # print(f"Echo 工具执行结果: {echo_result}")
    #
    # # 测试 Write 工具
    # test_file = Path(working_dir) / "registry_test.txt"
    # write_result = await write_tool.execute(
    #     file_path=str(test_file),
    #     content="This file was created by ToolRegistry example.\nLine 2\nLine 3"
    # )
    # print(f"Write 工具执行结果: {write_result}")
    #
    # # 测试 Read 工具
    # read_result = await read_tool.execute(file_path=str(test_file))
    # print(f"Read 工具执行结果: {read_result}")
    #
    # # 8. 取消注册工具
    # print("\n8. 取消注册工具")
    # print("-" * 60)
    # print(f"取消注册前，注册表大小: {len(registry)}")
    # registry.unregister("Echo")
    # print(f"✓ 已取消注册工具: Echo")
    # print(f"取消注册后，注册表大小: {len(registry)}")
    #
    # # 验证工具已被移除
    # if "Echo" not in registry:
    #     print("✓ 验证: Echo 工具已不在注册表中")
    #
    # # 9. 尝试注册重复的工具（应该抛出异常）
    # print("\n9. 尝试注册重复的工具")
    # print("-" * 60)
    # try:
    #     duplicate_read = ReadTool(session)
    #     registry.register(duplicate_read)
    #     print("✗ 错误: 应该抛出异常但没有")
    # except ValueError as e:
    #     print(f"✓ 正确捕获异常: {e}")
    #
    # # 10. 最终状态
    # print("\n10. 最终状态")
    # print("-" * 60)
    # print(f"最终注册表大小: {len(registry)}")
    # print("最终工具列表:")
    # for tool in registry.get_all():
    #     print(f"  - {tool.name}")
    #
    # print("\n" + "=" * 60)
    # print("示例完成！")
    # print("=" * 60)



if __name__ == "__main__":
    asyncio.run(main())

