from dataclasses import dataclass, field


@dataclass
class Intent:

    intent: str

    skill: str

    action: str

    parameters: dict = field(default_factory=dict)

    confidence: float = 0.0