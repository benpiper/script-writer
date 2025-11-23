
# --- Prompt: Generate Video Idea ---
IDEATION_PROMPT_TEMPLATE_TEXT = """
        Thoughtfully develop the following content idea:
        Inputs:
        - Topic: {topic} (string)
        - Domain: {domain} (string)
        - Audience level: {level} (string)

        Guidelines
        - Topic, domain, and audience level must align
        - Do not allow fictional tools or concepts
        If any of the input is incorrect, return this JSON error object:

          {{
            "error": "<reason>"
          }}

        
        - Output Format
        Return one JSON object using the following format:

            {{
                "title": "<string: SEO-optimized title>",
                "title_contrarian": "<string: contrarian title>",
                "title_descriptive": "<string: descriptive title>",
                "title_problem_solution": "<string: problem-solution>",
                "title_how_to": "<string: how-to>",
                "title_curiosity": "<string: curiosity>",
                "topic": "{topic}",
                "domain": "{domain}",
                "level": "{level}",
                "hook": "<string: 2-sentence hook>",
                "tags": <list of tags>,
                "tools": <list of tools (if applicable)>,
                "objectives": <list of objectives or outcomes>,
            }}

        Output Constraints:
        - Return only one JSON object per response.
        - Do not use markdown
        - Do not use emojis
        - SEO-optimize all titles

        After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
        If validation fails, self-correct and return a valid JSON object.

        """

# --- Prompt: Ideation QA Prompt Template ---
IDEATION_QA_PROMPT_TEMPLATE_TEXT = """
        The following input is a high-level idea for content.
        Guidelines:
        - Correct all factual, logical, spelling, grammar, and capitalization errors.
        - The title, topic, domain, level, hook, tags, tools, and objectives should align. If any do not align, change other fields to make them match the title and topic.
        - If the title and topic do not align, change the title to align with the topic.
        - If the topic is nonsensical, unclear, invalid, contradictory, or refers to things that don't exist, throw an error.
        
        ## Input
        {{
                "title": "{title}",
                "title_contrarian": "{title_contrarian}",
                "topic": {topic},
                "domain": "{domain}",
                "level": "{level}",
                "hook": "{hook}",
                "tags": {tags},
                "tools": {tools},
                "objectives": {objectives},
        }}

        ## Output format
        Output one JSON object with corrections using the same keys.
        Append an additional key "qa_status" with brief remarks.
        Do not use markdown.
"""

# --- Prompt: Generate Outline ---
OUTLINE_PROMPT_TEMPLATE = """
        Begin with a checklist of the main planning and sequencing steps you will follow before creating the outline. Do not output this checklist.
        Create a comprehensive, detailed outline using the structured input provided.

        Input JSON structure:
        {{
            "title": "{title}",
            "domain": "{domain}",
            "tools": {tools},
            "level": "{level}",
            "hook": "{hook}",
            "tags": {tags},
            "tools": {tools},
            "objectives": {objectives},

        }}

        Guidelines:
        - Stay strictly within the scope defined by the input.
        - Exclude self-paced exercises; all demonstrations should be incorporated within the outline.
        - Carefully design the outline to ensure it fully addresses the content indicated in the input.
        - Arrange all sections and demonstration steps in a clear, logical sequence.
        - The outline must be detailed, comprehensive, elaborate, and complete.
        - Do not use emojis
        - For the final section, refrain from including next steps, recommendations, or external/additional resources.

        If 'title' or 'tools' fields are missing or not the correct type, respond with the following JSON object:
        
        {{"error": "Missing or invalid input fields."}}
        

        After outlining, validate that each section directly supports the provided inputs, and confirm that all sections and steps are in logical order.
        If any guideline is not fully met, correct the outline before producing your final output.

        # Output Format
        - Return a JSON object structured as:
        
        {{
            "sections": [
            {{ "name": "<string>", "content": [<string>, ...] }}
            ]
        }}
        
        - 'sections' should be an array of section objects.
        - Each section object includes:
        - 'name': the title of the section (string)
        - 'content': an array of strings detailing the main points, demonstration steps, or explanations.

        """

