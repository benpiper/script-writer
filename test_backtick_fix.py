#!/usr/bin/env python3
"""Test backtick fix"""

import json

# The actual problematic JSON pattern
bad_json = """
{
  "text": "The outline refers to `dataset[\\"test\\"]` after a split"
}
"""

print("Testing backtick fix...")
print("=" * 60)
print("Original JSON (invalid):")
print(bad_json)
print()

# Apply the fix
fixed = bad_json.replace("`", "'")

print("Fixed JSON:")
print(fixed)
print()

try:
    result = json.loads(fixed)
    print("✓ Successfully parsed!")
    print("Result:", json.dumps(result, indent=2))
except json.JSONDecodeError as e:
    print(f"✗ Still invalid: {e}")
