from abc import ABC, abstractmethod


class Skill(ABC):
    name = "base"

    @abstractmethod
    def execute(self, action: str, parameters: dict):
        """Execute a skill action"""
        pass