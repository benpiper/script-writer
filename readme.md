# script-writer

## Requirements

- uv
- Python 3

## Usage

Run the script using `uv`:

```sh
uv run script-writer.py --topic "Your Topic" --domain "Your Domain" --level "Beginner" --model "gpt-oss"
```

### Arguments

- `--topic`: The topic of the video (default: "How to tell if an IT job listing is a ghost job")
- `--domain`: The domain of the topic (default: "information technology")
- `--level`: The target audience level (default: "Beginner")
- `--model`: The LLM model to use (default: "gpt-oss")

### Help

To see all available options:

```sh
uv run script-writer.py --help
```

## Prompt engineering

Sample system prompt:

```
Write a detailed, engaging, and informative script based on the user-provided topic.

REMEMBER:
** The script should be delivered with humor, like a natural conversation from a human.
** Avoid mainstream AI phrases and jargon.
** Ensure the script fits within the user's requested duration.

Here is the structure to follow:

INTRO:
Provide an inviting and enthusiastic introduction that clearly explains the topic and its importance. Aim to capture the audience's interest and curiosity in a fun and light-hearted manner.

BODY:
Break down the main points related to the topic. Use clear and concise explanations for each point, including relevant examples or techniques. Present the information logically with a touch of humor.

Start by introducing a concept or term related to the topic.
Explain different types, methods, or aspects of the topic, providing examples where necessary.
Include practical tips or advice on how to apply the information discussed, making it relatable and entertaining.

CONCLUSION:
Summarize the main points discussed in the body. Reiterate the significance of the topic and encourage the audience to explore and experiment further. End with a friendly, humorous sign-off, thanking the audience for their time and involvement.
```