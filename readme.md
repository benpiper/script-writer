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

## Features

- **CLI Arguments**: Easily customize topic, domain, level, and model via command-line flags.
- **Interactive Title Selection**: Choose from 6 generated title options (Original, Contrarian, Descriptive, Problem/Solution, How-To, Curiosity) with a 10-second timeout.
- **Organized Output**: Each run creates a unique, timestamped subfolder in the `output/` directory containing all generated artifacts (JSON ideas, outlines, scripts).
- **Robust Error Handling**: The script gracefully handles errors, including network issues and invalid generation, with automatic retries and clear error messages.
- **SEO-Friendly Naming**: Output folders and files use clean, slugified names.

## Output

All generated files are saved in `output/<timestamp>_<topic-slug>/`.
Artifacts include:
1. `1_idea.json`: Initial video idea.
2. `2_idea_qa.json`: Refined idea after QA.
3. `3_outline.json`: Generated video outline.
4. `4_outline_qa.json`: Outline QA report.
5. `5_outline_final.json`: Finalized outline.
6. `6_script.md`: First draft of the script.
7. `7_script_qa.json`: Script QA report.
8. `8_script_final.md`: Final polished script.

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