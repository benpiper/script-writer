""" script-writer.py """
import json
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from functions import get_llm, generate_video_idea, generate_video_outline, generate_video_script, generate_qa_report, generate_outline_qa_report

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("script_writer")


def main():
    """ main """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.debug("Starting at %s", timestamp)

    llm = get_llm("gpt-oss")

    logger.info("Generating video idea")

    MAX_MINUTES = 30
    TOPIC = "Create a fun GraphQL API using Python and mock data about cheese"
    DOMAIN = "information technology"
    LEVEL = "Beginner"
    debug_message = f"Max minutes: {MAX_MINUTES}, Topic: {TOPIC}, Domain: {DOMAIN}, Level: {LEVEL}"
    logger.debug(debug_message)

    # Generate video idea

    video_idea_json = generate_video_idea(
        llm, MAX_MINUTES, TOPIC, DOMAIN, LEVEL)
    logger.info("Video idea JSON")
    logger.info(video_idea_json)

    filename_suffix = video_idea_json['title'].replace(" ", "-").lower()

    # write video idea to file
    logger.info("Writing video idea to file")
    idea_filename = f"output/{timestamp}_{filename_suffix}_idea.md"
    with open(idea_filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(video_idea_json, indent=2, ensure_ascii=False))

    # Generate video outline

    logger.info("Generating video outline")

    outline_json = generate_video_outline(llm, video_idea_json)
    logger.debug(outline_json)

    # write outline to file
    logger.info("Writing outline to file")
    outline_filename = f"output/{timestamp}_{filename_suffix}_outline.json"
    with open(outline_filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(outline_json, indent=2, ensure_ascii=False))

    # Generate outline QA report
    outline_qa_report = generate_outline_qa_report(
        llm, video_idea_json, outline_json)
    logger.debug(outline_qa_report)
    if (outline_qa_report['decision'] == "fail"):
        logger.info("Outline QA failed: %s", outline_qa_report["reason"])
        raise Exception

    # write outline QA report to file
    logger.info("Writing outline QA report to file")
    outline_qa_filename = f"output/{timestamp}_{filename_suffix}_outline_qa.json"
    with open(outline_qa_filename, "w", encoding="utf-8") as f:
        f.write(json.dumps(outline_qa_report, indent=2, ensure_ascii=False))

    # Generate video script

    logger.info("Generating video script")

    video_script_json = generate_video_script(llm, outline_json)
    final_script_markdown = video_script_json.get(
        "script_markdown", "").strip()

    logger.info("Final script generated.")
    # logger.info(final_script_markdown)

    # write script to file
    logger.info("Writing script to file")
    script_filename = f"output/{timestamp}_{filename_suffix}_script.md"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(final_script_markdown)

    # Generating script QA

    logger.info("Starting script QA")

    script_qa_response = generate_qa_report(
        llm, video_idea_json['title'], LEVEL, final_script_markdown)
    # write script QA report to file
    script_qa_filename = f"output/{timestamp}_{filename_suffix}_script_qa.md"
    with open(script_qa_filename, "w", encoding="utf-8") as f:
        f.write(script_qa_response)


if __name__ == "__main__":
    main()
