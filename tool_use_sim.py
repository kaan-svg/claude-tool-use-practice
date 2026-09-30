"""
Tool use simulation.

Mimics how the Claude API's tool use loop works, without needing an API key.
The "model" is a fake that picks tools by keyword, but the message flow
(tool definitions -> tool_use -> tool_result -> final answer) has the same
shape as the real API.
"""

import random

# ---------- 1. Tool definitions ----------
TOOLS = [
    {
        "name": "get_weather",
        "description": "Returns the current weather for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
    {
        "name": "get_time",
        "description": "Returns the current time for a given city.",
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name"},
            },
            "required": ["city"],
        },
    },
    
]


# ---------- 2. Real Python functions behind the tools ----------
def get_weather(city):
    
    conditions = ["sunny", "cloudy", "rainy", "windy"]
    return f"{city}: {random.randint(10, 30)}°C, {random.choice(conditions)}"
    
from datetime import datetime
def get_time(city):
    return f"{city}: {datetime.now().strftime('%H:%M')}"




TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_time": get_time,
    
    
}


# ---------- 3. Fake model ----------
KEYWORDS = {
    "get_weather": ["weather", "hava"],
    "get_time": ["time", "saat"],
}


def fake_model(messages, tools):
    last = messages[-1]

    # If the last message carries tool results, answer using them.
    if isinstance(last["content"], list):
        results = [b["content"] for b in last["content"] if b["type"] == "tool_result"]
        return {
            "stop_reason": "end_turn",
            "content": [{"type": "text", "text": "Here's what I found: " + " | ".join(results)}],
        }

    # Otherwise decide which tools to call. Only tools that are defined can be used.
    question = last["content"].lower()
    available = {t["name"] for t in tools}
    city = question.split()[-1].strip("?.!").title()  # naive: last word is the city

    calls = []
    for name, words in KEYWORDS.items():
        if name in available and any(w in question for w in words):
            calls.append({
                "type": "tool_use",
                "id": f"toolu_{len(calls) + 1}",
                "name": name,
                "input": {"city": city},
            })

    if calls:
        return {"stop_reason": "tool_use", "content": calls}
    return {
        "stop_reason": "end_turn",
        "content": [{"type": "text", "text": "I don't have a tool for that."}],
    }


# ---------- 4. The tool use loop ----------
def run(question):
    messages = [{"role": "user", "content": question}]

    while True:
        response = fake_model(messages, TOOLS)
        messages.append({"role": "assistant", "content": response["content"]})

        if response["stop_reason"] == "end_turn":
            return response["content"][0]["text"]

        # The model asked for tools: run each one and send the results back.
        results = []
        for block in response["content"]:
            if block["type"] == "tool_use":
                print(f"  -> calling {block['name']}({block['input']})")
                name=block["name"]
                if name not in TOOL_FUNCTIONS:
                    output=f"Error: Unknow tool {name}"
                else:
                    try:
                     output = TOOL_FUNCTIONS[block["name"]](**block["input"])
                    except Exception as e :
                     output = f"Error : {e}"
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block["id"],
                    "content": output,
                })
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    questions = [
        "What's the weather in Istanbul?",
        "What time is it in Ankara?",
        "What's the weather and time in Izmir?",
    ]
    for q in questions:
        print(f"User: {q}")
        print(f"Model: {run(q)}\n")
