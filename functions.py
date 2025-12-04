"""functions.py"""

import os
import json
import re
import logging
import signal
import time
from dotenv import load_dotenv
from typing import Dict, Union
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from prompts import (
    IDEATION_PROMPT_TEMPLATE_TEXT,
    IDEATION_QA_PROMPT_TEMPLATE_TEXT,
    OUTLINE_PROMPT_TEMPLATE,
    SCRIPT_QA_PROMPT_TEMPLATE_TEXT,
    OUTLINE_QA_PROMPT_TEMPLATE_TEXT,
    OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT,
    SCRIPT_SECTION_PROMPT_TEMPLATE_TEXT,
    SUMMARIZE_SECTION_PROMPT_TEMPLATE_TEXT,
)

# Helper functions

load_dotenv()

# Get LLM


def get_llm(model):
    """Return model and provider based on a string"""
    if model == "gpt-5-nano":
        return ChatOpenAI(
            model="gpt-5-nano",
            temperature=1,
            use_responses_api=True,
            reasoning_effort="low",
        )
    elif model == "gpt-oss":
        return ChatOllama(
            model="gpt-oss",
            temperature=1.0,
            reasoning=None,
            num_predict=-1,  # similar to max tokens / num_predict
            validate_model_on_init=True,
            base_url=os.getenv("OLLAMA_BASE_URL"),
        )
    else:
        raise ValueError(f"Model '{model}' not supported")


def timeout_handler(signum, frame):
    raise TimeoutError


# Function: Ask for approval


def ask_approval():
    """Ask for approval with a 15-second timeout"""
    print("Enter 1 to approve, any other key to decline: ")

    # Set the signal handler and a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(15)  # Set a 15-second timer

    try:
        choice = input()
        signal.alarm(0)  # Cancel the alarm
        if choice == "1":
            logging.info("Approved")
            return True
        else:
            logging.info("Not approved")
            return False
    except TimeoutError:
        logging.info("No input provided; defaulting to Approved")
        return True


def select_title(video_idea_json):
    """Select a title from the generated options with a timeout"""
    titles = {
        "1": ("Original", video_idea_json.get("title")),
        "2": ("Contrarian", video_idea_json.get("title_contrarian")),
        "3": ("Descriptive", video_idea_json.get("title_descriptive")),
        "4": ("Problem/Solution", video_idea_json.get("title_problem_solution")),
        "5": ("How-To", video_idea_json.get("title_how_to")),
        "6": ("Curiosity", video_idea_json.get("title_curiosity")),
    }

    print("\nSelect a title (defaulting to 1 in 10 seconds):")
    for key, (desc, title) in titles.items():
        if title:
            print(f"{key}. {desc}: {title}")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    try:
        choice = input("\nEnter choice (1-6): ").strip()
        signal.alarm(0)
        if choice in titles and titles[choice][1]:
            selected_title = titles[choice][1]
            logging.info(f"Selected title: {selected_title}")
            return selected_title
    except TimeoutError:
        logging.info("Timeout reached. Defaulting to original title.")
    except Exception as e:
        logging.error(f"Error during selection: {e}")

    return video_idea_json.get("title")


# Safe json loading fx


def safe_json_loads(text):
    """Load JSON safely with enhanced recovery"""
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("safe_json_loader")
    if not isinstance(text, str):
        logger.warning("Not a string")
        return None

    # Clean up markdown code blocks if present
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Invalid JSON. Attempting to recover.")

        # Attempt 1: Fix invalid escapes (common in Windows paths)
        # Match double backslashes (keep them) OR single backslashes not followed by valid escape chars (escape them)
        fixed_text = re.sub(
            r'(\\\\)|(\\(?!["\\/bfnrtu]))',
            lambda m: m.group(1) if m.group(1) else r"\\",
            text,
        )
        try:
            return json.loads(fixed_text)
        except json.JSONDecodeError:
            pass

        # Try to extract a JSON object or array from the response
        # Find the first '{' and the last '}'
        m_obj = re.search(r"\{.*\}", text, re.S)
        # Find the first '[' and the last ']'
        m_arr = re.search(r"\[.*\]", text, re.S)

        candidates = []
        if m_obj:
            candidates.append(m_obj.group(0))
        if m_arr:
            candidates.append(m_arr.group(0))

        for candidate in candidates:
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Last ditch effort: try to fix common errors (like trailing commas)
        if m_obj:
            try:
                # Remove trailing commas before closing braces/brackets
                fixed_text = re.sub(r",\s*([\]\}])", r"\1", m_obj.group(0))
                return json.loads(fixed_text)
            except Exception:
                pass

        logger.warning("Unable to recover JSON from text.")
        logger.debug(f"Failed text: {text}")
        return {"error": "Invalid JSON format"}


"""  """
# Function: Write JSON


def write_json(data, filename):
    """Write JSON data to a file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))


# Function: Write markdown


def write_markdown(data, filename):
    """Write markdown to a file"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)


# Function: Generate and invoke chain


def create_invoke_chain(llm, prompt_template_text, input_json, retries=3):
    """Create and invoke chain with retries"""
    prompt_template = ChatPromptTemplate.from_template(prompt_template_text)
    chain = prompt_template | llm | StrOutputParser()

    for attempt in range(retries):
        try:
            result = chain.invoke(input_json)
            return result
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2**attempt)  # Exponential backoff
            else:
                logging.error("All retry attempts failed.")
                raise e


# Function: Generate video idea


