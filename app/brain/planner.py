import json

from app.brain import GeminiBrain
from app.intent.parser import IntentParser


SYSTEM_PROMPT = """
You are ARA's Planning Engine.

Your only job is to convert the user's request into JSON.

Return ONLY valid JSON.

Available skills:

system
windows
browser
memory

Schema:

{
    "intent":"",
    "skill":"",
    "action":"",
    "parameters":{},
    "confidence":0.0
}

Examples

User:
What operating system am I running?

Output:

{
    "intent":"system_info",
    "skill":"system",
    "action":"info",
    "parameters":{},
    "confidence":0.99
}

User:
Open Chrome

Output:

{
    "intent":"open_application",
    "skill":"windows",
    "action":"open",
    "parameters":{
        "application":"chrome"
    },
    "confidence":0.98
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

        response = self.brain.ask(prompt)

        data = json.loads(response)

        return self.parser.parse(data)