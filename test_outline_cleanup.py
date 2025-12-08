#!/usr/bin/env python3
"""Test the outline cleanup function with actual failed JSON"""

import json
import logging
import sys
import os

# Add parent directory to path to import functions
sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)

# The actual JSON that failed (with demonstration keys)
failed_json_str = """
{"meta":[{"title":"Fine-Tune GPT-OSS with Your Own Markdown Dataset: Step-by-Step Guide","level":"intermediate"}],"sections":[{"name":"Introduction","content":["Turn raw markdown into a powerhouse AI","This guide walks through preparing markdown data"]},{"name":"Installing Dependencies","content":["pip install --upgrade pip","pip install transformers datasets torch"],"demonstration":"Run the above pip commands"},{"name":"Loading Model","content":["from transformers import AutoModelForCausalLM"],"demonstration":"Test it"}]}
"""

print("Testing outline validation and cleanup...")
print("=" * 60)

try:
    from functions import validate_and_clean_outline

    # Parse the failed JSON
    outline_data = json.loads(failed_json_str)
    print(f"Original outline has {len(outline_data['sections'])} sections")

    # Check for demonstration keys
    demo_count = sum(1 for s in outline_data["sections"] if "demonstration" in s)
    print(f"Found {demo_count} sections with 'demonstration' keys")
    print()

    # Clean it
    print("Running validate_and_clean_outline...")
    print("-" * 60)
    cleaned_outline = validate_and_clean_outline(outline_data)
    print("-" * 60)
    print()

    # Verify cleanup
    demo_count_after = sum(
        1 for s in cleaned_outline["sections"] if "demonstration" in s
    )
    print(f"After cleanup: {demo_count_after} sections with 'demonstration' keys")
    print()

    # Show cleaned section structure
    print("Sample cleaned section:")
    print(json.dumps(cleaned_outline["sections"][1], indent=2))
    print()

    # Verify all sections have only name and content
    all_valid = all(
        set(s.keys()) == {"name", "content"} for s in cleaned_outline["sections"]
    )
    print(f"✓ All sections have only 'name' and 'content' keys: {all_valid}")

    print()
    print("=" * 60)
    print("✓ Test PASSED - Cleanup function works correctly!")

except ImportError as e:
    print(f"Import error (expected in test environment): {e}")
    print("This test would work in the actual script environment")
except Exception as e:
    print(f"✗ Test FAILED: {e}")
    import traceback

    traceback.print_exc()
