- 添加anthropic的version
- 添加其他todotool等tool
- 备注转英文
- 打包
- prompt修改: 先读取本地目录 然后再做todo 然后开始执行 每次完成勾选 当todo完成时 使用save important artifact后任务结束 
- 依赖管理就不需要了。。。。直接事先装好

- run可能需要改成yield 然后pretty print可能需要在用户那端去打印？？？ 不然后续埋点难做



1添加工具 读取文件然后执行python脚本还有依赖管理         @tool(
            name="run_python_file",
            description="Execute a Python script from a file in the working directory",
            input_schema={
                "type": "object",
                "properties": {
                    "file": {
                        "type": "string",
                        "description": "The path to the Python file to execute (relative to working directory)"
                    }
                },
                "required": ["file"]
            }
        )   2还有添加个list_dir工具 列出目录下的所有文件 不递归 这两个都给base的react agent注册