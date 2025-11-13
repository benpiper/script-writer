""" script-writer.py """
import json
import logging
from datetime import datetime
from langchain_openai import ChatOpenAI
#from langchain_ollama import ChatOllama
from functions import generate_video_idea, generate_video_outline, generate_video_script, generate_qa_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("script_writer")


def main():
    """ main """
    logger.debug("Starting")
    llm = ChatOpenAI(model="gpt-5-nano", temperature=1,
                     use_responses_api=True, reasoning_effort="low")

    """ llm = ChatOllama(
        model="codellama:latest",
        temperature=1.0,
        reasoning=None,
        num_predict=-1,        # similar to max tokens / num_predict
        validate_model_on_init=True,
        base_url="http://192.168.88.86:11434"
    ) """

    logger.info("Generating video idea")

    MAX_MINUTES = 30
    TOPIC = "why and how to use tiktoken in python"
    LEVEL = "Beginner"
    logger.debug("Max minutes: %s, Topic: %s, Level: %s", MAX_MINUTES, TOPIC, LEVEL)
    video_idea_json = generate_video_idea(llm, MAX_MINUTES, TOPIC, LEVEL)
    logger.info("Video idea JSON")
    logger.info(video_idea_json)

    filename_suffix = video_idea_json['title'].replace(" ", "-").lower()

    logger.info("Generating video outline")

    outline_json = generate_video_outline(llm, video_idea_json)
    logger.debug(outline_json)

    logger.info("Outline JSON:")
    # logger.info(outline_json)

    # write outline to file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    logger.info("Writing outline to file")
    outline_filename = f"output/{filename_suffix}_outline_{timestamp}.json"
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
    script_filename = f"output/{filename_suffix}_script_{timestamp}.md"
    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(final_script_markdown)

    logger.info("Starting script QA")

    script_qa_response = generate_qa_report(
        llm, video_idea_json['title'], LEVEL, final_script_markdown)
    # write script QA report to file
    script_qa_filename = f"output/{filename_suffix}_script_qa_{timestamp}.md"
    with open(script_qa_filename, "w", encoding="utf-8") as f:
        f.write(script_qa_response)


if __name__ == "__main__":
    main()
