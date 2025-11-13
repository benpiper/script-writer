import json
import re
import logging
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from prompts import IDEATION_PROMPT_TEMPLATE_TEXT, OUTLINE_PROMPT_TEMPLATE, SCRIPT_PROMPT_TEMPLATE_TEXT, QA_PROMPT_TEMPLATE_TEXT

# Helper functions

# Safe json loading fx


def safe_json_loads(text):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("safe_json_loader")
    if not isinstance(text, str):
        return None
    try:
        return json.loads(text)
    except Exception:
        logger.warning("Invalid JSON. Attempting to recover.")
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

# Function: Generate video idea


def generate_video_idea(llm, max_minutes, topic, level):
    """ Generate video idea """

    IDEATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        IDEATION_PROMPT_TEMPLATE_TEXT)

    # Construct the ideation chain: prompt > LLM > string
    video_idea_chain = IDEATION_PROMPT_TEMPLATE | llm | StrOutputParser()
    # logger.info("Chain:")
    # logger.info(video_idea_chain)

    # Invoke the ideation chain
    video_idea = video_idea_chain.invoke(
        {"max_minutes": max_minutes, "topic": topic, "level": level})

    # Convert result to JSON
    # video_idea_json = json.loads(video_idea)
    return (json.loads(video_idea))


# Function: Generate video outline


def generate_video_outline(llm, video_idea):
    """ Generate video outline from video_idea (json) """

    outline_prompt = ChatPromptTemplate.from_template(OUTLINE_PROMPT_TEMPLATE)

    # --- Construct the outline chain ---
    outline_chain = (
        outline_prompt
        | llm
        | StrOutputParser()
    )

    # --- Run the outline Chain ---
    outline_response = outline_chain.invoke(video_idea)
    # Convert result to JSON
    outline = safe_json_loads(outline_response)
    return outline

# Function: Generate video script


def generate_video_script(llm, outline):
    """ Generate video script from outline (json)
    Non-iterative version """

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
    """ accumulated_script_markdown_parts = []
    all_section_scripts = []

    accumulated_script_markdown_parts.append(f"# {video_idea_json['title']}")
    """

    script = script_chain.invoke({"content": outline})
    script_json = safe_json_loads(script)
    return script_json

# Function: Generate QA of script


def generate_qa_report(llm, title, level, script_md):
    """ Generate QA report from script """
    QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        QA_PROMPT_TEMPLATE_TEXT)

    # --- Construct the script QA chain ---
    script_qa_chain = (
        QA_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )

    script_qa_response = script_qa_chain.invoke(
        {"title": title, "level": level, "content": script_md})

    return script_qa_response