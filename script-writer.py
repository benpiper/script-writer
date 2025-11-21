""" script-writer.py """
import json
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from functions import get_llm, generate_video_idea, generate_idea_qa_report, generate_video_outline, generate_video_script, generate_qa_report, generate_outline_qa_report, generate_outline_final, write_json, write_markdown

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("script_writer")


def main():
    """ main """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.debug("Starting at %s", timestamp)

    llm = get_llm("gpt-oss")

    logger.info("Generating video idea")

    TOPIC: str = "express.js"
    DOMAIN: str = "Information technology"
    LEVEL: str = "Beginner"
    debug_message = f"Topic: {TOPIC}, Domain: {DOMAIN}, Level: {LEVEL}"
    logger.debug(debug_message)

    # Generate video idea

    video_idea_json = generate_video_idea(
        llm, TOPIC, DOMAIN, LEVEL)
    logger.info("Video idea JSON")
    logger.info(video_idea_json)

    filename_suffix = video_idea_json['title'].replace(" ", "-").lower()

    # write video idea to file
    logger.info("Writing video idea to file")
    idea_filename = f"output/{timestamp}_{filename_suffix}_1_idea.json"
    write_json(video_idea_json, idea_filename)

    # QA idea

    video_idea_qa_json = generate_idea_qa_report(llm, video_idea_json)
    # write video idea to file
    logger.info("Writing post-QA video idea to file")
    idea_qa_filename = f"output/{timestamp}_{filename_suffix}_2_idea_qa.json"
    write_json(video_idea_qa_json, idea_qa_filename)

    if ("error" in video_idea_qa_json):
        raise Exception

    # Generate video outline

    logger.info("Generating video outline")

    outline_json = generate_video_outline(llm, video_idea_qa_json)
    logger.debug(outline_json)

    # write outline to file
    logger.info("Writing outline to file")
    outline_filename = f"output/{timestamp}_{filename_suffix}_3_outline.json"
    write_json(outline_json, outline_filename)

    # Generate outline QA report
    outline_qa_report = generate_outline_qa_report(
        llm, video_idea_json, outline_json)
    logger.debug(outline_qa_report)
    if (outline_qa_report['decision'] == "fail"):
        logger.info("Outline QA failed: %s", outline_qa_report["reason"])
        raise Exception

    # write outline QA report to file
    logger.info("Writing outline QA report to file")
    outline_qa_filename = f"output/{timestamp}_{filename_suffix}_4_outline_qa.json"
    write_json(outline_qa_report, outline_qa_filename)

    # Correct outline based on QA findings
    logger.info("Correcting outline based on QA feedback")
    outline_final_json = generate_outline_final(
        llm, outline_qa_report, outline_json)
    outline_final_filename = f"output/{timestamp}_{filename_suffix}_5_outline_final.json"
    write_json(outline_final_json, outline_final_filename)

    # Generate video script
    video_script = None
    while video_script is None:
        logger.info("Generating script")
        video_script = generate_video_script(llm, outline_final_json)
    # final_script_markdown = video_script_json.get("script_markdown", "").strip()

    logger.info("Script generated.")

    # write script to file
    logger.info("Writing script to file")
    script_filename = f"output/{timestamp}_{filename_suffix}_6_script.md"
    write_markdown(video_script, script_filename)

    # Generating script QA

    logger.info("Starting script QA")

    script_qa_response = generate_qa_report(
        llm, video_idea_json['title'], LEVEL, video_script)
    # write script QA report to file
    script_qa_filename = f"output/{timestamp}_{filename_suffix}_7_script_qa.json"
    write_json(script_qa_response, script_qa_filename)


if __name__ == "__main__":
    main()
