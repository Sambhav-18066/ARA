from abc import ABC, abstractmethod


class Brain(ABC):

    @abstractmethod
    def ask(self, prompt: str):

        pass