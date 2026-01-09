"""script-writer.py"""

import json
import logging
import argparse
import sys
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from functions import (
    get_llm,
    ask_approval,
    generate_video_outline,
    generate_video_outline_with_langgraph,
    generate_video_script,
    generate_qa_report,
    generate_outline_qa_report,
    generate_outline_final,
    write_json,
    write_markdown,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("script_writer")


import os
import shutil
import uuid
from slugify import slugify


class ScriptWriter:
    def __init__(self, input_file: str, model: str, use_langgraph: bool = True) -> None:
        self.input_file = input_file
        self.model = model
        self.use_langgraph = use_langgraph
        self.timestamp = uuid.uuid4().hex
        self.llm = get_llm(self.model)

        try:
            with open(self.input_file, "r") as f:
                self.video_idea_json = json.load(f)
        except Exception as e:
            logger.critical(f"Failed to load input file: {e}")
            raise e

        # Extract details from loaded JSON for logging/context if needed
        self.topic = self.video_idea_json.get("topic", "Unknown Topic")
        self.level = self.video_idea_json.get("level", "Beginner")

        # Validate input JSON structure
        if not isinstance(self.video_idea_json, dict):
            raise ValueError("Input JSON must be a dictionary")
        required_fields = ["title", "topic", "level"]
        for field in required_fields:
            if field not in self.video_idea_json:
                raise ValueError(f"Required field '{field}' missing from input JSON")

        # Check write permissions
        if not os.access('.', os.W_OK):
            raise PermissionError("No write permission in the current directory")

        # Create output directory
        topic_slug = slugify(self.video_idea_json.get("title", self.topic))[:50]
        self.output_dir = f"output/{self.timestamp}_{topic_slug}"
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self) -> None:
        logger.debug("Starting at %s", self.timestamp)
        debug_message = f"Topic: {self.topic}, Model: {self.model}"
        logger.debug(debug_message)

        # Use loaded JSON directly
        video_idea_json = self.video_idea_json

        # Save a copy of the input idea for reference in the output folder
        self.write_artifact(video_idea_json, "1_idea.json")

        # Skip Idea QA as requested
        # Proceed directly to Outline Generation

        outline_json = self.step_outline(video_idea_json)

        self.write_artifact(outline_json, "3_outline.json")

        outline_qa_report = self.step_outline_qa(video_idea_json, outline_json)
        if outline_qa_report is None:
            raise ValueError("Failed to generate outline QA report")
        self.write_artifact(outline_qa_report, "4_outline_qa.json")

        outline_final_json = self.step_outline_final(outline_qa_report, outline_json)
        if outline_final_json is None:
            raise ValueError("Failed to generate final outline")
        self.write_artifact(outline_final_json, "5_outline_final.json")

        script_md, sections_data = self.step_script(outline_final_json)
        self.write_artifact(script_md, "6_script.md", is_markdown=True)

        script_qa_response = self.step_script_qa(sections_data, video_idea_json)
        self.write_artifact(script_qa_response, "7_script_qa.json")

    def step_outline(self, video_idea_json: Dict[str, Any]) -> Dict[str, Any]:
        approval_status = False
        outline_json = None
        while not approval_status:
            logger.info("Generating video outline")
            if self.use_langgraph:
                logger.info("Using LangGraph with autonomous search")
                outline_json = generate_video_outline_with_langgraph(
                    self.llm, video_idea_json
                )
            else:
                logger.info("Using standard outline generation")
                outline_json = generate_video_outline(self.llm, video_idea_json)
            logger.info("Outline JSON")
            logger.info(outline_json)
            if outline_json is None:
                raise Exception("Failed to generate outline")
            approval_status = ask_approval()
        return outline_json

    def step_outline_qa(self, video_idea_json: Dict[str, Any], outline_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return generate_outline_qa_report(self.llm, video_idea_json, outline_json)

    def step_outline_final(self, outline_qa_report: Dict[str, Any], outline_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        logger.info("Correcting outline based on QA feedback")
        return generate_outline_final(self.llm, outline_qa_report, outline_json)

    def step_script(self, outline_final_json: Dict[str, Any]) -> Tuple[str, Any]:
        approval_status = False
        script_md = None
        sections_data = None
        while not approval_status:
            logger.info("Generating script")
            script_md, sections_data = generate_video_script(
                self.llm, outline_final_json
            )
            if script_md is None:
                logger.error("Failed to generate script, retrying...")
                continue
            approval_status = ask_approval()
        logger.info("Script generated and approved.")
        logger.debug(script_md)
        return script_md, sections_data

    def step_script_qa(self, video_script_sections: Any, video_idea_json: Dict[str, Any]) -> Any:
        logger.info("Starting script QA")
        return generate_qa_report(
            self.llm, video_idea_json["title"], self.level, video_script_sections
        )

    def write_artifact(self, data: Any, suffix: str, is_markdown: bool = False) -> None:
        filename = os.path.join(self.output_dir, suffix)
        logger.info(f"Writing to {filename}")
        if is_markdown:
            write_markdown(data, filename)
        else:
            write_json(data, filename)


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI Script Writer")
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="Path to the idea JSON file",
    )
    parser.add_argument("--model", type=str, default="gpt-oss", help="LLM model to use")
    parser.add_argument(
        "--use-langgraph",
        action="store_true",
        default=True,
        help="Use LangGraph for outline generation with autonomous search (default: True)",
    )
    parser.add_argument(
        "--no-langgraph",
        dest="use_langgraph",
        action="store_false",
        help="Disable LangGraph and use standard outline generation",
    )

    return parser.parse_args()


def main():
    try:
        args = parse_arguments()
        writer = ScriptWriter(args.input_file, args.model, args.use_langgraph)
        writer.run()
    except KeyboardInterrupt:
        logger.warning("Script execution interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        # Cleanup output directory if it exists
        if 'writer' in locals() and hasattr(writer, 'output_dir'):
            shutil.rmtree(writer.output_dir, ignore_errors=True)
            logger.info(f"Cleaned up output directory: {writer.output_dir}")
        sys.exit(1)


if __name__ == "__main__":
    main()
