""" script-writer.py """
import json
import logging
import argparse
import sys
from datetime import datetime
from functions import (
    get_llm, ask_approval, generate_video_idea, generate_idea_qa_report,
    generate_video_outline, generate_video_script, generate_qa_report,
    generate_outline_qa_report, generate_outline_final, generate_script_final,
    write_json, write_markdown, select_title
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("script_writer")


class ScriptWriter:
    def __init__(self, topic, domain, level, model):
        self.topic = topic
        self.domain = domain
        self.level = level
        self.model = model
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.llm = get_llm(self.model)
        self.filename_suffix = None

    def run(self):
        logger.debug("Starting at %s", self.timestamp)
        debug_message = f"Topic: {self.topic}, Domain: {self.domain}, Level: {self.level}, Model: {self.model}"
        logger.debug(debug_message)

        video_idea_json = self.step_ideation()
        
        # Select title
        selected_title = select_title(video_idea_json)
        video_idea_json['title'] = selected_title
        
        self.filename_suffix = video_idea_json['title'].replace(" ", "-").lower()
        
        self.write_artifact(video_idea_json, "1_idea.json")

        video_idea_qa_json = self.step_ideation_qa(video_idea_json)
        
        # Ensure selected title is preserved
        if selected_title:
            video_idea_qa_json['title'] = selected_title
            
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

        video_script = self.step_script(outline_final_json)
        self.write_artifact(video_script, "6_script.md", is_markdown=True)

        script_qa_response = self.step_script_qa(video_script, video_idea_json)
        self.write_artifact(script_qa_response, "7_script_qa.json")

        video_script_final = self.step_script_final(script_qa_response, video_script)
        self.write_artifact(video_script_final, "8_script_final.md", is_markdown=True)

    def step_ideation(self):
        logger.info("Generating video idea")
        approval_status = False
        video_idea_json = None
        while not approval_status:
            video_idea_json = generate_video_idea(
                self.llm, self.topic, self.domain, self.level)
            logger.info("Video idea JSON")
            logger.info(video_idea_json)
            approval_status = ask_approval()
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
        video_script = None
        while not approval_status:
            while video_script is None:
                logger.info("Generating script")
                video_script = generate_video_script(self.llm, outline_final_json)
            approval_status = ask_approval()
        logger.info("Script generated.")
        logger.debug(video_script)
        return video_script

    def step_script_qa(self, video_script, video_idea_json):
        logger.info("Starting script QA")
        return generate_qa_report(
            self.llm, video_idea_json['title'], self.level, video_script)

    def step_script_final(self, script_qa_response, video_script):
        video_script_final = None
        while video_script_final is None:
            logger.info("Rewriting script with QA corrections")
            video_script_final = generate_script_final(
                self.llm, script_qa_response, video_script)
        return video_script_final

    def write_artifact(self, data, suffix, is_markdown=False):
        filename = f"output/{self.timestamp}_{self.filename_suffix}_{suffix}"
        logger.info(f"Writing to {filename}")
        if is_markdown:
            write_markdown(data, filename)
        else:
            write_json(data, filename)


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Script Writer")
    parser.add_argument("--topic", type=str, default="How to tell if an IT job listing is a ghost job", help="Video topic")
    parser.add_argument("--domain", type=str, default="information technology", help="Video domain")
    parser.add_argument("--level", type=str, default="Beginner", help="Target audience level")
    parser.add_argument("--model", type=str, default="gpt-oss", help="LLM model to use")
    return parser.parse_args()


def main():
    args = parse_arguments()
    writer = ScriptWriter(args.topic, args.domain, args.level, args.model)
    writer.run()


if __name__ == "__main__":
    main()
