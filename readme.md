# script-writer

## Requirements

- uv
- Python 3

## Usage

The script writer workflow is split into two parts: title generation and script creation.

---

### Step 1: Generate Video Idea

Generate a comprehensive video idea (including titles, hook, tools, and objectives) and save it to a file.

```sh
uv run generate_titles.py --topic "Your Topic" --save idea.json
```

**Output**: Generates `idea.json` with a chosen title (defaulting to the first suggestion) and other required fields.

### Step 2: Edit Idea (Optional)

Review and edit the `idea.json` file if you want to select a different title or tweak the content.

```json
{
  "title": "Selected Title",
  "topic": "Your Topic",
  ...
}
```

### Step 3: Generate Script

Run the script writer using your `idea.json` file as input.

```sh
uv run script-writer.py --input-file path/to/idea.json
```

---

## Features

- **Split Workflow**: Focused tools for brainstorming vs. execution.
- **File-Based Input**: Full control over the video idea before script generation starts.
- **Autonomous Research**: (Optional) Uses LangGraph to research the topic before outlining.
- **Organized Output**: Each run creates a unique, timestamped subfolder in `output/` containing all artifacts.
- **Robust Error Handling**: Automatic retries for network and generation issues.

## Output

All generated files are saved in `output/<timestamp>_<title-slug>/`.
Artifacts include:
1. `1_idea.json`: Copy of the input idea.
2. `3_outline.json`: Generated video outline.
3. `4_outline_qa.json`: Outline QA report.
4. `5_outline_final.json`: Finalized outline.
5. `6_script.md`: First draft of the script with code snippets.
6. `7_script_qa.json`: Script QA report.