import os
import json
import logging
import re
import time
from datetime import datetime, timezone
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from functions import generate_video_idea, generate_video_outline, generate_video_script

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("script_writer")


def main():
    """ main """
    logger.debug("Starting")
    llm = ChatOpenAI(model="gpt-5-nano", temperature=1,
                     use_responses_api=True, reasoning_effort="low")

    """ llm = ChatOllama(
        model="codellama:latest",      # change to your local Ollama model name
        temperature=1.0,
        reasoning=None,          # or True/False to match reasoning_effort
        num_predict=-1,        # similar to max tokens / num_predict
        validate_model_on_init=True,
        base_url="http://192.168.88.86:11434"
    ) """

    logger.info("Generating video idea")

    MAX_MINUTES = 20
    TOPIC = "current limitations of AI and LLMs"
    LEVEL = "Beginner"

    video_idea_json = generate_video_idea(llm, MAX_MINUTES, TOPIC, LEVEL)
    logger.info("Video idea JSON")
    logger.info(video_idea_json)

    filename_suffix = video_idea_json['title'].replace(" ", "-")

    logger.info("Generating video outline")

    outline_json = generate_video_outline(llm, video_idea_json)
    logger.debug(outline_json)

    logger.info("Outline JSON:")
    # logger.info(outline_json)

    # write outline to file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.info("Writing outline to file")
    outline_filename = f"{filename_suffix}_outline_{timestamp}.json"
    with open(outline_filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(outline_json, indent=2, ensure_ascii=False))

    logger.info("Generating video script")

    video_script_json = generate_video_script(llm, outline_json)
    final_script_markdown = video_script_json.get(
        "script_markdown", "").strip()

    logger.info("Final script generated.")
    # logger.info(final_script_markdown)

    # write script to file
    logger.info("Writing script to file")
    # timestamp = int(time.time())
    script_filename = f"{filename_suffix}_script_{timestamp}.md"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(final_script_markdown)

    logger.info("Starting script QA")

    # --- Prompt: QA Analysis ---

    QA_PROMPT_TEMPLATE_TEXT = """
        Analyze the provided content for accuracy, relevance, logical consistency, clarity, completeness, and audience appropriateness.
        - Title: {title}
        - Audience level: {level}
        Produce a concise, actionable report with the following sections:

        - Summary (one short sentence): state the content’s main claim or purpose and overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

        - Correctness: identify major factual errors. For each issue include why it is incorrect (brief explanation).

        - Consistency: identify internal contradictions, mismatched terminology, or logical gaps.

        - Completeness and Structure: The script should be a complete script, not a draft or outline. List missing points or structural problems (e.g., poor flow, missing headings).

        - Audience Fit: state whether content matches the intended audience. Do not mention inclusivity.

        Formatting requirements for your response:
        - Use Markdown headings for each numbered section above (e.g., "### 1. Summary").
        - Under remaining sections, present all suggestions as Markdown bullet lists.

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
    script_qa_filename = f"{filename_suffix}_script_qa_{timestamp}.md"
    with open(script_qa_filename, "w", encoding="utf-8") as f:
        f.write(script_qa_response)


if __name__ == "__main__":
    main()
