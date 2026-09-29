# Claude Tool Use Practice

A small Python simulation of how **tool use** works in the Claude API, built to understand the request/response loop before connecting to the real API. No API key needed.

## How It Works

1. **Define tools** – Each tool is described with a name, a description and a JSON Schema for its inputs. The model reads the description to decide when to use it.
2. **Model requests a tool** – Instead of answering directly, the model returns a `tool_use` block with the tool name and its inputs (`stop_reason == "tool_use"`).
3. **Run the function** – The program calls the matching Python function and sends the output back as a `tool_result`.
4. **Loop until done** – This repeats until the model returns a final answer (`stop_reason == "end_turn"`). One question can trigger several tool calls.

In this project the model is a keyword-based fake, so the focus stays on the message flow rather than the AI itself.

## Tools

| Tool | Description |
|------|-------------|
| `get_weather` | Returns a (simulated) weather report for a city |
| `get_time` | Returns the current time |

## Run

```bash
python tool_use_sim.py
```

Example output:

```
User: What's the weather and time in Izmir?
  -> calling get_weather({'city': 'Izmir'})
  -> calling get_time({'city': 'Izmir'})
Model: Here's what I found: Izmir: 22°C, sunny | 14:35
```

## Next Steps

- [ ] Replace the fake model with a real Claude API call using the `anthropic` Python SDK
- [ ] Load the API key from a `.env` file (never commit it)
- [ ] Add a tool that calls a real external API

## Resources

- [anthropics/courses](https://github.com/anthropics/courses)
- [Claude tool use docs](https://docs.claude.com/en/docs/agents-and-tools/tool-use/overview)
