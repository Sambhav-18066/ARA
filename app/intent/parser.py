from app.intent.models import Intent


class IntentParser:

    def parse(self, data: dict) -> Intent:

        return Intent(
            intent=data.get("intent", ""),
            skill=data.get("skill", ""),
            action=data.get("action", ""),
            parameters=data.get("parameters", {}),
            confidence=data.get("confidence", 0.0)
        )