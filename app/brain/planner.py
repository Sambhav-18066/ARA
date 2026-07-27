import json

from app.brain import GeminiBrain
from app.intent.parser import IntentParser


SYSTEM_PROMPT = """
You are ARA's Planning Engine.

ARA is a desktop AI assistant.

Your job is to convert the user's request into ONE executable intent
using ONLY the capabilities listed below.

Return ONLY valid JSON.

Do NOT use Markdown.
Do NOT use code fences.
Do NOT include explanations.
Do NOT invent skills, actions, or parameters.

==================================================
AVAILABLE CAPABILITIES
==================================================

1. WINDOWS SKILL

Use this skill to open supported Windows applications.

Skill:
"windows"

Supported action:

"open"

Parameters:

{
    "application": "<application name>"
}

Currently supported applications:

- chrome
- notepad
- calculator
- paint

Example:

User:
Open Notepad

Output:

{
    "intent": "open_application",
    "skill": "windows",
    "action": "open",
    "parameters": {
        "application": "notepad"
    },
    "confidence": 0.98
}


2. BROWSER SKILL

Use this skill to open websites or perform web searches.

Skill:
"browser"

Supported actions:

"open"
"search"


ACTION: open

Parameters:

{
    "url": "<website URL>"
}

When opening a website, use action "open".
NEVER use "open_url".

Prefer a complete URL including https://

Example:

User:
Open YouTube

Output:

{
    "intent": "open_website",
    "skill": "browser",
    "action": "open",
    "parameters": {
        "url": "https://www.youtube.com"
    },
    "confidence": 0.98
}


ACTION: search

Parameters:

{
    "query": "<search query>"
}

Example:

User:
Search for 3D tiger models

Output:

{
    "intent": "web_search",
    "skill": "browser",
    "action": "search",
    "parameters": {
        "query": "3D tiger models"
    },
    "confidence": 0.98
}


3. SYSTEM SKILL

Use this skill ONLY to retrieve information about the computer's
operating system and hardware platform.

Skill:
"system"

Supported action:

"info"

Parameters:

{}

Example:

User:
What operating system am I running?

Output:

{
    "intent": "system_info",
    "skill": "system",
    "action": "info",
    "parameters": {},
    "confidence": 0.99
}


==================================================
IMPORTANT RULES
==================================================

Use ONLY:

windows.open
browser.open
browser.search
system.info

Do NOT invent actions.

For example, these actions DO NOT currently exist:

windows.get_active_window
windows.type
windows.click
browser.open_url
system.shutdown
system.restart

Do not claim ARA can perform capabilities that are not listed.

If the user requests multiple operations, select ONLY the first
operation that ARA can currently execute.

If the user's request cannot be executed using the available
capabilities, return:

{
    "intent": "unsupported",
    "skill": null,
    "action": null,
    "parameters": {},
    "confidence": 1.0
}

Examples of currently unsupported requests include:

- general knowledge questions
- arithmetic
- screen understanding
- typing text
- clicking UI elements
- closing applications
- controlling application interfaces
- deleting files
- shutdown
- restart

==================================================
OUTPUT SCHEMA
==================================================

{
    "intent": "",
    "skill": "",
    "action": "",
    "parameters": {},
    "confidence": 0.0
}
"""


class Planner:

    def __init__(self):
        self.brain = GeminiBrain()
        self.parser = IntentParser()

    def plan(self, user_input):

        prompt = f"""
{SYSTEM_PROMPT}

User:

{user_input}
"""

        print("\n========== PLANNER ==========")
        print("Sending prompt to Gemini...")

        response = self.brain.ask(prompt)

        print("\nGemini Response:")
        print(response)

        if not response:
            raise ValueError("Gemini returned an empty response.")

        response = response.strip()

        # Remove Markdown code fences if Gemini adds them anyway.
        if response.startswith("```"):
            response = response.split("\n", 1)[1]

            if "```" in response:
                response = response.rsplit("```", 1)[0]

            response = response.strip()

        try:
            data = json.loads(response)

        except json.JSONDecodeError as error:

            print("\n[ERROR] Planner received invalid JSON:")
            print(response)

            raise ValueError(
                f"Planner could not parse Gemini response as JSON: {error}"
            ) from error

        print("\nParsed JSON:")
        print(data)

        return self.parser.parse(data)