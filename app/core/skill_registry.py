from typing import Callable


class SkillRegistry:
    def __init__(self):
        self.skills = {}

    def register(self, name: str, handler: Callable):
        self.skills[name] = handler
        print(f"[Skill] Registered: {name}")

    def execute(self, name: str, *args, **kwargs):
        if name not in self.skills:
            raise Exception(f"Skill '{name}' not found")

        return self.skills[name](*args, **kwargs)

    def list_skills(self):
        return list(self.skills.keys())


registry = SkillRegistry()