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

ideation_prompt_template_text = """
        I want to create YouTube videos covering hands-on AI and LLM development and theory.
        Provide an idea for a video I can record and publish quickly.
        Keep the videos simple and accessible.
        Videos should be less than {max_minutes} minutes.
        Be sure that that title, tools, and learning objectives reflect content or hands-on activities that can be covered and completed in {max_minutes} minutes or less.
        Err on the side of covering too little rather than covering too much.
        Avoid overdone topics such as chatbots.
        Be decisive. Do not use "or" in the list of tools or learning objectives.

        # Output Format
        Return your answer as valid JSON using the following format:

            {{
                "title": "<string: SEO-optimized title of the video>",
                "tools": ["Tool or framework 1", "Tool or framework 2"],
                "learning_objectives": ["Learning objective 1", "Learning objective 2"]
            }}

        Return a maximum of 1 JSON object.

        # Example

        The following is an example output:

            {{
                "title": "Lightning Labs: Build a Tiny LLM Agent in 20 Minutes (Hands-On for IT Pros)",
                "tools": ["Python", "OpenAI API", "VS Code"],
                "learning_objectives": ["learn basic prompt design and chaining", "Understand the end-to-end flow of a small language-model-powered agent"]
            }},

        """

ideation_prompt_template = ChatPromptTemplate.from_template(
    ideation_prompt_template_text)

# Construct the ideation chain: prompt > LLM > string
video_idea_chain = ideation_prompt_template | llm | StrOutputParser()
logger.info("Chain:")
logger.info(video_idea_chain)

# Invoke the ideation chain
max_minutes = 30
video_idea = video_idea_chain.invoke({"max_minutes": max_minutes})

# Convert result to JSON
video_idea_json = json.loads(video_idea)
logger.info("Video idea JSON")
logger.info(video_idea_json)

# --- Prompt: Generate Outline ---

OUTLINE_PROMPT_TEMPLATE = """
        You will create a detailed outline for the following video.

          {{
                "title": "{title}",
                "tools": "{tools}",
                "learning_objectives": {learning_objectives}
          }},

        - Do not exceed the scope as defined by the title, tools, and learning objectives.
        - Do not include self-paced exercises. All demonstrations will be done in the video.
        - Think deeply about the outline and be absolutely sure it covers but does not exceed what the title promises.
        - Ensure the outline follows a logical sequence.
        - In the final section, do not include next steps or additional resources.

        # Output Format
        Return your answer as JSON formatted as follows:
        {{
            "sections": [
                {{ "name": "<string>", "content": []" }}
            ]
        }}

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
    - Ensure tone and formatting are consistent with previous sections.
    - Do not include next steps or external resources in this section.
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
#script = script_chain.invoke(outline_json["sections"][0])
#logger.info("Script:")
#logger.info(script)

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
            logger.exception("Error generating script for section: %s", section.get("name"))
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
