import os
import json
import logging
import time
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("script_writer")

llm = ChatOpenAI(model="gpt-5-nano", temperature=1,
                 use_responses_api=True, reasoning_effort="low")

# --- Prompt: Generate Video Idea ---

IDEATION_PROMPT_TEMPLATE_TEXT = """
        Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level. Do not output this checklist
        Generate an idea for a video that can be quickly recorded and published, guided by the following requirements:
        - Inputs:
        - Topic: {topic} (string)
        - Audience level: {level} (string)
        - Maximum Length: {max_minutes} (positive integer; video must be less than or equal to this number of minutes)
        - Requirements:
        - The title, list of tools, and learning objectives must all be achievable within {max_minutes} minutes.
        - Learning objectives should be specific
        - The video idea should avoid generic or overly common topics (e.g., chatbots).
        - Be specific and decisive in output: Do not use "or" in the lists of tools or learning objectives.

        - Output Format
        Return your answer as valid JSON using the following format:

            {{
                "title": "<string: SEO-optimized title of the video>",
                "tools": ["Tool or framework 1", "Tool or framework 2"],
                "learning_objectives": ["Learning objective 1", "Learning objective 2"]
            }}

        - Output Constraints:
        - Only return a single JSON object per response.

          After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
          If validation fails, self-correct and return the correct JSON error object.

          - Example output
            {{
                "title": "How to write a Hello World program in Python",
                "tools": ["Python", "VS Code"],
                "learning_objectives": ["Write a program in Python", "Run a Python program", "Understand Python syntax"]
            }}
        """

IDEATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    IDEATION_PROMPT_TEMPLATE_TEXT)

# Construct the ideation chain: prompt > LLM > string
video_idea_chain = IDEATION_PROMPT_TEMPLATE | llm | StrOutputParser()
# logger.info("Chain:")
# logger.info(video_idea_chain)

# Invoke the ideation chain
MAX_MINUTES = 30
TOPIC = "Creating a simple React app using vite and functional components"
LEVEL = "Beginner"
video_idea = video_idea_chain.invoke(
    {"max_minutes": MAX_MINUTES, "topic": TOPIC, "level": LEVEL})

# Convert result to JSON
video_idea_json = json.loads(video_idea)
logger.info("Video idea JSON")
logger.info(video_idea_json)

# --- Prompt: Generate Outline ---

OUTLINE_PROMPT_TEMPLATE = """
        Begin with a concise checklist (3-7 bullets) of the main planning and sequencing steps you will follow before creating the outline. Do not output this checklist
        Create a comprehensive outline for a video using the structured input provided.

        Input JSON structure:
        ```
        {{
            "title": "{title}",
            "tools": {tools},
            "learning_objectives": {learning_objectives}
        }}
        ```

        Guidelines:
        - Stay strictly within the scope defined by the title, tools, and learning objectives.
        - Exclude self-paced exercises; all demonstrations should be incorporated within the video outline.
        - Carefully design the outline to ensure it fully addresses, but does not go beyond, the content indicated in the title.
        - Arrange all sections and demonstration steps in a clear, logical sequence.
        - For the final section, refrain from including next steps, recommendations, or external/additional resources.
        - Do not include a wrap-up , summary, or recap

        If 'title', 'tools', or 'learning_objectives' fields are missing or not the correct type, respond with the following JSON object:
        ```
        {{"error": "Missing or invalid input fields."}}
        ```

        After outlining, validate that each section directly supports the provided title and learning objectives, and confirm that all demonstrations are video-based and in logical order.
        If any guideline is not fully met, correct the outline before producing your final output.

        # Output Format
        - Return a JSON object structured as:
        ```
        {{
            "sections": [
            {{ "name": "<string>", "content": [<string>, ...] }}
            ]
        }}
        ```
        - 'sections' should be an array of section objects.
        - Each section object includes:
        - 'name': the title of the section (string)
        - 'content': an array of strings detailing the main points, demonstration steps, or explanations.

        """

outline_prompt = ChatPromptTemplate.from_template(OUTLINE_PROMPT_TEMPLATE)

# --- Construct the outline chain ---
outline_chain = (
    outline_prompt
    | llm
    | StrOutputParser()

)

# --- Run the outline Chain ---
outline = outline_chain.invoke(video_idea_json)

# Convert result to JSON
outline_json = json.loads(outline)
logger.info("Outline JSON:")
# logger.info(outline_json)

# write outline to file
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
logger.info("Writing outline to file")
outline_filename = f"video_outline_{timestamp}.json"
with open(outline_filename, "w", encoding="utf-8") as f:
    f.write(json.dumps(outline_json, indent=2, ensure_ascii=False))

# --- Script generation logic ---
# Iterate through the outline
# Generate markdown from first section
# Subsequent sections, generate markdown from second section plus script so far

# --- Prompt: Generate script ---

