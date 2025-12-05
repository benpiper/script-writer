#!/usr/bin/env python3
"""Test SearXNG with POST and different formats"""

import requests

searxng_url = "http://192.168.88.86:8888"

print("Testing different SearXNG request methods...")
print("=" * 60)

# Test 1: POST with form data
print("\n1. Testing POST with form data...")
try:
    response = requests.post(
        f"{searxng_url}/search",
        data={"q": "Python programming", "format": "json"},
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ Success! Response length: {len(response.text)}")
        try:
            data = response.json()
            print(f"  Results: {len(data.get('results', []))}")
        except:
            print(f"  Not JSON, first 200 chars: {response.text[:200]}")
    else:
        print(f"✗ Failed")
except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: Plain search (HTML)
print("\n2. Testing plain HTML search...")
try:
    response = requests.get(
        f"{searxng_url}/search", params={"q": "Python programming"}, timeout=10
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"✓ HTML search works! Length: {len(response.text)}")
        if "results" in response.text.lower():
            print("  Contains search results")
    else:
        print(f"✗ Failed")
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 60)
