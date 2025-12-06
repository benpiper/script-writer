"""generate_titles.py"""

import argparse
import logging
import sys
from functions import get_llm

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("generate_titles")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Video Idea")
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
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Path to save the generated idea JSON (e.g., idea.json)",
    )
    return parser.parse_args()


def main():
    try:
        args = parse_arguments()
        llm = get_llm(args.model)

        print(f"\nGenerating comprehensive video idea for topic: '{args.topic}'...\n")

        # Import locally to avoid circular imports if any
        from functions import generate_video_idea_data, write_json

        idea_data = generate_video_idea_data(llm, args.topic, args.domain, args.level)

        print("=" * 40)
        print("GENERATED VIDEO IDEA")
        print("=" * 40)
        print(f"Hook: {idea_data.get('hook', 'N/A')}")
        print("\nSuggested Titles:")
        for t in idea_data.get("titles", []):
            print(f"- {t}")

        if args.save:
            write_json(idea_data, args.save)
            print(f"\nSaved idea to: {args.save}")
            print(
                f"To use this idea, run: uv run script-writer.py --input-file {args.save}"
            )

        print("=" * 40)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
