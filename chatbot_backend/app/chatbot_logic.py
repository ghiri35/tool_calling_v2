import re
from .tools import get_stock_price, get_company_news, get_weather, send_email,cancel_order
import requests
from rapidfuzz import process, fuzz
import ast
from ollama import chat

available_funcs = {
    "get_stock_price": get_stock_price,
    "get_company_news": get_company_news,
    "get_weather": get_weather,
    "send_email": send_email,
    "cancel_order": cancel_order,
    # Add more here as needed
}

def chatbot_response(message: str) -> str:

    response = chat(
        messages = [
            {
                "role": "user",
                "content": message
                },
        ],
        model = "llama3.2:latest",
        tools = [get_stock_price, get_company_news, get_weather, send_email, cancel_order],
    )

    print(response)
    message = ""
    for tool in response.message.tool_calls:
        function_to_call = available_funcs.get(tool.function.name)
        if function_to_call:
            function_output = function_to_call(**tool.function.arguments)
            print(f"Function output: {function_output}")
            message  += function_output["message"] + "."
    return message
