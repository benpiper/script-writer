#!/usr/bin/env python3
"""Test DuckDuckGo search as fallback"""

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    search = DuckDuckGoSearchRun()
    result = search.run("Python programming latest version")
    print("✓ DuckDuckGo search works!")
    print(f"Result preview:\n{result[:300]}")
except ImportError as e:
    print(f"✗ Need to install: pip install duckduckgo-search")
    print(f"Error: {e}")
except Exception as e:
    print(f"✗ Error: {e}")
