#!/usr/bin/env python3
"""Test SearXNG connection with LangChain"""

import os
from dotenv import load_dotenv

load_dotenv()

# Test direct connection first
import requests

searxng_url = os.getenv("SEARXNG_URL", "http://192.168.88.86:8888")
print(f"Testing SearXNG at: {searxng_url}")
print("=" * 60)

# Test 1: Basic search
print("\n1. Testing basic search...")
try:
    response = requests.get(
        f"{searxng_url}/search",
        params={"q": "Python programming", "format": "json"},
        timeout=10,
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Got {len(data.get('results', []))} results")
        if data.get("results"):
            print(f"  First result: {data['results'][0].get('title', 'N/A')}")
    else:
        print(f"✗ Error: {response.text[:200]}")
except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: LangChain wrapper
print("\n2. Testing LangChain SearxSearchWrapper...")
try:
    from langchain_community.utilities import SearxSearchWrapper

    search = SearxSearchWrapper(searx_host=searxng_url)
    result = search.run("test query")
    print(f"✓ LangChain wrapper works!")
    print(f"  Result preview: {result[:200]}")
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 60)
print("Test complete!")
