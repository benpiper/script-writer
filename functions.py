import json
import re
import logging
from typing import Dict, Union
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_ollama import ChatOllama
from prompts import IDEATION_PROMPT_TEMPLATE_TEXT, OUTLINE_PROMPT_TEMPLATE, SCRIPT_PROMPT_TEMPLATE_TEXT, SCRIPT_QA_PROMPT_TEMPLATE_TEXT, OUTLINE_QA_PROMPT_TEMPLATE_TEXT

# Helper functions

# Get LLM


def get_llm(model):
    """ Return model and provider based on a string """
    try:
        if (model == "gpt-5-nano"):
            llm = ChatOpenAI(model="gpt-5-nano", temperature=1,
                             use_responses_api=True, reasoning_effort="low")
        elif (model == "gpt-oss"):
            llm = ChatOllama(
                model="gpt-oss",
                temperature=1.0,
                reasoning=None,
                num_predict=-1,        # similar to max tokens / num_predict
                validate_model_on_init=True,
                base_url="http://192.168.88.86:11434"
            )
        return llm
    except NameError as e:
        raise NameError("Model not found") from e


# Safe json loading fx

def safe_json_loads(text):
    """ Load JSON safely """
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


def generate_video_idea(llm: Union[ChatOpenAI, ChatOllama], max_minutes: float, topic: str, domain: str, level: str) -> Dict:
    """ Generate video idea """

    IDEATION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        IDEATION_PROMPT_TEMPLATE_TEXT)

    # Construct the ideation chain: prompt > LLM > string
    video_idea_chain = IDEATION_PROMPT_TEMPLATE | llm | StrOutputParser()
    # logger.info("Chain:")
    # logger.info(video_idea_chain)

    # Invoke the ideation chain
    video_idea = video_idea_chain.invoke(
        {"max_minutes": max_minutes, "topic": topic, "domain": domain, "level": level})

    # Convert result to JSON
    # video_idea_json = json.loads(video_idea)
    return (json.loads(video_idea))


# Function: Generate video outline


def generate_video_outline(llm: Union[ChatOpenAI, ChatOllama], video_idea):
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


def generate_outline_qa_report(llm: Union[ChatOpenAI, ChatOllama], video_idea, outline):
    """ Generate QA report for outline """
    OUTLINE_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        OUTLINE_QA_PROMPT_TEMPLATE_TEXT)
    outline_qa_chain = (
        OUTLINE_QA_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )
    outline_qa_response = outline_qa_chain.invoke(
        {"outline": outline, **video_idea})
    return json.loads(outline_qa_response)


def generate_video_script(llm: Union[ChatOpenAI, ChatOllama], outline):
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

# Function: Generate QA for script


def generate_qa_report(llm: Union[ChatOpenAI, ChatOllama], title, level, script_md):
    """ Generate QA report from script """
    SCRIPT_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        SCRIPT_QA_PROMPT_TEMPLATE_TEXT)

    # --- Construct the script QA chain ---
    script_qa_chain = (
        SCRIPT_QA_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )

    script_qa_response = script_qa_chain.invoke(
        {"title": title, "level": level, "content": script_md})

    return script_qa_response
