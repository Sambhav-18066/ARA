from pathlib import Path
from datetime import datetime

import pyautogui


class ScreenCapture:

    def __init__(self, output_dir="data/screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def capture(self, filename=None):
        """
        Capture the entire screen and save it locally.
        """

        try:
            if filename is None:
                timestamp = datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )

                filename = f"ara_screen_{timestamp}.png"

            if not filename.lower().endswith(".png"):
                filename += ".png"

            path = self.output_dir / filename

            screenshot = pyautogui.screenshot()

            screenshot.save(path)

            return {
                "success": True,
                "message": "Screen captured successfully.",
                "path": str(path.resolve()),
                "width": screenshot.width,
                "height": screenshot.height,
            }

        except Exception as error:
            return {
                "success": False,
                "message": f"Screen capture failed: {error}",
            }