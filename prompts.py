
# --- Prompt: Generate Video Idea ---
IDEATION_PROMPT_TEMPLATE_TEXT = """
        Find a trending video idea for {topic}.
        Begin with a concise checklist (3-7 bullets) of what you will do; keep items conceptual, not implementation-level. Do not output this checklist.
        Generate an idea for a video that can be quickly recorded and published, guided by the following requirements:
        - Inputs:
        - Topic: {topic} (string)
        - Audience level: {level} (string)

        - Output Format
        Return your answer as valid JSON using the following format:

            {{
                "title": "<string: SEO-optimized title of the video>",
                "hook": "<string: 3-line hook>",
                "tags": ["tag 1", "tag 2", "tag 3"],
                "tools": ["Tool or framework 1", "Tool or framework 2"]
            }}

        - Output Constraints:
        - Only return a single JSON object per response.

        After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
        If validation fails, self-correct and return the correct JSON error object.

        - Example output
            {{
                "title": "How to write a Hello World program in Python",
                "tools": ["Python", "VS Code"]
            }}
        """

# --- Prompt: Generate Outline ---
OUTLINE_PROMPT_TEMPLATE = """
        Begin with a checklist of the main planning and sequencing steps you will follow before creating the outline. Do not output this checklist.
        Create a comprehensive, detailed outline for a video using the structured input provided.

        Input JSON structure:
        ```
        {{
            "title": "{title}",
            "tools": {tools},
            "hook": "{hook}"
        }}
        ```

        Guidelines:
        - Stay strictly within the scope defined by the input.
        - Exclude self-paced exercises; all demonstrations should be incorporated within the video outline.
        - Carefully design the outline to ensure it fully addresses the content indicated in the title.
        - Arrange all sections and demonstration steps in a clear, logical sequence.
        - For the final section, refrain from including next steps, recommendations, or external/additional resources.

        If 'title' or 'tools' fields are missing or not the correct type, respond with the following JSON object:
        ```
        {{"error": "Missing or invalid input fields."}}
        ```

        After outlining, validate that each section directly supports the provided inputs, and confirm that all demonstrations are video-based and in logical order.
        If any guideline is not fully met, correct the outline before producing your final output.

        # Output Format
        - Return a JSON object structured as:
        ```
        {{
            "sections": [
            {{ "name": "<string>", "content": [<string>, ...] }}
            ]
        }}
        ```
        - 'sections' should be an array of section objects.
        - Each section object includes:
        - 'name': the title of the section (string)
        - 'content': an array of strings detailing the main points, demonstration steps, or explanations.

        """

# --- Prompt: Generate script ---
SCRIPT_PROMPT_TEMPLATE_TEXT = """
        Begin with a checklist of the steps to generate the script for the given outline. Do not output this checklist.
        Create a detailed, markdown-formatted narrative script for the following outline:

        ## Input
        {content}

        Requirements:
        - Think carefully about the content
        - Validate required keys before composing the script.
        - Use clear, consistent headings
        - Write for clarity and readability
        - Make the output concise yet thorough
        - Ensure all content is recent and up-to-date
        - Ensure the script you generate is consistent with the preceding sections in terms of tone, formatting, and flow
        - Avoid unnecessary repetition
        - Do not include a recap, wrap-up, or summary.
        - Be detailed and ensure accurate, step-by-step instructions are included for hands-on demonstrations.
        - Ensure all code works, is complete, syntactically correct, and functional
        - Add explanatory comments to code
        - The script should be a complete, ready-to-record script.
        - Do not include cues for visuals or gestures

        ## Output Format
        Return ONLY the script content for this section as a JSON object:
        {{
        "script_markdown": "<string>"
        }}

    """

# --- Prompt: QA Analysis ---
QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the input and produce a concise, actionable report with the following sections:

    - Overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

    - Correctness: identify major factual errors. For each issue include why it is incorrect (brief explanation).

    - Completeness and Structure: The script should be a complete script, not a draft or outline. List missing points, structural problems, or logical gaps.

    - Audience Fit: whether content matches the intended audience. Do not mention inclusivity.

    Begin the analysis now on the following content:

    ## Input
    - Title: {title}
    - Audience level: {level}
    {content}
"""