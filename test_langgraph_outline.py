#!/usr/bin/env python3
"""Test LangGraph outline generation with search"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from functions import (
    get_llm,
    generate_video_outline_with_langgraph,
)

logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("test_langgraph")

# Test data - topic that should trigger search
test_video_idea_search = {
    "title": "New Features in Python 3.13",
    "domain": "programming",
    "level": "Intermediate",
    "hook": "Discover the latest capabilities in Python 3.13",
    "tags": ["python", "programming", "new-features"],
    "tools": ["python", "pip"],
    "objectives": [
        "Understand new Python 3.13 features",
        "Learn when to use them",
        "See practical examples",
    ],
}

# Test data - general topic that shouldn't need search
test_video_idea_no_search = {
    "title": "Introduction to Variables in Programming",
    "domain": "programming",
    "level": "Beginner",
    "hook": "Learn the fundamentals of variables",
    "tags": ["programming", "basics", "variables"],
    "tools": [],
    "objectives": ["Understand what variables are", "Learn basic variable operations"],
}


def test_outline_with_search():
    """Test LangGraph outline generation with search-worthy topic"""
    logger.info("=" * 70)
    logger.info("TEST 1: Topic that should trigger search")
    logger.info("=" * 70)

    llm = get_llm("gpt-oss")

    try:
        outline = generate_video_outline_with_langgraph(llm, test_video_idea_search)

        if outline and "sections" in outline:
            logger.info(f"✓ Success! Generated {len(outline['sections'])} sections")
            for i, section in enumerate(outline["sections"][:3], 1):
                logger.info(f"  Section {i}: {section.get('name', 'Unnamed')}")
            return True
        else:
            logger.error("✗ Failed: No sections in outline")
            return False

    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_outline_without_search():
    """Test LangGraph outline generation with general topic"""
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST 2: General topic (may not need search)")
    logger.info("=" * 70)

    llm = get_llm("gpt-oss")

    try:
        outline = generate_video_outline_with_langgraph(llm, test_video_idea_no_search)

        if outline and "sections" in outline:
            logger.info(f"✓ Success! Generated {len(outline['sections'])} sections")
            for i, section in enumerate(outline["sections"][:3], 1):
                logger.info(f"  Section {i}: {section.get('name', 'Unnamed')}")
            return True
        else:
            logger.error("✗ Failed: No sections in outline")
            return False

    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    logger.info("Testing LangGraph Outline Generation")
    logger.info("")

    # Check if SearXNG is configured
    searxng_url = os.getenv("SEARXNG_URL")
    if searxng_url:
        logger.info(f"✓ SearXNG configured at: {searxng_url}")
    else:
        logger.warning("⚠ SearXNG not configured (search will be skipped)")

    logger.info("")

    # Run tests
    test1_passed = test_outline_with_search()
    test2_passed = test_outline_without_search()

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    logger.info(
        f"Test 1 (with search topic): {'✓ PASSED' if test1_passed else '✗ FAILED'}"
    )
    logger.info(f"Test 2 (general topic): {'✓ PASSED' if test2_passed else '✗ FAILED'}")
    logger.info("")

    if test1_passed and test2_passed:
        logger.info("✓ All tests passed!")
        sys.exit(0)
    else:
        logger.error("✗ Some tests failed")
        sys.exit(1)
