
# --- Prompt: Generate Video Idea ---
IDEATION_PROMPT_TEMPLATE_TEXT = """
        Generate an idea for a video that can be quickly recorded and published, guided by the following requirements:
        Inputs:
        - Topic: {topic} (string)
        - Domain: {domain} (string)
        - Audience level: {level} (string)

        - Output Format
        Return your answer as valid JSON using the following format:

            {{
                "title": "<string: SEO-optimized title of the video>",
                "domain": "{domain}",
                "hook": "<string: 3-line hook>",
                "tags": [<list of tags>],
                "tools": [<list of tools>],
                "objectives": [<list of objectives or outcomes>],
            }}

        Output Constraints:
        - Return only a single JSON object per response.
        - Do not use emojis
        - Verify that everything makes sense. If any of the input is inconsistent, correct it in the output.

        After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
        If validation fails, self-correct and return a valid JSON object.

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
            "hook": "{hook}",
            "domain": "{domain}",
            "objectives": "{objectives}",

        }}
        ```

        Guidelines:
        - Stay strictly within the scope defined by the input.
        - Exclude self-paced exercises; all demonstrations should be incorporated within the video outline.
        - Carefully design the outline to ensure it fully addresses the content indicated in the input.
        - Arrange all sections and demonstration steps in a clear, logical sequence.
        - The outline must be detailed, comprehensive, elaborate, and complete.
        - Do not use emojis
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

# --- Prompt: QA Outline ---

OUTLINE_QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the input based on the following criteria:

    - Overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

    - Correctness: Identify major factual or logical errors.

    - Completeness and Structure: The outline should be complete and thorough. There should be no missing points, structural problems, or logical gaps.

    - Decision: PASS or FAIL

    ## Output Format

        Return ONLY a JSON object structured as follows:

    {{
      "decision": "<pass or fail>",
      "reason": "<reason for the decision (string)"
    }}
    
    Begin the analysis now on the following content:

    ## Input
    - Title: {title}
    - Tools: {tools}
    - Hook: {hook}
    - Domain: {domain}
    - Objectives: {objectives}
    - Outline JSON:
      {outline}
"""

# --- Prompt: Generate script ---
SCRIPT_PROMPT_TEMPLATE_TEXT = """     
        Begin with a checklist of the steps to generate the script for the given outline. Do not output this checklist.

        Create a detailed, markdown-formatted narrative script for the following outline:

        ## Input
        {content}

        Requirements:
        - Think carefully about the content
        - Start by introducing a concept or term related to the topic.
        - Validate required keys before composing the script.
        - Use clear, consistent headings
        - Write in the style of Ben Piper: Direct, blunt, conversational, explanatory, clear, slightly humorous.
        - Be thorough, comprehensive, detailed, and complete
        - Ensure all content is recent and up-to-date
        - Ensure the script you generate is consistent with the preceding sections in terms of tone, formatting, and flow
        - Explain different types, methods, or aspects of the topic, providing examples where necessary.
        - Avoid unnecessary repetition
        - Do not include a recap, wrap-up, or summary.
        - Be detailed and ensure accurate, step-by-step instructions are included for hands-on demonstrations.
        - Ensure all code works, is complete, syntactically correct, and functional
        - Add explanatory comments to code
        - The script should be a complete, ready-to-record script. Not an outline.
        - Do not include cues for visuals or gestures

        ## Output Format
        Return ONLY the script content for this section as a JSON object:
        {{
        "script_markdown": "<string>"
        }}

    """

# --- Prompt: QA Analysis ---
SCRIPT_QA_PROMPT_TEMPLATE_TEXT = """
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