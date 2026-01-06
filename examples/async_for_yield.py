import asyncio

# 定义异步生成器（核心：async def + yield/async yield）
async def async_generator():
    for i in range(3):
        # 模拟异步操作（如IO、网络请求）
        await asyncio.sleep(1)
        # 异步产出值（async yield 与 yield 等价）
        yield f"值 {i}"

# 协程函数中使用 async for 遍历
async def main():
    print("开始遍历异步生成器：")
    # async for 自动迭代异步生成器，等待每个 yield 的值
    async for item in async_generator():
        print(f"获取到：{item}")

# 运行协程
asyncio.run(main())