# --- Prompt: QA Outline ---

OUTLINE_QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the input based on the following criteria:

    - Overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

    - Correctness: Identify any factual or logical errors.

    - Completeness and Structure: The outline should be complete and thorough. There should be no missing points, structural problems, or logical gaps.

    - Consistency: The outline should be internally consistent and free of contradictions.

    - Decision: PASS or FAIL

    ## Output Format

        Return ONLY a JSON object structured as follows:

    {{
      "decision": "<pass or fail>",
      "reason": "<reason for the decision (string)",
      "quality": "<overall quality judgment> (string)",
      "correctness": <list of factual or logical errors>,
      "completeness": <list of gaps or missing points>,
      "consistency": <list of inconsistent or contradictory points>,
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

# --- Prompt: Generate outline based on QA feedback ---
OUTLINE_FINAL_PROMPT_TEMPLATE_TEXT = """
        Correct the outline based on the feedback in the QA report.
        
        ## Inputs
        - Outline: {outline}
        - QA Report: {outline_qa_report}

        ## Output Format
        - Return a JSON object structured as:
        
        {{
            "sections": [
            {{ "name": "<string>", "content": [<string>, ...] }}
            ]
        }}
"""

# --- Prompt: Generate script ---
SCRIPT_PROMPT_TEMPLATE_TEXT = """     
        Begin with a checklist of the steps to generate a script for the given outline. Do not output this checklist.

        Create a detailed, markdown-formatted narrative script for the following outline:

        ## Input
        {content}

        Requirements:
        - Think carefully about the content
        - Start by introducing a concept or term related to the topic.
        - Validate required keys before composing the script.
        - Use clear, consistent headings
        - Write in the style of Ben Piper: Direct, clear, conversational, explanatory, authoritative
        - Be thorough, comprehensive, detailed, and complete
        - Ensure all content is recent and up-to-date
        - Ensure the script you generate is consistent with the preceding sections in terms of tone, formatting, and flow
        - Explain different types, methods, or aspects of the topic, providing examples where necessary.
        - Avoid unnecessary repetition
        - Be detailed and ensure accurate, step-by-step instructions are included for hands-on demonstrations.
        - If code is included, it should be complete, syntactically correct, consistent, and functional
        - Add explanatory comments to any code
        - The script should be a complete, ready-to-record script. Not an outline.
        - The script must be a spoken narrative. Use complete sentences.
        - Do not use bullets or numbered points
        - Do not use tables
        - Expand all acronyms in parentheses
        - Define all technical terms
        - Do not include cues for gestures or visuals
    """

# --- Prompt: QA Analysis ---
SCRIPT_QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the input and produce concise, actionable suggestions in a report with the following sections:

    - Correctness: identify major factual errors. For each issue include why it is incorrect (brief explanation).

    - Completeness and Structure: The script should be a complete script, not a draft or outline. List missing points, structural problems, incomplete sentences, or logical gaps to be corrected.

    - Audience Fit: whether content matches the intended audience. Do not mention inclusivity.

    - Score: PASS or FAIL

    ## Output
    Return one JSON object.

    Begin the analysis now on the following content:

    ## Input
    - Title: {title}
    - Audience level: {level}
    - Content:
    {content}
"""

# --- Prompt: Generate final script based on QA feedback ---
SCRIPT_FINAL_PROMPT_TEMPLATE_TEXT = """
        You will be given a markdown script and a QA report with suggestions for improvement.
        Guidelines:
        - Do not use bullets or numbered points
        - Do not use tables
        - Return the corrected script in markdown format.

        ## Output Format
        - Markdown
        
        ## Inputs
        - QA Report: {script_qa_report}
        - Script: {script}

"""