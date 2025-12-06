"""generate_titles.py"""

import argparse
import logging
import sys
from functions import get_llm, generate_titles

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("generate_titles")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generate Video Titles")
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
        llm = get_llm(args.model)

        print(f"\nGenerating titles for topic: '{args.topic}'...\n")

        titles = generate_titles(llm, args.topic, args.domain, args.level)

        print("=" * 40)
        print("SUGGESTED TITLES")
        print("=" * 40)
        print(titles)
        print("=" * 40)

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