def generate_video_idea(
    llm: Union[ChatOpenAI, ChatOllama], topic: str, domain: str, level: str
) -> Dict:
    """Generate video idea"""
    input_json = {"topic": topic, "domain": domain, "level": level}
    video_idea = create_invoke_chain(llm, IDEATION_PROMPT_TEMPLATE_TEXT, input_json)
    logging.debug("Idea response: %s", video_idea)
    # Convert result to JSON
    # video_idea_json = json.loads(video_idea)
    return safe_json_loads(video_idea)


# Function: Generate ideation post-QA output


def generate_idea_qa_report(llm: Union[ChatOpenAI, ChatOllama], video_idea: Dict):
    """Generate QA report for idea"""
    IDEATION_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        IDEATION_QA_PROMPT_TEMPLATE_TEXT
    )
    idea_qa_chain = IDEATION_QA_PROMPT_TEMPLATE | llm | StrOutputParser()
    idea_qa_response = idea_qa_chain.invoke(video_idea)
    logging.debug("Idea QA response: %s", idea_qa_response)
    idea_qa_response_json = safe_json_loads(idea_qa_response)
    return idea_qa_response_json


# Function: Generate video outline


def generate_video_outline(llm: Union[ChatOpenAI, ChatOllama], video_idea: str):
    """Generate video outline from video_idea (json)"""

    outline_prompt = ChatPromptTemplate.from_template(OUTLINE_PROMPT_TEMPLATE)

    # --- Construct the outline chain ---
    outline_chain = outline_prompt | llm | StrOutputParser()

    # --- Run the outline Chain ---
    outline_response = outline_chain.invoke(video_idea)
    # Convert result to JSON
    outline = safe_json_loads(outline_response)
    return outline


# Function: Generate video script


def generate_outline_qa_report(
    llm: Union[ChatOpenAI, ChatOllama], video_idea: str, outline: str
):
    """Generate QA report for outline"""
    OUTLINE_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        OUTLINE_QA_PROMPT_TEMPLATE_TEXT
    )
    outline_qa_chain = OUTLINE_QA_PROMPT_TEMPLATE | llm | StrOutputParser()
    outline_qa_response = outline_qa_chain.invoke({"outline": outline, **video_idea})
    outline_qa_response_json = safe_json_loads(outline_qa_response)
    return outline_qa_response_json


# Function: Generate outline based on QA report


def generate_outline_final(llm, outline_qa_report, outline_json):
    """Generate new outline based on QA report"""
    input_json = {"outline": outline_json, "outline_qa_report": outline_qa_report}
    outline_final = create_invoke_chain(
        llm, OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT, input_json
    )
    return safe_json_loads(outline_final)


def summarize_script_section(llm: Union[ChatOpenAI, ChatOllama], section_script: str):
    """Summarize a script section for context"""
    SUMMARIZE_PROMPT = ChatPromptTemplate.from_template(
        SUMMARIZE_SECTION_PROMPT_TEMPLATE_TEXT
    )
    summary_chain = SUMMARIZE_PROMPT | llm | StrOutputParser()
    summary = summary_chain.invoke({"section_script": section_script})
    logging.debug(f"Section Summary: {summary}")
    return summary


def generate_video_script(llm: Union[ChatOpenAI, ChatOllama], outline: Dict):
    """Generate video script from outline (json) iteratively"""

    SCRIPT_SECTION_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        SCRIPT_SECTION_PROMPT_TEMPLATE_TEXT
    )

    # --- Construct the script chain ---
    script_chain = SCRIPT_SECTION_PROMPT_TEMPLATE | llm | StrOutputParser()

    full_script = ""

    # Extract title and level from meta if available
    title = ""
    level = ""
    if "meta" in outline and len(outline["meta"]) > 0:
        title = outline["meta"][0].get("title", "")
        level = outline["meta"][0].get("level", "")

    # Iterate through sections, accumulating script
    running_summary = "No previous content."

    for i, section in enumerate(outline.get("sections", [])):
        section_name = section.get("name", "")
        section_content = "\n".join(section.get("content", []))

        logging.info(f"Generating script for section: {section_name}")

        # Get recent script content (last ~2000 chars) for immediate context
        recent_script_content = (
            full_script[-2000:] if len(full_script) > 2000 else full_script
        )
        if not recent_script_content:
            recent_script_content = "No preceding script."

        section_script = script_chain.invoke(
            {
                "title": title,
                "level": level,
                "outline": json.dumps(outline, indent=2),
                "context_summary": running_summary,
                "recent_script_content": recent_script_content,
                "section_name": section_name,
                "section_content": section_content,
            }
        )

        full_script += f"\n\n{section_script}"

        # Update summary for next iteration
        logging.info(f"Summarizing section: {section_name}")
        new_summary = summarize_script_section(llm, section_script)
        if running_summary == "No previous content.":
            running_summary = new_summary
        else:
            running_summary += f"\n\n{new_summary}"

    return full_script


# Function: Generate QA for script


def generate_qa_report(
    llm: Union[ChatOpenAI, ChatOllama], title: str, level: str, script_md: str
):
    """Generate QA report from script"""
    SCRIPT_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        SCRIPT_QA_PROMPT_TEMPLATE_TEXT
    )

    # --- Construct the script QA chain ---
    script_qa_chain = SCRIPT_QA_PROMPT_TEMPLATE | llm | StrOutputParser()

    script_qa_response = script_qa_chain.invoke(
        {"title": title, "level": level, "content": script_md}
    )

    return safe_json_loads(script_qa_response)
