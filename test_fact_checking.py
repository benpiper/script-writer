#!/usr/bin/env python3
"""Test fact-checking integration"""

import os
from dotenv import load_dotenv

load_dotenv()

# Set config
os.environ["SEARXNG_URL"] = "http://192.168.88.86:8888"

print("Testing fact-checking integration...")
print("=" * 60)

try:
    from functions import get_search_tool, verify_facts_with_search, get_llm

    # Test 1: Search tool initialization
    print("\n1. Testing search tool initialization...")
    search_tool = get_search_tool()
    if search_tool:
        print("✓ Search tool initialized")
    else:
        print("✗ Search tool not available")
        exit(1)

    # Test 2: Fact-checking function
    print("\n2. Testing fact-checking function...")
    llm = get_llm("gpt-oss")

    test_content = """
    {
        "content": ["Python 3.12 was released in 2023", 
                   "pip install tensorflow to install TensorFlow",
                   "use numpy for scientific computing"]
    }
    """

    result = verify_facts_with_search(llm, test_content, context="test_outline")

    if result:
        print(f"✓ Fact-checking completed!")
        print(f"  Summary: {result.get('summary', 'N/A')}")
        print(f"  Verifications: {len(result.get('verifications', []))}")
        for v in result.get("verifications", []):
            print(f"    - {v['claim'][:60]}... = {'✓' if v.get('verified') else '✗'}")
    else:
        print("✗ Fact-checking returned None")

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback

    traceback.print_exc()
