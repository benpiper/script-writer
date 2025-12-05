#!/usr/bin/env python3
"""Test string concatenation fix"""

import json
import re

# The actual problematic JSON from the debug file (simplified)
bad_json = """
{
  "sections": [
    {
      "name": "Test",
      "content": [
        "text1" + "text2" + "text3"
      ]
    }
  ]
}
"""

print("Testing string concatenation fix...")
print("=" * 60)
print("Original JSON (invalid):")
print(bad_json)
print()

# Apply the fix
fixed = re.sub(r'"\s*\+\s*"', "", bad_json)

print("Fixed JSON:")
print(fixed)
print()

try:
    result = json.loads(fixed)
    print("✓ Successfully parsed!")
    print("Result:", json.dumps(result, indent=2))
except json.JSONDecodeError as e:
    print(f"✗ Still invalid: {e}")
