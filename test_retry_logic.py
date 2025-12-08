#!/usr/bin/env python3
"""Test script to verify retry logic and debugging functionality"""

import json
import logging
from functions import safe_json_loads, retry_with_backoff

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test")

print("=" * 60)
print("Testing safe_json_loads with various inputs")
print("=" * 60)

# Test 1: Valid JSON
print("\n1. Testing valid JSON...")
valid_json = '{"sections": [{"name": "Intro", "content": ["Point 1"]}]}'
result = safe_json_loads(valid_json, context="test_valid")
print(f"✓ Valid JSON parsed: {result is not None and 'error' not in result}")

# Test 2: JSON with markdown wrapper
print("\n2. Testing JSON with markdown wrapper...")
markdown_json = '```json\n{"sections": [{"name": "Test"}]}\n```'
result = safe_json_loads(markdown_json, context="test_markdown")
print(f"✓ Markdown-wrapped JSON parsed: {result is not None and 'error' not in result}")

# Test 3: Invalid JSON (should create debug file)
print("\n3. Testing invalid JSON (should create debug file)...")
invalid_json = '{"sections": [{"name": "Test", "content": ["incomplete'
result = safe_json_loads(invalid_json, context="test_invalid")
print(f"✓ Invalid JSON handled: {result is not None and 'error' in result}")
print(f"   Debug file should be created in debug_json_failures/")

# Test 4: Test retry decorator
print("\n4. Testing retry decorator...")
attempt_count = 0


@retry_with_backoff(max_retries=3, base_delay=0.1, exceptions=(ValueError,))
def failing_function():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ValueError(f"Attempt {attempt_count} failed")
    return "Success on attempt 3"


try:
    result = failing_function()
    print(f"✓ Retry decorator worked: {result}")
    print(f"   Took {attempt_count} attempts")
except Exception as e:
    print(f"✗ Retry decorator failed: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
