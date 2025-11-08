# script-writer

A Python script that generates a video idea, a JSON outline, and a sectioned Markdown script by chaining prompt templates through an OpenAI chat client.

## Files
- script-writer.py — main script (generates video_script.md)

## Requirements
- Python 3.9+ (or compatible)
- Installed packages referenced in the code:
  - langchain_openai
  - langchain_core

## Behavior (as implemented)
- Configures logging with:
  - logging.basicConfig(level=logging.INFO)
  - logger name: "script_writer"
- Instantiates an LLM client:
  - ChatOpenAI(model="gpt-5-nano", temperature=1, use_responses_api=True, reasoning_effort="low")
- Constructs prompt templates from strings using ChatPromptTemplate.from_template:
  - ideation_prompt_template_text — generates a single JSON object with keys: title, tools, learning_objectives
  - OUTLINE_PROMPT_TEMPLATE — requests a JSON object with "sections"
  - SCRIPT_PROMPT_TEMPLATE_TEXT — generates a JSON object with keys "section_name" and "script_markdown"
- Chains prompts to the LLM and parses outputs with StrOutputParser:
  - video_idea_chain = ideation_prompt_template | llm | StrOutputParser()
  - outline_chain = outline_prompt | llm | StrOutputParser()
  - script_chain = SCRIPT_PROMPT_TEMPLATE | llm | StrOutputParser()
- Ideation inputs used in the script:
  - max_minutes 
  - topic
  - level 
- Flow:
  1. Invoke ideation chain to produce video idea JSON and parse it with json.loads.
  2. Invoke outline chain with the video idea JSON to produce an outline JSON and parse it.
  3. Iterate over outline_json["sections"]:
     - For each section, build section_input with keys "name", "content" (JSON-stringified), and "script_so_far" (JSON-stringified accumulated parts).
     - Invoke script_chain for each section, parse the returned JSON, extract "script_markdown".
     - On empty script_markdown, raise ValueError.
     - Exceptions during section generation are logged (logger.exception) and re-raised.
     - Accumulate section markdown parts and section objects.
  4. Join accumulated parts into final_script_markdown.
  5. Write final_script_markdown to video_script.md with UTF-8 encoding.
- Logs info at several steps: the constructed chain, returned JSONs, per-section generation, and final script.

## Output
- video_script.md — written by the script (final combined script markdown)
