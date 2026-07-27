import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class VisionAnalyzer:

    def __init__(self):

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY was not found."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = "gemini-2.5-flash"

    def analyze(self, image_path, prompt=None):

        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "success": False,
                "message": (
                    f"Screenshot not found: "
                    f"{image_path}"
                ),
            }

        if prompt is None:
            prompt = (
                "Describe what is currently visible "
                "on this computer screen. "
                "Identify the main application or window, "
                "important visible UI elements, text, "
                "buttons, menus, dialogs, and anything "
                "that may be useful to a desktop assistant. "
                "Be concise and factual. "
                "Do not guess about elements that are not "
                "clearly visible."
            )

        try:

            image_bytes = image_path.read_bytes()

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/png",
                    ),
                ],
            )

            description = (
                response.text.strip()
                if response.text
                else ""
            )

            if not description:
                return {
                    "success": False,
                    "message": (
                        "Vision model returned "
                        "no description."
                    ),
                }

            return {
                "success": True,
                "message": description,
                "data": {
                    "description": description,
                    "image_path": str(
                        image_path.resolve()
                    ),
                    "model": self.model,
                },
            }

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Screen analysis is temporarily "
                    f"unavailable: {error}"
                ),
                "reason": "vision_ai_unavailable",
            }