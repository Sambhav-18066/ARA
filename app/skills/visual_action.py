from app.skills.base import Skill

from app.vision.capture import ScreenCapture
from app.vision.ocr import LocalOCR
from app.vision.target_selector import TargetSelector

from app.skills.windows import WindowsSkill


class VisualActionSkill(Skill):

    name = "visual_action"

    def __init__(self):

        self.capture_service = ScreenCapture()
        self.ocr = LocalOCR()
        self.target_selector = TargetSelector()
        self.windows = WindowsSkill()

    # ==================================================
    # EXECUTE
    # ==================================================

    def execute(self, action, parameters):

        if parameters is None:
            parameters = {}

        if action == "click_text":
            return self._click_text(parameters)

        return {
            "success": False,
            "message": (
                f"Unknown visual action: {action}"
            ),
        }

    # ==================================================
    # CLICK TEXT
    # ==================================================

    def _click_text(self, parameters):

        target = (
            parameters
            .get("text", "")
            .strip()
        )

        if not target:

            return {
                "success": False,
                "message": "No visual target provided.",
                "reason": "target_missing",
            }

        # --------------------------------------------------
        # 1. CAPTURE CURRENT SCREEN
        # --------------------------------------------------

        capture_result = (
            self.capture_service.capture()
        )

        if not capture_result.get("success"):

            return capture_result

        image_path = self._get_image_path(
            capture_result
        )

        if not image_path:

            return {
                "success": False,
                "message": (
                    "Screenshot captured but no "
                    "image path was returned."
                ),
                "reason": "image_path_missing",
            }

        # --------------------------------------------------
        # 2. OCR SEARCH
        # --------------------------------------------------

        try:

            ocr_result = self.ocr.find(
                image_path,
                target,
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    f"Visual search failed: {error}"
                ),
                "reason": "ocr_error",
            }

        if not ocr_result.get("success"):

            return {
                "success": False,
                "message": ocr_result.get(
                    "message",
                    f"Could not find '{target}'."
                ),
                "reason": "target_not_found",
            }

        # --------------------------------------------------
        # 3. BUILD CANDIDATES
        # --------------------------------------------------

        matches = ocr_result.get(
            "matches",
            []
        )

        candidates = []

        for index, match in enumerate(
            matches,
            start=1,
        ):

            center = match.get(
                "center",
                {}
            )

            x = match.get("x")
            y = match.get("y")

            width = match.get("width")
            height = match.get("height")

            center_x = center.get("x")
            center_y = center.get("y")

            # Calculate center if OCR didn't.

            if (
                center_x is None
                and x is not None
                and width is not None
            ):

                center_x = (
                    x + width // 2
                )

            if (
                center_y is None
                and y is not None
                and height is not None
            ):

                center_y = (
                    y + height // 2
                )

            candidates.append({
                "index": index,
                "text": match.get("text"),
                "confidence": match.get(
                    "confidence",
                    0,
                ),
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "center_x": center_x,
                "center_y": center_y,
            })

        # --------------------------------------------------
        # 4. SELECT TARGET
        # --------------------------------------------------

        try:

            selection = (
                self.target_selector.select(
                    target,
                    candidates,
                )
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Visual target selection failed: "
                    f"{error}"
                ),
                "reason": "selection_error",
            }

        if not selection.get("selected"):

            return {
                "success": False,
                "message": selection.get(
                    "message",
                    "Visual target was ambiguous."
                ),
                "reason": selection.get(
                    "reason",
                    "target_not_selected",
                ),
                "selection": selection,
            }

        candidate = selection.get(
            "candidate",
            {}
        )

        center_x = candidate.get(
            "center_x"
        )

        center_y = candidate.get(
            "center_y"
        )

        if (
            center_x is None
            or center_y is None
        ):

            return {
                "success": False,
                "message": (
                    "Target selected but no valid "
                    "click coordinates were available."
                ),
                "reason": "coordinates_missing",
            }

        # --------------------------------------------------
        # 5. CLICK
        # --------------------------------------------------

        click_result = self.windows.execute(
            "click",
            {
                "x": center_x,
                "y": center_y,
            },
        )

        if not click_result.get("success"):

            return click_result

        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        return {
            "success": True,
            "message": (
                f"Clicked '{candidate.get('text')}' "
                f"at ({center_x}, {center_y})."
            ),
            "target": target,
            "clicked_text": candidate.get(
                "text"
            ),
            "confidence": candidate.get(
                "confidence"
            ),
            "score": candidate.get(
                "score"
            ),
            "x": center_x,
            "y": center_y,
        }

    # ==================================================
    # SCREENSHOT PATH HELPER
    # ==================================================

    @staticmethod
    def _get_image_path(capture_result):

        return (
            capture_result.get("path")
            or capture_result.get("image_path")
            or capture_result.get("file")
            or capture_result.get("filename")
        )