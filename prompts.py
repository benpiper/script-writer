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
                "hook": "<string: punchy, provocative hook under 50 words that grabs attention>",
                "tags": <list of tags>,
                "tools": <list of tools (if applicable)>,
                "objectives": <list of objectives or outcomes>,
            }}

        Output Constraints:
        - Return only one JSON object per response.
        - Use only ASCII characters
        - Do not use markdown
        - SEO-optimize all titles
        - Return ONLY valid JSON.
        - Do not include any text before or after the JSON.
        - Ensure all keys and string values are enclosed in double quotes.

        After generating the output, review it to ensure all requirements and formatting constraints are fulfilled.
        If validation fails, self-correct and return a valid JSON object.

        """

# --- Prompt: Ideation QA Prompt Template ---
IDEATION_QA_PROMPT_TEMPLATE_TEXT = """
        The following input is a high-level idea for content.
        Guidelines:
        - Correct all factual, logical, spelling, grammar, and capitalization errors.
        - The title provided is the user-selected title. DO NOT CHANGE THE TITLE.
        - The topic, domain, level, hook, tags, tools, and objectives should align with the title. If any do not align, change other fields to make them match the title.
        - If the topic is nonsensical, unclear, invalid, contradictory, or refers to things that don't exist, throw an error.
        
        ## Input
        {{
                "title": "{title}",
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
        Create an outline using the structured input provided.

        Input JSON structure:
        {{
            "title": "{title}",
            "domain": "{domain}",
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
        - The outline must be comprehensive and complete.
        - The outline must be detailed but concise enough to fit within output limits.
        - Do not include code blocks
        - Use only ASCII characters
        - For the final section, refrain from including next steps, recommendations, or external/additional resources.
        - Return ONLY valid JSON.
        - Do not include any text before or after the JSON.
        - Ensure all keys and string values are enclosed in double quotes.
        - **CRITICAL**: The 'sections' array must be a FLAT list of objects. DO NOT nest sections inside other sections.
        - **CRITICAL**: Do NOT use string concatenation operators (+) or any other programming syntax inside JSON. Each string must be complete.
        - If content is long, keep it as one complete string or split into multiple array elements. Never use + to join strings.

        If 'title' or 'tools' fields are missing or not the correct type, respond with the following JSON object:
        
        {{"error": "Missing or invalid input fields."}}
        

        After outlining, validate that each section directly supports the provided inputs, and confirm that all sections and steps are in logical order.
        If any guideline is not fully met, correct the outline before producing your final output.

        # Output Format
        - Return a JSON object structured as:
        
        {{
            "meta":[
            {{
            "title": "{title}",
            "level": "{level}",
        }}
            ],
            "sections": [
            {{ "name": "<string>", "content": [<string>, ...] }},
            {{ "name": "<string>", "content": [<string>, ...] }}
            ]
        }}
        
        - 'sections' should be a single FLAT array of section objects.
        - **CRITICAL**: Each section object MUST have EXACTLY TWO keys: 'name' and 'content'. NO OTHER KEYS are allowed.
        - 'name': the title of the section (string)
        - 'content': an array of strings detailing the main points, demonstration steps, or explanations.
        - **DO NOT add keys like 'demonstration', 'subsections', 'sections', 'steps', or any other keys besides 'name' and 'content'.**
        - If you need to include demonstration steps, add them as strings in the 'content' array.
        
        Example of a VALID section:
        {{ "name": "Setting Up Environment", "content": ["Install Python 3.9+", "Run: pip install transformers", "Verify installation: python -c 'import transformers'"] }}
        
        Example of INVALID sections (DO NOT DO THIS):
        {{ "name": "Setup", "content": ["Install Python"], "demonstration": "python --version" }}  // WRONG - extra 'demonstration' key
        {{ "name": "Setup", "content": ["Install Python"], "steps": ["Step 1", "Step 2"] }}  // WRONG - extra 'steps' key

        """


# --- Prompt: QA Outline ---

OUTLINE_QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the input based on the following criteria:

    - Overall quality judgment (accurate/inaccurate, consistent/inconsistent, clear/unclear).

    - Completeness and Structure: The outline should be complete and thorough. There should be no missing points, structural problems, or logical gaps.

    - Consistency: The outline should be internally consistent and free of contradictions.

    - Decision: PASS or FAIL

    ## Output Format

        Return ONLY a JSON object structured as follows:

    {{
      "decision": "<pass or fail>",
      "reason": "<reason for the decision (string)",
      "quality": "<overall quality judgment> (string)",
      "completeness": <list of gaps or missing points>,
      "consistency": <list of inconsistent or contradictory points>,
    }}
    
    **JSON Formatting Rules**:
    - Return ONLY valid JSON. No text before or after.
    - **CRITICAL**: JSON requires DOUBLE QUOTES (") for all keys and string values. Do NOT use single quotes (').
    - Do NOT use backticks (`) for code references. Use plain text description instead.
    - Do NOT include code examples with quotes in strings. Describe code in prose without syntax.
    - If you must reference code, use descriptive text, not literal syntax.
    
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
        
        ## Critical JSON Rules
        - Return ONLY valid JSON. No text before or after.
        - Each section object MUST have EXACTLY TWO keys: 'name' and 'content'. NO OTHER KEYS.
        - **CRITICAL**: Do NOT use string concatenation operators (+) or any programming syntax inside JSON.
        - Each string in the content array must be complete. If content is long, split into multiple array elements.
        - Do NOT write: "text1" + "text2" (WRONG)
        - DO write: "text1", "text2" or "text1 text2" (CORRECT)
        - Do NOT use backticks (`) for code references. Use plain text description instead.
        - Do NOT include code examples with quotes in strings. Describe code in prose without syntax.
        - If you must reference code, use descriptive text, not literal syntax.
        - Do not include entire terminal commands.
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
        - Style: Direct, clear, conversational, explanatory, authoritative
        - Use smooth transitional phrases between sections to maintain flow
        - Capitalize words that should be emphasized in speech
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

# --- Prompt: Generate script section ---
SCRIPT_SECTION_PROMPT_TEMPLATE_TEXT = """
        You are writing a video script section by section.
        
        ## Context
        Title: {title}
        Audience Level: {level}
        
        ## Full Outline
        {outline}
        
        ## Context Summary (What has happened so far)
        {context_summary}
        
        ## Recent Script Content (Last few paragraphs)
        {recent_script_content}
        
        ## Current Section to Write
        Name: {section_name}
        Content Points:
        {section_content}
        
        ## Instructions
        - Write the script for the "Current Section" ONLY.
        - Ensure smooth transition from the "Recent Script Content", keeping the "Context Summary" in mind.
        - Maintain the same tone and style (Direct, clear, conversational, authoritative).
        - Capitalize words that should be emphasized in speech. Do not embolden or italicize words.
        - Avoid unnecessary repetition
        - Add explanatory comments to any code
        - Provide filenames for code files
        - The script must be a spoken narrative. Use complete sentences.
        - Do not use bullets or numbered points
        - Do not use tables
        - Do not use emojis
        - Expand all acronyms in parentheses
        - Define all technical terms
        - Do not include cues for gestures or visuals
        - Cover all points in "Content Points".
        - Use markdown formatting.
        - Use clear, consistent headings
        - Do not repeat the title or intro if already covered (unless this IS the intro).
        - Do not output the "Recent Script Content" or "Context Summary" again.
        - Output ONLY the new script content for this section.
"""

# --- Prompt: Summarize Script Section ---
SUMMARIZE_SECTION_PROMPT_TEMPLATE_TEXT = """
    Summarize the following script section.
    
    ## Input Script Section
    {section_script}
    
    ## Instructions
    - Create a concise summary of the key points covered in this section.
    - Focus on information that is relevant for maintaining continuity in subsequent sections (e.g., concepts introduced, terms defined, current state of a demo).
    - Do not include minor details or filler.
    - The summary should be a single paragraph.
"""

# --- Prompt: QA Analysis ---
SCRIPT_QA_PROMPT_TEMPLATE_TEXT = """
    Analyze the following script section and produce a concise, actionable QA report.

    ## Input Content to Analyze
    Title: {title}
    Audience Level: {level}
    
    <script_content>
    {content}
    </script_content>

    ## Analysis Criteria
    
    1. Completeness and Structure
       - Ensure no bullets or tables are used.
       - Ensure no incomplete sentences.
    
    2. Audience Fit
       - Verify content matches the intended audience level.
       - Do not mention inclusivity.

    ## Output Format
    Return ONE JSON object. Do not include any text before or after the JSON.
    
    {{
      "completeness": "<string: analysis of completeness and structure>",
      "audience_fit": "<string: analysis of audience fit>"
    }}

    ## Final Instructions
    - Output ONLY valid JSON.
    - Ensure all keys and string values are enclosed in double quotes.
    - Do not use markdown formatting.
    - Analyze the <script_content> provided above and generate the JSON report now.
"""

# --- Prompt: Search Decision (for LangGraph) ---
SEARCH_DECISION_PROMPT_TEXT = """
You are analyzing whether web search is needed to create an accurate, up-to-date video outline.

## Topic Information
{video_idea_json}

## Decision Criteria
Search is NEEDED if the topic involves:
- Specific software versions, release dates, or features
- Current best practices that may have changed
- Recent tools, libraries, or technologies
- Time-sensitive information
- Technical specifications or API details

Search is NOT NEEDED if the topic involves:
- General concepts (e.g., "what is a variable")
- Fundamental programming principles
- Timeless educational content
- Topics you have sufficient knowledge about

## Output Format
Return ONLY a JSON object:

{{
  "needs_search": true/false,
  "reasoning": "brief explanation of your decision",
  "search_queries": ["query 1", "query 2"] // if needs_search is true, provide 1-3 specific search queries
}}

**Critical**: Return ONLY valid JSON. No text before or after.
"""

# --- Prompt: Outline with Search Context (for LangGraph) ---
OUTLINE_WITH_SEARCH_PROMPT_TEXT = """
Begin with a checklist of the main planning and sequencing steps you will follow before creating the outline. Do not output this checklist.
Create an outline using the structured input provided.

Input JSON structure:
{{
    "title": "{title}",
    "domain": "{domain}",
    "level": "{level}",
    "hook": "{hook}",
    "tags": {tags},
    "tools": {tools},
    "objectives": {objectives},
}}

## Search Context (if available)
{search_context}

Guidelines:
- If search context is provided above, incorporate the factual information into your outline
- Ensure version numbers, dates, and technical details match the search results
- Stay strictly within the scope defined by the input.
- Exclude self-paced exercises; all demonstrations should be incorporated within the outline.
- Carefully design the outline to ensure it fully addresses the content indicated in the input.
- Arrange all sections and demonstration steps in a clear, logical sequence.
- The outline must be comprehensive and complete.
- The outline must be detailed but concise enough to fit within output limits.
- Do not include code blocks
- Use only ASCII characters
- For the final section, refrain from including next steps, recommendations, or external/additional resources.
- Return ONLY valid JSON.
- Do not include any text before or after the JSON.
- Ensure all keys and string values are enclosed in double quotes.
- **CRITICAL**: The 'sections' array must be a FLAT list of objects. DO NOT nest sections inside other sections.
- **CRITICAL**: Do NOT use string concatenation operators (+) or any other programming syntax inside JSON. Each string must be complete.
- If content is long, keep it as one complete string or split into multiple array elements. Never use + to join strings.

If 'title' or 'tools' fields are missing or not the correct type, respond with the following JSON object:

{{"error": "Missing or invalid input fields."}}


After outlining, validate that each section directly supports the provided inputs, and confirm that all sections and steps are in logical order.
If any guideline is not fully met, correct the outline before producing your final output.

# Output Format
- Return a JSON object structured as:

{{
    "meta":[
    {{
    "title": "{title}",
    "level": "{level}",
}}
    ],
    "sections": [
    {{ "name": "<string>", "content": [<string>, ...] }},
    {{ "name": "<string>", "content": [<string>, ...] }}
    ]
}}

- 'sections' should be a single FLAT array of section objects.
- **CRITICAL**: Each section object MUST have EXACTLY TWO keys: 'name' and 'content'. NO OTHER KEYS are allowed.
- 'name': the title of the section (string)
- 'content': an array of strings detailing the main points, demonstration steps, or explanations.
- **DO NOT add keys like 'demonstration', 'subsections', 'sections', 'steps', or any other keys besides 'name' and 'content'.**
- If you need to include demonstration steps, add them as strings in the 'content' array.

Example of a VALID section:
{{ "name": "Setting Up Environment", "content": ["Install Python 3.9+", "Run: pip install transformers", "Verify installation: python -c 'import transformers'"] }}

Example of INVALID sections (DO NOT DO THIS):
{{ "name": "Setup", "content": ["Install Python"], "demonstration": "python --version" }}  // WRONG - extra 'demonstration' key
{{ "name": "Setup", "content": ["Install Python"], "steps": ["Step 1", "Step 2"] }}  // WRONG - extra 'steps' key
"""
