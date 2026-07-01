from app.brain import GeminiBrain
from app.core.engine import ARAEngine
from app.core.skill_registry import SkillRegistry

from app.skills.system import system_info


class ARA:

    def __init__(self):

        self.engine = ARAEngine()

        self.brain = GeminiBrain()

        self.skills = SkillRegistry()

        self.register_skills()

    def register_skills(self):

        self.skills.register(
            "system_info",
            system_info
        )

    def start(self):

        self.engine.start()

    def process(self, prompt: str):

        prompt = prompt.strip()

        # temporary

        if prompt.lower() == "system":

            return self.skills.execute(
                "system_info"
            )

        return {
            "message": self.brain.ask(prompt)
        }