""" functions.py """
import os
import json
import re
import logging
import signal
from dotenv import load_dotenv
from typing import Dict, Union
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_ollama import ChatOllama
from prompts import IDEATION_PROMPT_TEMPLATE_TEXT, IDEATION_QA_PROMPT_TEMPLATE_TEXT, OUTLINE_PROMPT_TEMPLATE, SCRIPT_PROMPT_TEMPLATE_TEXT, SCRIPT_QA_PROMPT_TEMPLATE_TEXT, OUTLINE_QA_PROMPT_TEMPLATE_TEXT, OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT, SCRIPT_FINAL_PROMPT_TEMPLATE_TEXT

# Helper functions

load_dotenv()

# Get LLM


def get_llm(model):
    """ Return model and provider based on a string """
    if model == "gpt-5-nano":
        return ChatOpenAI(model="gpt-5-nano", temperature=1,
                          use_responses_api=True, reasoning_effort="low")
    elif model == "gpt-oss":
        return ChatOllama(
            model="gpt-oss",
            temperature=1.0,
            reasoning=None,
            num_predict=-1,        # similar to max tokens / num_predict
            validate_model_on_init=True,
            base_url=os.getenv('OLLAMA_BASE_URL')
        )
    else:
        raise ValueError(f"Model '{model}' not supported")


def timeout_handler(signum, frame):
    raise TimeoutError


# Function: Ask for approval


def ask_approval():
    """ Ask for approval with a 10-second timeout """
    print("Enter 1 to approve, any other key to decline: ")
    
    # Set the signal handler and a timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # Set a 10-second timer

    try:
        choice = input()
        signal.alarm(0)  # Cancel the alarm
        if choice == '1':
            logging.info("Approved")
            return True
        else:
            logging.info("Not approved")
            return False
    except TimeoutError:
        logging.info("No input provided; defaulting to Approved")
        return True


def select_title(video_idea_json):
    """ Select a title from the generated options with a timeout """
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
    """ Load JSON safely with enhanced recovery """
    logging.basicConfig(level=logging.INFO)
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
        
        logger.warning("Unable to recover JSON from text.")
        logger.debug(f"Failed text: {text}")
        return {"error": "Invalid JSON format"}


"""  """
# Function: Write JSON


def write_json(data, filename):
    """ Write JSON data to a file """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False))

# Function: Write markdown


def write_markdown(data, filename):
    """ Write markdown to a file """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)

# Function: Generate and invoke chain


import time

def create_invoke_chain(llm, prompt_template_text, input_json, retries=3):
    """ Create and invoke chain with retries """
    prompt_template = ChatPromptTemplate.from_template(prompt_template_text)
    chain = prompt_template | llm | StrOutputParser()
    
    for attempt in range(retries):
        try:
            result = chain.invoke(input_json)
            return result
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logging.error("All retry attempts failed.")
                raise e

# Function: Generate video idea


def generate_video_idea(llm: Union[ChatOpenAI, ChatOllama], topic: str, domain: str, level: str) -> Dict:
    """ Generate video idea """
    input_json = {"topic": topic, "domain": domain, "level": level}
    video_idea = create_invoke_chain(
        llm, IDEATION_PROMPT_TEMPLATE_TEXT, input_json)
    logging.debug("Idea response: %s", video_idea)
    # Convert result to JSON
    # video_idea_json = json.loads(video_idea)
    return safe_json_loads(video_idea)


# Function: Generate ideation post-QA output

def generate_idea_qa_report(llm: Union[ChatOpenAI, ChatOllama], video_idea: Dict):
    """ Generate QA report for idea """
    IDEATION_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        IDEATION_QA_PROMPT_TEMPLATE_TEXT)
    idea_qa_chain = (
        IDEATION_QA_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )
    idea_qa_response = idea_qa_chain.invoke(
        video_idea)
    logging.debug("Idea QA response: %s", idea_qa_response)
    idea_qa_response_json = safe_json_loads(idea_qa_response)
    return idea_qa_response_json

# Function: Generate video outline


def generate_video_outline(llm: Union[ChatOpenAI, ChatOllama], video_idea: str):
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


def generate_outline_qa_report(llm: Union[ChatOpenAI, ChatOllama], video_idea: str, outline: str):
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
    outline_qa_response_json = safe_json_loads(outline_qa_response)
    return outline_qa_response_json

# Function: Generate outline based on QA report


def generate_outline_final(llm, outline_qa_report, outline_json):
    """ Generate new outline based on QA report """
    input_json = {"outline": outline_json,
                  "outline_qa_report": outline_qa_report}
    outline_final = create_invoke_chain(
        llm, OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT, input_json)
    return safe_json_loads(outline_final)


def generate_video_script(llm: Union[ChatOpenAI, ChatOllama], outline: str):
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
    logging.debug("Generate script response: %s", script)
    # script_json = safe_json_loads(script)
    # return script_json
    return script

# Function: Generate QA for script


def generate_qa_report(llm: Union[ChatOpenAI, ChatOllama], title: str, level: str, script_md: str):
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

    return safe_json_loads(script_qa_response)


def generate_script_final(llm: Union[ChatOpenAI, ChatOllama], script_qa_response: str, video_script: str):
    """ Correct video script using QA feedback """

    SCRIPT_FINAL_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        SCRIPT_FINAL_PROMPT_TEMPLATE_TEXT)

    # --- Construct the script chain ---
    script_chain = (
        SCRIPT_FINAL_PROMPT_TEMPLATE
        | llm
        | StrOutputParser()

    )
    chain_input = {"script_qa_report": script_qa_response,
                   "script": video_script}
    script = script_chain.invoke(chain_input)
    logging.debug("Generate corrected script response: %s", script)
    return script
