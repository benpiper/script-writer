# --- Prompt: Generate Video Idea ---
# --- Prompt: Generate Video Titles ---
IDEA_GENERATION_PROMPT_TEMPLATE_TEXT = """
        Develop a comprehensive video idea based on the input.
        
        Inputs:
        - Topic: {topic}
        - Domain: {domain}
        - Audience level: {level}

        Output Guidelines:
        1. **Titles**: Generate 5 distinct, SEO-optimized titles. Mix styles (How-to, Listicle, Contrarian, Problem/Solution).
        2. **Hook**: Write a single, compelling hook sentence to grab attention immediately.
        3. **Tools**: List 3-7 specific tools, libraries, or technologies that will be used or discussed.
        4. **Objectives**: List 3-5 clear learning objectives or takeaways for the viewer.
        
        Return ONLY a JSON object with the following structure:
        {{
            "titles": ["Title 1", "Title 2", ...],
            "hook": "Your hook sentence",
            "tools": ["Tool 1", "Tool 2", ...],
            "objectives": ["Objective 1", "Objective 2", ...]
        }}
        """


IDEA_GENERATION_WITH_SEARCH_PROMPT_TEMPLATE_TEXT = """
        Develop a comprehensive video idea based on the input and search context.
        
        Inputs:
        - Topic: {topic}
        - Domain: {domain}
        - Audience level: {level}
        
        Search Context:
        {search_context}

        Output Guidelines:
        1. **Titles**: Generate 5 distinct, SEO-optimized titles. Mix styles (How-to, Listicle, Contrarian, Problem/Solution).
        2. **Hook**: Write a single, compelling hook sentence to grab attention immediately.
        3. **Tools**: List 3-7 specific tools, libraries, or technologies that will be used or discussed. Use the search context to ensure these are accurate and up-to-date.
        4. **Objectives**: List 3-5 clear learning objectives or takeaways for the viewer.
        
        Return ONLY a JSON object with the following structure:
        {{
            "titles": ["Title 1", "Title 2", ...],
            "hook": "Your hook sentence",
            "tools": ["Tool 1", "Tool 2", ...],
            "objectives": ["Objective 1", "Objective 2", ...]
        }}
        """


# --- Prompt: Ideation QA Prompt Template ---


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
            "tools": {tools},
            "objectives": {objectives},
            "delivery_type": "{delivery_type}",
        }}

        Guidelines:
        - Stay strictly within the scope defined by the input.
        - Arrange all sections in a clear, logical sequence.
        - Describe actions in plain English. Do not include literal shell commands (e.g., use "Install package" instead of "npm install package").
        - Do not include code snippets.
        - Use only ASCII characters. Do not use Unicode characters.
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
            "delivery_type": "{delivery_type}"
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

    - Consistency: The outline should be internally consistent and free of contradictions.
    - Completeness: The outline should clearly detail prerequisites, steps, and expected outcomes.
    - Audience Fit: The outline should be appropriate for the intended audience level.
    - Decision: PASS or FAIL

    ## Output Format

        Return ONLY a JSON object structured as follows:

    {{
      "decision": "<pass or fail>",
      "reason": "<reason for the decision (string)",
      "consistency": <list of inconsistent or contradictory points>,
      "completeness": <list of incomplete points>,
    }}
    
    **JSON Formatting Rules**:
    - Return ONLY valid JSON. No text before or after.
    - **CRITICAL**: JSON requires DOUBLE QUOTES (") for all keys and string values. Do NOT use single quotes (').
    - Do NOT use backticks (`) for code references. Use plain text description instead.
    - Do NOT include code examples. Describe code in prose without syntax.
    - If you must reference code, use descriptive text, not literal syntax.
    
    Begin the analysis now on the following content:

    ## Input
    - Title: {title}
    - Tools: {tools}
    - Hook: {hook}
    - Domain: {domain}
    - Objectives: {objectives}
    - Audience level: {level}
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
        - Do NOT include code examples. Describe code in prose without syntax.
        - If you must reference code, use descriptive text, not literal syntax.
        - Do not include code or any commands.
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
        Delivery Type: {delivery_type}
        
        Guidelines based on Delivery Type:
        - If 'Delivery Type' contains "lecture" or "no code", focus on concepts, theory, and high-level strategy. DOES NOT include code blocks or technical implementation details.
        - If 'Delivery Type' contains "lab" or "demo", include practical steps, specific commands, and code examples.
        
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
       - Ensure terms are defined and explained
    
    2. Audience Fit
       - Ensure content matches the intended audience level.
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

Search is NOT NEEDED if the topic only involves:
- General concepts (e.g., "what is a variable")
- Fundamental programming principles
- Timeless educational content

Search is NEEDED for anything else.

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
    "tools": {tools},
    "objectives": {objectives},
    "delivery_type": "{delivery_type}",
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
- Describe actions in plain English. Do not include literal shell commands.
- Do not include code snippets.
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
    "delivery_type": "{delivery_type}",
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
