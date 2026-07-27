class ResponseRenderer:

    @staticmethod
    def render(result):

        if result is None:
            return "No response."

        if not isinstance(result, dict):
            return str(result)

        # ------------------------------------------
        # FAILURE
        # ------------------------------------------

        if not result.get("success", False):

            return result.get(
                "message",
                result.get(
                    "reason",
                    "Command failed.",
                ),
            )

        message = result.get("message")
        data = result.get("data")

        # ------------------------------------------
        # NO STRUCTURED DATA
        # ------------------------------------------

        if not data:
            return message or "Done."

        lines = []

        if message:
            lines.append(message)

        # ------------------------------------------
        # WINDOW LIST
        # ------------------------------------------

        windows = data.get("windows")

        if isinstance(windows, list):

            if windows:

                lines.append("")

                for index, window in enumerate(
                    windows,
                    start=1,
                ):
                    lines.append(
                        f"  {index}. {window}"
                    )

            else:
                lines.append("No windows found.")

            return "\n".join(lines)

        # ------------------------------------------
        # GENERIC DATA
        # ------------------------------------------

        lines.append("")

        for key, value in data.items():

            label = (
                key.replace("_", " ")
                .strip()
                .title()
            )

            lines.append(
                f"  {label}: {value}"
            )

        return "\n".join(lines)