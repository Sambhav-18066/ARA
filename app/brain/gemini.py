import os

from dotenv import load_dotenv
from google import genai

from app.brain.base import Brain

load_dotenv()


class GeminiBrain(Brain):

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:

            raise Exception("Missing GEMINI_API_KEY")

        self.client = genai.Client(
            api_key=api_key
        )

    def ask(self, prompt: str):

        response = self.client.models.generate_content(

            model="gemini-2.5-flash",

            contents=prompt

        )

        return response.text