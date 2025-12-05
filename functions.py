"""functions.py"""

import os
import json
import re
import logging
import signal
import time
import functools
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Union, Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from langchain_community.utilities import SearxSearchWrapper
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

# Initialize search tool (optional - only if SEARXNG_URL is configured)
_search_tool = None


def get_search_tool():
    """Get or create SearXNG search tool"""
    global _search_tool
    if _search_tool is None:
        searxng_url = os.getenv("SEARXNG_URL")
        if searxng_url:
            try:
                _search_tool = SearxSearchWrapper(searx_host=searxng_url)
                logging.info(f"SearXNG search tool initialized at {searxng_url}")
            except Exception as e:
                logging.warning(f"Failed to initialize SearXNG: {e}")
    return _search_tool


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


# Retry Decorator


def retry_with_backoff(max_retries=3, base_delay=1.0, exceptions=(Exception,)):
    """Decorator to retry a function with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds (doubles each retry)
        exceptions: Tuple of exceptions to catch and retry
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__name__)

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}"
                        )
                        raise

                    delay = base_delay * (2**attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)[:100]}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)

        return wrapper

    return decorator


# Safe json loading fx


def safe_json_loads(text, context="", save_debug=True):
    """Load JSON safely with enhanced recovery and debugging

    Args:
        text: The text to parse as JSON
        context: Description of what this JSON is for (for debug logging)
        save_debug: Whether to save failed JSON to debug file
    """
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("safe_json_loader")

    # Log the raw response with context
    if context:
        logger.debug(f"\n{'=' * 60}\nParsing JSON for: {context}\n{'=' * 60}")

    logger.debug(
        f"Raw response length: {len(text) if isinstance(text, str) else 'N/A'} characters"
    )
    logger.debug(f"Raw response preview (first 500 chars):\n{str(text)[:500]}")

    if not isinstance(text, str):
        logger.warning(f"Expected string, got {type(text)}")
        return None

    original_text = text  # Keep original for debug file

    # Clean up markdown code blocks if present
    text = text.strip()
    if text.startswith("```json"):
        logger.debug("Removing ```json markdown wrapper")
        text = text[7:]
    if text.startswith("```"):
        logger.debug("Removing ``` markdown wrapper")
        text = text[3:]
    if text.endswith("```"):
        logger.debug("Removing trailing ```")
        text = text[:-3]
    text = text.strip()

    # Attempt 1: Direct parsing
    try:
        result = json.loads(text)
        logger.debug("✓ Successfully parsed JSON on first attempt")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parse failed: {e}")
        logger.debug(f"Error at line {e.lineno}, column {e.colno}: {e.msg}")

    # Attempt 2: Fix backticks with nested quotes (e.g., `dataset["test"]`)
    if "`" in text and '"' in text:
        logger.debug(
            "Attempting recovery: replacing backticks to prevent nested quote issues"
        )
        # Replace backticks with single quotes to avoid quote nesting
        fixed_text = text.replace("`", "'")
        try:
            result = json.loads(fixed_text)
            logger.debug("✓ Successfully parsed JSON after replacing backticks")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed after replacing backticks: {e.msg}")

    # Attempt 3: Convert Python dict syntax to JSON (single quotes to double quotes)
    if text.strip().startswith("{") and "'" in text and ":" in text:
        logger.debug("Attempting recovery: converting Python dict syntax to JSON")
        # Replace single quotes with double quotes for JSON compliance
        fixed_text = text.replace("'", '"')
        try:
            result = json.loads(fixed_text)
            logger.debug(
                "✓ Successfully parsed JSON after converting Python dict syntax"
            )
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed after Python dict conversion: {e.msg}")

    # Attempt 4: Fix string concatenation (e.g., "text1" + "text2")
    if '" +' in text or "' +" in text:
        logger.debug("Attempting recovery: removing string concatenation operators")
        # Remove "+ and +" patterns (with optional whitespace)
        fixed_text = re.sub(r'"\s*\+\s*"', "", text)  # "text" + "text" -> "texttext"
        fixed_text = re.sub(
            r"'\s*\+\s*'", "", fixed_text
        )  # 'text' + 'text' -> 'texttext'
        try:
            result = json.loads(fixed_text)
            logger.debug(
                "✓ Successfully parsed JSON after removing string concatenation"
            )
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed after removing concatenation: {e.msg}")

    # Attempt 5: Fix invalid escapes (common in Windows paths)
    logger.debug("Attempting recovery: fixing invalid escape sequences")
    fixed_text = re.sub(
        r'(\\\\)|(\\(?!["\\/ bfnrtu]))',
        lambda m: m.group(1) if m.group(1) else r"\\",
        text,
    )
    try:
        result = json.loads(fixed_text)
        logger.debug("✓ Successfully parsed JSON after fixing escape sequences")
        return result
    except json.JSONDecodeError as e:
        logger.debug(f"Failed after escape fix: {e.msg}")

    # Attempt 6: Extract JSON object or array from the response
    logger.debug("Attempting recovery: extracting JSON from surrounding text")
    m_obj = re.search(r"\{.*\}", text, re.S)
    m_arr = re.search(r"\[.*\]", text, re.S)

    candidates = []
    if m_obj:
        candidates.append(("object", m_obj.group(0)))
    if m_arr:
        candidates.append(("array", m_arr.group(0)))

    for json_type, candidate in candidates:
        try:
            result = json.loads(candidate)
            logger.debug(f"✓ Successfully parsed JSON {json_type} after extraction")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed to parse extracted {json_type}: {e.msg}")

    # Attempt 7: Fix trailing commas
    if m_obj:
        logger.debug("Attempting recovery: removing trailing commas")
        try:
            fixed_text = re.sub(r",\s*([\]\}])", r"\1", m_obj.group(0))
            result = json.loads(fixed_text)
            logger.debug("✓ Successfully parsed JSON after removing trailing commas")
            return result
        except json.JSONDecodeError as e:
            logger.debug(f"Failed after removing trailing commas: {e.msg}")

    # All attempts failed - save debug file and return error
    logger.error("✗ All JSON recovery attempts failed")

    if save_debug:
        try:
            debug_dir = "debug_json_failures"
            os.makedirs(debug_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            context_slug = (
                re.sub(r"[^a-z0-9]+", "_", context.lower()) if context else "unknown"
            )
            debug_file = os.path.join(debug_dir, f"{timestamp}_{context_slug}.txt")

            with open(debug_file, "w", encoding="utf-8") as f:
                f.write("Failed JSON Parse Debug Report\n")
                f.write("=" * 60 + "\n")
                f.write(f"Context: {context}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Response length: {len(original_text)} characters\n")
                f.write("\n" + "=" * 60 + "\n")
                f.write("ORIGINAL RESPONSE:\n")
                f.write("=" * 60 + "\n")
                f.write(original_text)
                f.write("\n\n" + "=" * 60 + "\n")
                f.write("CLEANED TEXT:\n")
                f.write("=" * 60 + "\n")
                f.write(text)

            logger.info(f"Debug file saved: {debug_file}")
        except Exception as e:
            logger.error(f"Failed to save debug file: {e}")

    logger.debug(f"Failed to parse. Last 1000 chars of cleaned text:\n{text[-1000:]}")
    return {"error": "Invalid JSON format"}


def validate_and_clean_outline(outline_data):
    """Validate and clean outline JSON structure, removing invalid keys

    Args:
        outline_data: Parsed JSON outline data

    Returns:
        Cleaned outline data with only valid keys
    """
    logger = logging.getLogger("validate_outline")

    if not isinstance(outline_data, dict):
        logger.warning("Outline data is not a dictionary")
        return outline_data

    if "error" in outline_data:
        return outline_data

    # Validate and clean sections
    if "sections" in outline_data and isinstance(outline_data["sections"], list):
        cleaned_sections = []
        invalid_keys_found = []

        for i, section in enumerate(outline_data["sections"]):
            if not isinstance(section, dict):
                logger.warning(f"Section {i} is not a dictionary, skipping")
                continue

            # Check for invalid keys
            allowed_keys = {"name", "content"}
            actual_keys = set(section.keys())
            invalid_keys = actual_keys - allowed_keys

            if invalid_keys:
                invalid_keys_found.extend(invalid_keys)
                logger.warning(
                    f"Section {i} ('{section.get('name', 'unnamed')}') has invalid keys: {invalid_keys}. "
                    f"Stripping them out."
                )

            # Create cleaned section with only allowed keys
            cleaned_section = {
                "name": section.get("name", ""),
                "content": section.get("content", []),
            }
            cleaned_sections.append(cleaned_section)

        if invalid_keys_found:
            unique_invalid = set(invalid_keys_found)
            logger.info(
                f"✓ Cleaned outline: removed {len(invalid_keys_found)} invalid keys "
                f"({', '.join(sorted(unique_invalid))}) from sections"
            )

        outline_data["sections"] = cleaned_sections

    return outline_data


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
    return safe_json_loads(video_idea, context="video_idea")


# Function: Generate ideation post-QA output


def generate_idea_qa_report(llm: Union[ChatOpenAI, ChatOllama], video_idea: Dict):
    """Generate QA report for idea"""
    IDEATION_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        IDEATION_QA_PROMPT_TEMPLATE_TEXT
    )
    idea_qa_chain = IDEATION_QA_PROMPT_TEMPLATE | llm | StrOutputParser()
    idea_qa_response = idea_qa_chain.invoke(video_idea)
    logging.debug("Idea QA response: %s", idea_qa_response)
    idea_qa_response_json = safe_json_loads(idea_qa_response, context="idea_qa_report")
    return idea_qa_response_json


# Function: Generate video outline


@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    exceptions=(json.JSONDecodeError, KeyError, TypeError),
)
def generate_video_outline(llm: Union[ChatOpenAI, ChatOllama], video_idea: str):
    """Generate video outline from video_idea (json) with retry logic"""
    logger = logging.getLogger("generate_video_outline")

    logger.info("Generating video outline...")
    logger.debug(
        f"Input video_idea keys: {list(video_idea.keys()) if isinstance(video_idea, dict) else 'N/A'}"
    )

    outline_prompt = ChatPromptTemplate.from_template(OUTLINE_PROMPT_TEMPLATE)
    outline_chain = outline_prompt | llm | StrOutputParser()

    # Run the outline chain
    logger.debug("Invoking outline chain...")
    outline_response = outline_chain.invoke(video_idea)

    logger.debug(f"Outline response received ({len(outline_response)} chars)")
    logger.debug(f"Outline response preview: {outline_response[:300]}...")

    # Convert result to JSON with context for better debugging
    outline = safe_json_loads(outline_response, context="video_outline")

    # Clean up the outline to remove invalid keys
    outline = validate_and_clean_outline(outline)

    # Validate the outline structure
    if outline and "error" not in outline:
        if "sections" not in outline:
            logger.error("Outline missing 'sections' key")
            raise KeyError("Generated outline is missing required 'sections' key")
        if not isinstance(outline.get("sections"), list):
            logger.error(
                f"Outline 'sections' is not a list: {type(outline.get('sections'))}"
            )
            raise TypeError("Generated outline 'sections' must be a list")
        logger.info(
            f"✓ Successfully generated outline with {len(outline['sections'])} sections"
        )
    elif outline and "error" in outline:
        logger.error(f"Outline generation returned error: {outline['error']}")
        raise ValueError(f"Outline generation error: {outline['error']}")
    else:
        logger.error("Outline is None or invalid")
        raise ValueError("Failed to generate valid outline")

    return outline


# Function: Generate video script


def generate_outline_qa_report(
    llm: Union[ChatOpenAI, ChatOllama], video_idea: str, outline: str
):
    """Generate QA report for outline with optional fact-checking"""
    OUTLINE_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        OUTLINE_QA_PROMPT_TEMPLATE_TEXT
    )
    outline_qa_chain = OUTLINE_QA_PROMPT_TEMPLATE | llm | StrOutputParser()
    outline_qa_response = outline_qa_chain.invoke({"outline": outline, **video_idea})
    outline_qa_response_json = safe_json_loads(
        outline_qa_response, context="outline_qa_report"
    )

    # Add fact-checking if SearXNG is configured
    fact_check_results = verify_facts_with_search(
        llm, json.dumps(outline), context="outline"
    )
    if fact_check_results:
        outline_qa_response_json["fact_check"] = fact_check_results

    return outline_qa_response_json


# Function: Verify facts with search


def verify_facts_with_search(
    llm: Union[ChatOpenAI, ChatOllama], content: str, context: str = "content"
) -> Optional[Dict]:
    """Verify factual claims in content using SearXNG search

    Args:
        llm: Language model for extraction and analysis
        content: Content to fact-check (JSON string or dict)
        context: Description of what's being checked

    Returns:
        Dict with verification results or None if search unavailable
    """
    logger = logging.getLogger("fact_checker")

    search_tool = get_search_tool()
    if not search_tool:
        logger.info("SearXNG not configured, skipping fact-checking")
        return None

    logger.info(f"Running fact-check on {context}...")

    # Extract verifiable claims using LLM
    extract_prompt = ChatPromptTemplate.from_template(
        """Analyze the following content and extract 3-5 specific, verifiable factual claims that can be checked via web search.
        Focus on technical details, version numbers, command syntax, package names, and URLs.
        
        Content: {content}
        
        Return ONLY a JSON array of claims (strings). Example: ["Python 3.9 was released", "pip is the package installer"]
        """
    )

    try:
        extract_chain = extract_prompt | llm | StrOutputParser()
        claims_response = extract_chain.invoke(
            {"content": str(content)[:2000]}
        )  # Limit content size
        claims = safe_json_loads(
            claims_response, context="claims_extraction", save_debug=False
        )

        if not claims or isinstance(claims, dict):
            logger.warning("No claims extracted or invalid format")
            return None

        logger.debug(f"Extracted {len(claims)} claims to verify")

        # Verify each claim
        verifications = []
        for claim in claims[:3]:  # Limit to 3 to avoid rate limiting
            try:
                search_results = search_tool.run(str(claim))
                verifications.append(
                    {
                        "claim": claim,
                        "search_results": search_results[:300],  # First 300 chars
                        "verified": len(search_results) > 50,  # Simple heuristic
                    }
                )
                time.sleep(1)  # Rate limiting
            except Exception as e:
                logger.warning(f"Search failed for claim '{claim}': {e}")

        return {
            "factcheck_performed": True,
            "verifications": verifications,
            "summary": f"Verified {len(verifications)} claims via web search",
        }

    except Exception as e:
        logger.error(f"Fact-checking failed: {e}")
        return {"factcheck_performed": False, "error": str(e)}


# Function: Generate outline based on QA report


def generate_outline_final(llm, outline_qa_report, outline_json):
    """Generate new outline based on QA report"""
    input_json = {"outline": outline_json, "outline_qa_report": outline_qa_report}
    outline_final = create_invoke_chain(
        llm, OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT, input_json
    )
    return safe_json_loads(outline_final, context="outline_final")


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
    sections_data = []

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
        sections_data.append({"name": section_name, "script": section_script})

        # Update summary for next iteration
        logging.info(f"Summarizing section: {section_name}")
        new_summary = summarize_script_section(llm, section_script)
        if running_summary == "No previous content.":
            running_summary = new_summary
        else:
            running_summary += f"\n\n{new_summary}"

    return full_script, sections_data


# Function: Generate QA for script


def generate_qa_report(
    llm: Union[ChatOpenAI, ChatOllama], title: str, level: str, sections_data: list
):
    """Generate QA report from script sections"""
    SCRIPT_QA_PROMPT_TEMPLATE = ChatPromptTemplate.from_template(
        SCRIPT_QA_PROMPT_TEMPLATE_TEXT
    )

    # --- Construct the script QA chain ---
    script_qa_chain = SCRIPT_QA_PROMPT_TEMPLATE | llm | StrOutputParser()

    aggregated_qa = {"sections": []}

    for section in sections_data:
        section_name = section["name"]
        section_script = section["script"]

        logging.info(f"Running QA for section: {section_name}")

        script_qa_response = script_qa_chain.invoke(
            {"title": title, "level": level, "content": section_script}
        )

        section_qa = safe_json_loads(
            script_qa_response, context=f"script_qa_{section_name}"
        )
        aggregated_qa["sections"].append(
            {"section_name": section_name, "qa_analysis": section_qa}
        )

    return aggregated_qa
