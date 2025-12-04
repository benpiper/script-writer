FROM astral/uv:python3.12-bookworm-slim

COPY *.py .
COPY pyproject.toml .
RUN uv sync
CMD ["uv", "run", "script-writer.py"]
