"""工具使用示例"""
import asyncio
import os
import sys
from pathlib import Path

from src.lightweight_agent import Session, OpenAIClient
from src.lightweight_agent.tools.builtin import ReadTool, WriteTool, EditTool

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

import dotenv
dotenv.load_dotenv()

async def main():
    """演示工具使用"""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_API_BASE")
    model = os.getenv("MODEL")

    client = OpenAIClient(api_key=api_key, base_url=base_url, model=model)
    working_dir = "E:\pycharm_project\lightweight-agent\examples\my_project"
    session = Session(
        working_dir=working_dir,
        client=client,
        session_id="my-session-123"  # 自定义 ID
    )

    
    # 创建工具实例
    read_tool = ReadTool(session)
    write_tool = WriteTool(session)
    edit_tool = EditTool(session)
    
    # 示例文件路径
    test_file = Path(working_dir).resolve() / "test.txt"
    
    print("=" * 60)
    print("工具使用示例")
    print("=" * 60)
    
    # 1. Write 工具示例
    print("\n1. 使用 Write 工具创建文件...")
    content = """Hello, World!
This is a test file.
Line 3
Line 4
Line 5
"""
    result = await write_tool.execute(file_path=str(test_file), content=content)
    print(f"Write 结果: {result}")

    # # 1.1 Write 工具示例
    # print("\n1.1 使用 Write 工具创建文件 outside...")
    # content = """Hello, World!
    # This is a test file.
    # Line 3
    # Line 4
    # Line 5
    # """
    # result = await write_tool.execute(file_path=fr"E:\pycharm_project\lightweight-agent\examples\1.txt", content=content)
    # print(f"Write 结果: {result}")
    
    # 2. Read 工具示例 - 读取全部
    # print("\n2. 使用 Read 工具读取整个文件...")
    # result = await read_tool.execute(file_path=str(test_file))
    # print(f"Read 结果: {result}")

    # 3. Read 工具示例 - 读取部分行
    # print("\n3. 使用 Read 工具读取部分行 (offset=2, limit=3)...")
    # result = await read_tool.execute(
    #     file_path=str(test_file),
    #     offset=2,
    #     limit=2
    # )
    # print(f"Read 结果: {result}")

    # 4. Edit 工具示例 - 替换第一个匹配
    print("\n4. 使用 Edit 工具替换第一个匹配...")
    result = await edit_tool.execute(
        file_path=str(test_file),
        old_string="Line 3",
        new_string="Line 3 (Modified)",
        replace_all=False
    )
    # print(f"Edit 结果: {result}")
    #
    # # 5. 读取文件查看修改结果
    # print("\n5. 读取文件查看修改结果...")
    # result = await read_tool.execute(file_path=str(test_file))
    # print(f"Read 结果: {result}")
    #
    # # 6. Edit 工具示例 - 替换所有匹配
    # print("\n6. 使用 Edit 工具替换所有匹配...")
    # result = await edit_tool.execute(
    #     file_path=str(test_file),
    #     old_string="Line",
    #     new_string="Modified Line",
    #     replace_all=True
    # )
    # print(f"Edit 结果: {result}")
    #
    # # 7. 读取文件查看最终结果
    # print("\n7. 读取文件查看最终结果...")
    # result = await read_tool.execute(file_path=str(test_file))
    # print(f"Read 结果: {result}")
    #
    # print("\n" + "=" * 60)
    # print("示例完成！")
    # print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

