import logging
import json
from functions import safe_json_loads

# Mock logging to avoid clutter
logging.basicConfig(level=logging.CRITICAL)


def test_safe_json_loads():
    test_cases = [
        # Case 1: Valid JSON
        ('{"key": "value"}', {"key": "value"}),
        # Case 2: Markdown block
        ('```json\n{"key": "value"}\n```', {"key": "value"}),
        # Case 3: Text before and after
        ('Here is the JSON: {"key": "value"} Hope it helps!', {"key": "value"}),
        # Case 4: Trailing comma (if we implemented fix)
        ('{"key": "value",}', {"key": "value"}),
        # Case 5: Nested objects
        (
            'Some text {"outer": {"inner": "value"}} more text',
            {"outer": {"inner": "value"}},
        ),
        # Case 6: Array
        ('Here is a list: ["item1", "item2"]', ["item1", "item2"]),
    ]

    passed = 0
    for i, (input_text, expected) in enumerate(test_cases):
        result = safe_json_loads(input_text)
        if result == expected:
            print(f"Case {i + 1}: PASS")
            passed += 1
        else:
            print(f"Case {i + 1}: FAIL")
            print(f"  Input: {input_text}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")

    print(f"\nPassed {passed}/{len(test_cases)}")


if __name__ == "__main__":
    test_safe_json_loads()
