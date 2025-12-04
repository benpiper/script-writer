"""script-writer.py"""

import json
import logging
import argparse
import sys
from datetime import datetime
from functions import (
    get_llm,
    ask_approval,
    generate_video_idea,
    generate_idea_qa_report,
    generate_video_outline,
    generate_video_script,
    generate_qa_report,
    generate_outline_qa_report,
    generate_outline_final,
    write_json,
    write_markdown,
    select_title,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("script_writer")


import os
from slugify import slugify


class ScriptWriter:
    def __init__(self, topic, domain, level, model):
        self.topic = topic
        self.domain = domain
        self.level = level
        self.model = model
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.llm = get_llm(self.model)
        self.filename_suffix = None

        # Create output directory
        topic_slug = slugify(self.topic)
        self.output_dir = f"output/{self.timestamp}_{topic_slug}"
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        logger.debug("Starting at %s", self.timestamp)
        debug_message = f"Topic: {self.topic}, Domain: {self.domain}, Level: {self.level}, Model: {self.model}"
        logger.debug(debug_message)

        video_idea_json = self.step_ideation()

        # Select title
        selected_title = select_title(video_idea_json)
        video_idea_json["title"] = selected_title

        self.filename_suffix = slugify(video_idea_json["title"])

        self.write_artifact(video_idea_json, "1_idea.json")

        video_idea_qa_json = self.step_ideation_qa(video_idea_json)

        # Ensure selected title is preserved
        if selected_title:
            video_idea_qa_json["title"] = selected_title

        self.write_artifact(video_idea_qa_json, "2_idea_qa.json")

        if "error" in video_idea_qa_json:
            logger.error("Error in Idea QA")
            raise Exception("Error in Idea QA")

        outline_json = self.step_outline(video_idea_qa_json)
        self.write_artifact(outline_json, "3_outline.json")

        outline_qa_report = self.step_outline_qa(video_idea_json, outline_json)
        self.write_artifact(outline_qa_report, "4_outline_qa.json")

        if outline_qa_report is None:
            raise Exception("Error in Outline QA")

        outline_final_json = self.step_outline_final(outline_qa_report, outline_json)
        self.write_artifact(outline_final_json, "5_outline_final.json")

        if outline_final_json is None:
            raise Exception("Error in Final Outline")

        script_md, sections_data = self.step_script(outline_final_json)
        self.write_artifact(script_md, "6_script.md", is_markdown=True)

        script_qa_response = self.step_script_qa(sections_data, video_idea_json)
        self.write_artifact(script_qa_response, "7_script_qa.json")

    def step_ideation(self):
        logger.info("Generating video idea")
        approval_status = False
        video_idea_json = None
        while not approval_status:
            video_idea_json = generate_video_idea(
                self.llm, self.topic, self.domain, self.level
            )
            logger.info("Video idea JSON")
            logger.info(video_idea_json)

            if video_idea_json is None:
                raise Exception("Failed to generate valid JSON for video idea")

            if "error" in video_idea_json:
                raise Exception(f"Video Ideation Error: {video_idea_json['error']}")

            # approval_status = ask_approval()
            approval_status = True  # Auto-approve for now as requested by user modification implies skipping manual approval
        return video_idea_json

    def step_ideation_qa(self, video_idea_json):
        return generate_idea_qa_report(self.llm, video_idea_json)

    def step_outline(self, video_idea_qa_json):
        approval_status = False
        outline_json = None
        while not approval_status:
            logger.info("Generating video outline")
            outline_json = generate_video_outline(self.llm, video_idea_qa_json)
            logger.info("Outline JSON")
            logger.info(outline_json)
            if outline_json is None:
                raise Exception("Failed to generate outline")
            approval_status = ask_approval()
        return outline_json

    def step_outline_qa(self, video_idea_json, outline_json):
        return generate_outline_qa_report(self.llm, video_idea_json, outline_json)

    def step_outline_final(self, outline_qa_report, outline_json):
        logger.info("Correcting outline based on QA feedback")
        return generate_outline_final(self.llm, outline_qa_report, outline_json)

    def step_script(self, outline_final_json):
        approval_status = False
        script_md = None
        sections_data = None
        while not approval_status:
            while script_md is None:
                logger.info("Generating script")
                script_md, sections_data = generate_video_script(
                    self.llm, outline_final_json
                )
            approval_status = ask_approval()
        logger.info("Script generated.")
        logger.debug(script_md)
        return script_md, sections_data

    def step_script_qa(self, video_script_sections, video_idea_json):
        logger.info("Starting script QA")
        return generate_qa_report(
            self.llm, video_idea_json["title"], self.level, video_script_sections
        )

    def write_artifact(self, data, suffix, is_markdown=False):
        filename = os.path.join(self.output_dir, suffix)
        logger.info(f"Writing to {filename}")
        if is_markdown:
            write_markdown(data, filename)
        else:
            write_json(data, filename)


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Script Writer")
    parser.add_argument(
        "--topic",
        type=str,
        default="How to tell if an IT job listing is a ghost job",
        help="Video topic",
    )
    parser.add_argument(
        "--domain", type=str, default="information technology", help="Video domain"
    )
    parser.add_argument(
        "--level", type=str, default="Beginner", help="Target audience level"
    )
    parser.add_argument("--model", type=str, default="gpt-oss", help="LLM model to use")
    return parser.parse_args()


def main():
    try:
        args = parse_arguments()
        writer = ScriptWriter(args.topic, args.domain, args.level, args.model)
        writer.run()
    except KeyboardInterrupt:
        logger.warning("Script execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