SCRIPT_PROMPT_TEMPLATE_TEXT = """
    Begin with a concise checklist (3-7 bullets) of the steps to generate the script for the given section. Do not output this checklist.
    Create a detailed, markdown-formatted script for a specific section using the following inputs:

    - Section title: {name}
    - Section content: {content}

    Requirements:
    - Validate required keys before composing the script.
    - Use clear, consistent headings for each major step
    - Write for clarity and readability
    - Make the output concise yet thorough for this section.
    - Ensure all content is recent and up-to-date
    - Ensure the script you generate is consistent with the preceding sections in terms of tone, formatting, and flow
    - Avoid unnecessary repetition
    - Do not include a recap, wrap-up, or summary.
    - Be detailed and ensure accurate, step-by-step instructions are included for hands-on demonstrations.
    - Ensure all code samples work and are syntactically correct and functional

    Add your result to the following script:
    # START OF SCRIPT
    {script_so_far}
    # END OF SCRIPT

    ## Output Format
    Return ONLY the script content for this section as a JSON object:
    {{
    "section_name": "{name}",
    "script_markdown": "<string>"
    }}

"""

SCRIPT_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    SCRIPT_PROMPT_TEMPLATE_TEXT)

# --- Construct the script chain ---
script_chain = (
    SCRIPT_PROMPT_TEMPLATE
    | llm
    | StrOutputParser()

)

# --- Run the outline Chain with first section only ---
# script = script_chain.invoke(outline_json["sections"][0])
# logger.info("Script:")
# logger.info(script)

# Iterate through sections, accumulating script
accumulated_script_markdown_parts = []
all_section_scripts = []

accumulated_script_markdown_parts.append(f"# {video_idea_json['title']}")

# Safe json loading fx


def safe_json_loads(text):
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        # Try to extract a JSON object or array from the response
        m = re.search(r'\{.*\}', text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        m = re.search(r'\[.*\]', text, re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return None
##


for section in outline_json["sections"]:
    section_input = {
        "name": section.get("name", ""),
        "content": json.dumps(section.get("content", [])),
        "script_so_far": json.dumps(accumulated_script_markdown_parts)
    }
    try:
        raw_section_resp = script_chain.invoke(section_input)
        #section_obj = json.loads(raw_section_resp)
        section_obj = safe_json_loads(raw_section_resp)
        script_md = section_obj.get("script_markdown", "").strip()
        if not script_md:
            raise ValueError("Empty script returned for section.")
    except Exception:
        logger.exception(
            "Error generating script for section: %s", section.get("name"))
        logger.exception(raw_section_resp)
        raise

    # Accumulate
    logger.info("Script part generated:")
    logger.info(script_md)
    accumulated_script_markdown_parts.append(f"\n\n{script_md}")
    all_section_scripts.append(section_obj)

# Final combined script markdown
final_script_markdown = "\n\n".join(accumulated_script_markdown_parts)
logger.info("Final script generated.")
# logger.info(final_script_markdown)

# write script to file
logger.info("Writing script to file")
# timestamp = int(time.time())
script_filename = f"video_script_{timestamp}.md"
with open(script_filename, "w", encoding="utf-8") as f:
    f.write(final_script_markdown)

logger.info("Starting script QA")

QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the provided content for accuracy, relevance, logical consistency, clarity, completeness, tone, style, and audience appropriateness.
    - Title: {title}
    - Audience level: {level}
    Produce a concise, actionable report with the following sections:

    - Summary (one short sentence): state the content’s main claim or purpose and overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

    - Correctness: identify major factual errors. For each issue include why it is incorrect (brief explanation).

    - Consistency: identify internal contradictions, mismatched terminology, or logical gaps.

    - Clarity and Readability: note sentences or sections that are confusing, verbose, or jargon-heavy.

    - Completeness and Structure: list missing points, unanswered questions, or structural problems (e.g., poor flow, missing headings).

    - Audience Fit: state whether content matches the intended audience
    - Priority Level: assign each suggested change a priority (High/Medium/Low).
    - Final Recommendation: one sentence stating whether content is ready, needs minor edits, or requires major revision.

    Formatting requirements for your response:
       - Use Markdown headings for each numbered section above (e.g., "### 1. Summary").
       - Under remaining sections, present all suggestions as Markdown bullet lists.
       - For every bullet, include a Priority label in bold at the start (e.g., High:).

    Begin the analysis now on the following content:

    ## Input
    {content}
"""

QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    QA_PROMPT_TEMPLATE_TEXT)

# --- Construct the script QA chain ---
script_qa_chain = (
    QA_PROMPT_TEMPLATE
    | llm
    | StrOutputParser()
)

script_qa_response = script_qa_chain.invoke(
    {"title": video_idea_json['title'], "level": LEVEL, "content": final_script_markdown})

# write script QA report to file
script_qa_filename = f"video_script_qa_{timestamp}.md"
with open(script_qa_filename, "w", encoding="utf-8") as f:
    f.write(script_qa_response)
