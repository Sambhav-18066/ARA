from app.intent.models import Intent


class Decision:

    def __init__(
        self,
        approved: bool,
        reason: str,
        risk: str
    ):
        self.approved = approved
        self.reason = reason
        self.risk = risk


class DecisionEngine:

    SAFE_SKILLS = {
        "system",
        "memory",
        "browser",
        "windows"
    }

    HIGH_RISK_ACTIONS = {
        "delete",
        "format",
        "shutdown",
        "restart"
    }

    def evaluate(self, intent: Intent):

        # Unknown skill
        if intent.skill not in self.SAFE_SKILLS:

            return Decision(
                False,
                "Unknown skill.",
                "HIGH"
            )

        # Dangerous action
        if intent.action.lower() in self.HIGH_RISK_ACTIONS:

            return Decision(
                False,
                "Confirmation required.",
                "HIGH"
            )

        # Low confidence
        if intent.confidence < 0.70:

            return Decision(
                False,
                "Confidence too low.",
                "MEDIUM"
            )

        return Decision(
            True,
            "Approved",
            "LOW"
        )