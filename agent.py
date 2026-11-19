import json
import os
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1"),
    api_key=os.environ["GROQ_API_KEY"],
)
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")


# ---------- tools: real Python functions ----------
def get_time():
    return datetime.now().strftime("%H:%M")


def calculator(expression):
    return str(eval(expression, {"__builtins__": {}}))


TOOLS_MAP = {"get_time": get_time, "calculator": calculator}


# ---------- tool schemas: what the model sees ----------
tools = [
    {"type": "function", "function": {
        "name": "get_time",
        "description": "Get the current local time",
        "parameters": {"type": "object", "properties": {}},
    }},
    {"type": "function", "function": {
        "name": "calculator",
        "description": "Evaluate a math expression like '23*47'",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    }},
]

def assistant_message_to_dict(msg):
    # convert the SDK's message object into a plain dict we can save as JSON
    return {
        "role": "assistant",
        "content": msg.content,
        "tool_calls": [
            {
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                },
            }
            for tc in msg.tool_calls
        ],
    }


# ---------- the agent loop, as a function ----------
def run_agent(question, max_steps=5, messages=None, steps=None, on_step=None):  # NEW params
    if messages is None:                                        # NEW
        messages = [{"role": "user", "content": question}]      # NEW
    if steps is None:                                           # NEW
        steps = []                                              # NEW

    for _ in range(max_steps):
        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            return {"answer": msg.content, "steps": steps, "messages": messages}

        messages.append(assistant_message_to_dict(msg))

        for tc in msg.tool_calls:
            name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            try:
                result = TOOLS_MAP[name](**args)
            except Exception as e:
                result = f"Error: {e}"

            steps.append({"tool": name, "args": args, "result": str(result)})
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })

        if on_step is not None:                                 # NEW
            on_step(messages, steps)                            # NEW

    return {"answer": "Stopped: hit max steps", "steps": steps, "messages": messages}