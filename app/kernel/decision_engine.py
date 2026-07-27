from app.intent.models import Intent


class Decision:

    def __init__(
        self,
        approved: bool,
        reason: str,
        risk: str,
    ):
        self.approved = approved
        self.reason = reason
        self.risk = risk


class DecisionEngine:

    # ==================================================
    # ALLOWED SKILLS
    # ==================================================

    SAFE_SKILLS = {
        "system",
        "memory",
        "browser",
        "windows",
        "calculator",
        "vision",
        "visual_action",
    }

    # ==================================================
    # HIGH-RISK ACTIONS
    # ==================================================

    HIGH_RISK_ACTIONS = {
        "delete",
        "format",
        "shutdown",
        "restart",
    }

    # ==================================================
    # EVALUATE
    # ==================================================

    def evaluate(self, intent: Intent):

        # --------------------------------------------------
        # UNKNOWN SKILL
        # --------------------------------------------------

        if intent.skill not in self.SAFE_SKILLS:

            return Decision(
                False,
                "Unknown skill.",
                "HIGH",
            )

                # --------------------------------------------------
        # DANGEROUS ACTION
        # --------------------------------------------------

        action = (
            intent.action or ""
        ).lower()

        if action in self.HIGH_RISK_ACTIONS:

            parameters = (
                intent.parameters or {}
            )

            confirmed = bool(
                parameters.get(
                    "confirmed",
                    False,
                )
            )

            if not confirmed:

                return Decision(
                    False,
                    "Confirmation required.",
                    "HIGH",
                )

        # --------------------------------------------------
        # LOW CONFIDENCE
        # --------------------------------------------------

        if intent.confidence < 0.70:

            return Decision(
                False,
                "Confidence too low.",
                "MEDIUM",
            )

        # --------------------------------------------------
        # APPROVED
        # --------------------------------------------------

        return Decision(
            True,
            "Approved",
            "LOW",
        )