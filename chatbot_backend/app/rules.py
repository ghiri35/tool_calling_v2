from .models import Order
from ollama import chat
from datetime import datetime
import pytz, json


def is_action_allowed_with_llm(data: dict, rule_text: str, retry_count:int) -> bool:

    combined_info = {key: value.to_dict() for key, value in data.items()}
    prompt = f"""
    Act like a boolean rule-checker. Give a boolean response. Do not explain. Do not add any extra words.
    **All rules must be satisfied.**
    
    JSON data:
    {json.dumps(combined_info, indent=2)}

    Here is today's datetime:
    > {datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")} (in ISO 8601 format)

    Here are the rules:{rule_text}

    Now answer: does this order satisfy all the rule? Answer in one word.
    """
    # if retry_count > 0:
    #      prompt += "\n\nPlease reconsider carefully and verify the rule once more."
    print(f"Prompt for LLM: {prompt}")
    response = chat(
         messages=[{"role": "user", "content": prompt}],
         model="phi3:latest",
         options={
               'temperature': 0  # Makes responses deterministic
               },
         )
    answer = response["message"]["content"].strip().lower()
    print(f"LLM response: {answer}")
    return "true" in answer or "yes" in answer
