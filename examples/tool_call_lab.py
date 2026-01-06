# 1. 初始化客户端
import json
import os

from openai import OpenAI
import dotenv
dotenv.load_dotenv()

"""演示OpenAI流式响应"""
api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_API_BASE")
model = os.getenv("MODEL")
client = OpenAI(api_key=api_key,base_url=base_url)

# 2. 定义工具列表
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "根据城市名称查询实时天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称"},
                    "unit": {"type": "string", "description": "温度单位，默认摄氏度", "default": "celsius"}
                },
                "required": ["city"]
            }
        }
    }
]


# 3. 模拟天气查询工具（实际场景可替换为真实天气API）
def get_weather(city: str) -> dict:
    """
    模拟天气查询函数
    :param city: 城市名称
    :param unit: 温度单位
    :return: 天气信息字典
    """
    # 模拟天气数据
    mock_weather_data = {
        "北京": {"temperature": 18, "condition": "晴", "wind": "3级",},
        "上海": {"temperature": 22, "condition": "多云", "wind": "2级"},
        "广州": {"temperature": 26, "condition": "小雨", "wind": "4级"},
        "深圳": {"temperature": 25, "condition": "阴", "wind": "3级"}
    }
    # 若查询城市不存在，返回错误信息
    return mock_weather_data.get(city, {"error": f"未查询到{city}的天气信息"})

# 3. 调用模型，触发工具调用
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "查询上海，北京的天气"}],
    tools=tools,  # 传入工具定义
    tool_choice="auto"  # 让模型自主决定是否调用工具
)
# print(response)
# 4. 解析模型返回的工具调用指令
message = response.choices[0].message
#加入tool： ChatCompletion(id='chatcmpl-CtYv2zyiqcqPasybiAnBkEM0Uj1mK', choices=[Choice(finish_reason='tool_calls', index=0, message=ChatCompletionMessage(content=None, role='assistant', function_call=None, tool_calls=[ChatCompletionMessageToolCall(id='call_brTrddSej5iQKsbuQfUEUPtl', function=Function(arguments='{"city":"上海"}', name='get_weather', parameters=None), type='function')]))], created=1767358304, model='gpt-4o', object='chat.completion', system_fingerprint='fp_4a331a0222', usage=CompletionUsage(completion_tokens=15, prompt_tokens=67, total_tokens=82, prompt_tokens_details={'cached_tokens': 0, 'audio_tokens': 0}, completion_tokens_details={'audio_tokens': 0, 'reasoning_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}, input_tokens=0, output_tokens=0, input_tokens_details=None))
#无加入tool ChatCompletion(id='chatcmpl-CtYvty3ITsXpOMmcGg73ZQLu5D2WI', choices=[Choice(finish_reason='stop', index=0, message=ChatCompletionMessage(content='对不起，我无法提供当天的实时天气信息。你可以通过天气预报网站或者天气应用来查询上海今天的天气。常用的方式包括访问“中国天气网”、“中央气象台”或使用手机上的天气应用。', role='assistant', function_call=None, tool_calls=None))], created=1767358358, model='gpt-4o', object='chat.completion', system_fingerprint='fp_4a331a0222', usage=CompletionUsage(completion_tokens=52, prompt_tokens=12, total_tokens=64, prompt_tokens_details={'cached_tokens': 0, 'audio_tokens': 0}, completion_tokens_details={'audio_tokens': 0, 'reasoning_tokens': 0, 'accepted_prediction_tokens': 0, 'rejected_prediction_tokens': 0}, input_tokens=0, output_tokens=0, input_tokens_details=None))
#都有response.choices[0].message.tool_calls 只是看是否返回None
print(message)
tool_calls = message.tool_calls  # 模型生成的工具调用列表（可能有多个）
print(tool_calls)
if tool_calls:
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        tool_call_id=tool_call.id
        print(f"模型要求调用工具：{function_name}")
        print(f"调用参数：{function_args}")  # 输出：{"city":"上海","unit":"celsius"}
        print(f"tool call id:{tool_call_id}")
    # 提取第一个工具调用的参数
        # 执行工具调用（这里调用本地模拟的get_weather函数）
        if function_name == "get_weather":
            weather_result = get_weather(**function_args)
            print(weather_result)

            # 7. 构造工具调用结果消息，回填到对话历史
            # messages.append({
            #     "role": "tool",
            #     "content": json.dumps(weather_results, ensure_ascii=False),
            #     "tool_call_id": tool_call_id
            # })
            """
            调用 API 时会直接报错，因为 OpenAI API 仅接收 JSON 可序列化的基础类型（字符串、数字、布尔、None），content 字段不支持嵌套的列表 / 字典类型。
json.dumps() 的核心作用
把 Python 中的「列表 / 字典」等复杂数据结构，转换成 JSON 格式的字符串（满足 API 格式要求），同时保证：
数据结构不丢失（列表、嵌套字典能完整保留）；
跨语言 / 跨系统的解析一致性（模型能准确解析结构化数据）；
特殊字符（如中文、空格、符号）的正确编码
            """
else:
    print(message.content)