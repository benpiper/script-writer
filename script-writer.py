import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("script_writer")

llm = ChatOpenAI(model="gpt-5-nano", temperature=1,
                 use_responses_api=True, reasoning_effort="low")

# --- Prompt: Generate Video Idea ---

IDEATION_PROMPT_TEMPLATE_TEXT = """
        Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level.
        Generate an idea for a video that can be quickly recorded and published, guided by the following requirements:
        - Inputs:
        - Topic: {topic} (string)
        - Level: {level} (string)
        - Maximum Length: {max_minutes} (positive integer; video must be less than or equal to this number of minutes)
        - Requirements:
        - Do not include or mention time estimates in the video title.
        - The title, list of tools, and learning objectives must all be achievable within {max_minutes} minutes.
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

        - Example


            {{
                "title": "Lightning Labs: Build a Tiny LLM Agent in 20 Minutes (Hands-On for IT Pros)",
                "tools": ["Python", "OpenAI API", "VS Code"],
                "learning_objectives": ["learn basic prompt design and chaining", "Understand the end-to-end flow of a small language-model-powered agent"]
            }},

          After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
          If validation fails, self-correct and return the correct JSON error object.
        """

IDEATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
    IDEATION_PROMPT_TEMPLATE_TEXT)

# Construct the ideation chain: prompt > LLM > string
video_idea_chain = IDEATION_PROMPT_TEMPLATE | llm | StrOutputParser()
logger.info("Chain:")
logger.info(video_idea_chain)

# Invoke the ideation chain
MAX_MINUTES = 30
TOPIC = "hands-on AI, ML, or LLM development and theory."
LEVEL = "Beginner"
video_idea = video_idea_chain.invoke(
    {"max_minutes": MAX_MINUTES, "topic": TOPIC, "level": LEVEL})

# Convert result to JSON
video_idea_json = json.loads(video_idea)
logger.info("Video idea JSON")
logger.info(video_idea_json)

# --- Prompt: Generate Outline ---

OUTLINE_PROMPT_TEMPLATE = """
        Begin with a concise checklist (3-7 bullets) of the main planning and sequencing steps you will follow before creating the outline.
        Create a comprehensive outline for the specified video using the structured input provided.

        Input JSON structure:
        ```
        {
        "title": "<string>",
        "tools": [<string>, ...],
        "learning_objectives": [<string>, ...]
        }
        ```
         
        Guidelines:
        - Stay strictly within the scope defined by the title, tools, and learning objectives.
        - Exclude self-paced exercises; all demonstrations should be incorporated within the video outline.
        - Do not incorporate Google Colab in examples or demonstrations.
        - Carefully design the outline to ensure it fully addresses, but does not go beyond, the content indicated in the title.
        - Arrange all sections and demonstration steps in a clear, logical sequence.
        - For the final section, refrain from including next steps, recommendations, or external/additional resources.

        If 'title', 'tools', or 'learning_objectives' fields are missing or not the correct type, respond with the following JSON object:
        ```
        {"error": "Missing or invalid input fields."}
        ```

        After outlining, validate that each section directly supports the provided title and learning objectives, and confirm that all demonstrations are video-based and in logical order.
        If any guideline is not fully met, correct the outline before producing your final output.

        # Output Format
        - Return a JSON object structured as:
        ```
        {
        "sections": [
        { "name": "<string>", "content": [<string>, ...] }
        ]
        }
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
logger.info(outline_json)

# --- Script generation logic ---
# Iterate through the outline
# Generate markdown from first section
# Subsequent sections, generation markdown from second section plus script so far

# --- Prompt: Generate script ---

SCRIPT_PROMPT_TEMPLATE_TEXT = """
    You will write a detailed script based on the following section of an outline.

    - Section title: {name}
    - Section content: {content}

    You will add your result to the following script, ensuring it is consistent and complete:
    # START OF SCRIPT
    {script_so_far}
    # END OF SCRIPT

    Requirements:
    - Keep the output concise but complete for this section.
    - Ensure tone, formatting, and facts are consistent with previous sections.
    - Do not include next steps or external resources in this section.
    - Do not repeat explanations or definitions.
    - Do not reiterate the learning objectives in the final section
    - Do not include a recap
    - Return ONLY the script content for this section as a JSON object:
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

for section in outline_json["sections"]:
    section_input = {
        "name": section.get("name", ""),
        "content": json.dumps(section.get("content", [])),
        "script_so_far": json.dumps(accumulated_script_markdown_parts)
    }
    try:
        raw_section_resp = script_chain.invoke(section_input)
        section_obj = json.loads(raw_section_resp)
        script_md = section_obj.get("script_markdown", "").strip()
        if not script_md:
            raise ValueError("Empty script returned for section.")
    except Exception:
        logger.exception(
            "Error generating script for section: %s", section.get("name"))
        raise

    # Accumulate
    logger.info("Script part generated:")
    logger.info(script_md)
    accumulated_script_markdown_parts.append(f"\n\n{script_md}")
    all_section_scripts.append(section_obj)

# Final combined script markdown
final_script_markdown = "\n\n".join(accumulated_script_markdown_parts)
logger.info("Final script generated.")
logger.info(final_script_markdown)


# write to file
with open("video_script.md", "w", encoding="utf-8") as f:
    f.write(final_script_markdown)
