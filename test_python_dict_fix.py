#!/usr/bin/env python3
"""Test Python dict to JSON conversion"""

import json

# The actual problematic Python dict syntax
python_dict_str = """
{'decision': 'pass',
 'reason': 'Test reason',
 'quality': 'clear and consistent',
 'correctness': [],
 'completeness': [],
 'consistency': []}
"""

print("Testing Python dict to JSON conversion...")
print("=" * 60)
print("Original (Python dict syntax):")
print(python_dict_str)
print()

# Apply the fix
fixed = python_dict_str.replace("'", '"')

print("Fixed (JSON syntax):")
print(fixed)
print()

try:
    result = json.loads(fixed)
    print("✓ Successfully parsed!")
    print("Result keys:", list(result.keys()))
except json.JSONDecodeError as e:
    print(f"✗ Still invalid: {e}")
