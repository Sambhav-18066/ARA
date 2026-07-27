from datetime import datetime


class ActionLogger:

    def log(self, action, result):

        print(
            f"[{datetime.now()}] "
            f"{action} -> {result}"
        )