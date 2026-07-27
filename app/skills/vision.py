from app.skills.base import Skill

from app.vision.capture import ScreenCapture
from app.vision.analyzer import VisionAnalyzer
from app.vision.ocr import LocalOCR
from app.vision.target_selector import TargetSelector


class VisionSkill(Skill):

    name = "vision"

    # ==================================================
    # INITIALIZATION
    # ==================================================

    def __init__(self):

        # --------------------------------------------------
        # SCREEN CAPTURE
        # --------------------------------------------------

        self.capture_service = ScreenCapture()

        # --------------------------------------------------
        # LOCAL OCR
        # --------------------------------------------------

        try:

            self.ocr = LocalOCR()

            print("[OK] Local OCR")

        except Exception as error:

            print(
                "[VISION WARNING] "
                f"Local OCR unavailable: {error}"
            )

            self.ocr = None

        # --------------------------------------------------
        # VISUAL TARGET SELECTOR
        # --------------------------------------------------

        try:

            self.target_selector = TargetSelector()

            print("[OK] Visual Target Selector")

        except Exception as error:

            print(
                "[VISION WARNING] "
                f"Target selector unavailable: {error}"
            )

            self.target_selector = None

        # --------------------------------------------------
        # AI VISION
        # --------------------------------------------------
        #
        # AI failure must NOT prevent ARA from booting.
        #
        # Local capabilities:
        #
        #   screenshot
        #   OCR
        #   text location
        #   visual target selection
        #
        # should continue working without Gemini.
        # --------------------------------------------------

        try:

            self.analyzer = VisionAnalyzer()

        except Exception as error:

            print(
                "[VISION WARNING] "
                f"Analyzer unavailable: {error}"
            )

            self.analyzer = None

    # ==================================================
    # EXECUTE
    # ==================================================

    def execute(self, action, parameters):

        if parameters is None:
            parameters = {}

        # --------------------------------------------------
        # SCREENSHOT
        # --------------------------------------------------

        if action == "capture":

            return self._capture(
                parameters
            )

        # --------------------------------------------------
        # LOCAL OCR
        # --------------------------------------------------

        if action == "ocr":

            return self._ocr(
                parameters
            )

        # --------------------------------------------------
        # FIND TEXT
        # --------------------------------------------------

        if action == "find_text":

            return self._find_text(
                parameters
            )

        # --------------------------------------------------
        # SELECT VISUAL TARGET
        # --------------------------------------------------

        if action == "select_text":

            return self._select_text(
                parameters
            )

        # --------------------------------------------------
        # AI SCREEN ANALYSIS
        # --------------------------------------------------

        if action == "analyze":

            return self._analyze(
                parameters
            )

        # --------------------------------------------------
        # UNKNOWN ACTION
        # --------------------------------------------------

        return {
            "success": False,
            "message": (
                f"Unknown vision action: {action}"
            ),
        }

    # ==================================================
    # CAPTURE SCREEN
    # ==================================================

    def _capture(self, parameters):

        filename = parameters.get(
            "filename"
        )

        return self.capture_service.capture(
            filename=filename,
        )

    # ==================================================
    # LOCAL OCR — READ SCREEN
    # ==================================================

    def _ocr(self, parameters):

        # --------------------------------------------------
        # Check OCR availability
        # --------------------------------------------------

        if self.ocr is None:

            return {
                "success": False,
                "message": (
                    "Local OCR is currently unavailable."
                ),
                "reason": "ocr_unavailable",
            }

        # --------------------------------------------------
        # Capture current screen
        # --------------------------------------------------

        capture_result = (
            self.capture_service.capture()
        )

        if not capture_result.get(
            "success"
        ):

            return capture_result

        # --------------------------------------------------
        # Extract screenshot path
        # --------------------------------------------------

        image_path = self._get_image_path(
            capture_result
        )

        if not image_path:

            return {
                "success": False,
                "message": (
                    "Screenshot was captured but "
                    "no image path was returned."
                ),
                "reason": "image_path_missing",
            }

        # --------------------------------------------------
        # Run OCR
        # --------------------------------------------------

        try:

            result = self.ocr.read(
                image_path
            )

            if not result.get(
                "success"
            ):

                return result

            return result

        except Exception as error:

            return {
                "success": False,
                "message": (
                    f"Local OCR failed: {error}"
                ),
                "reason": "ocr_error",
            }

    # ==================================================
    # FIND TEXT ON SCREEN
    # ==================================================

    def _find_text(self, parameters):

        # --------------------------------------------------
        # Check OCR
        # --------------------------------------------------

        if self.ocr is None:

            return {
                "success": False,
                "message": (
                    "Local OCR is currently unavailable."
                ),
                "reason": "ocr_unavailable",
            }

        # --------------------------------------------------
        # Target
        # --------------------------------------------------

        target = (
            parameters
            .get("text", "")
            .strip()
        )

        if not target:

            return {
                "success": False,
                "message": (
                    "No target text was provided."
                ),
                "reason": "target_missing",
            }

        # --------------------------------------------------
        # Capture current screen
        # --------------------------------------------------

        capture_result = (
            self.capture_service.capture()
        )

        if not capture_result.get(
            "success"
        ):

            return capture_result

        # --------------------------------------------------
        # Screenshot path
        # --------------------------------------------------

        image_path = self._get_image_path(
            capture_result
        )

        if not image_path:

            return {
                "success": False,
                "message": (
                    "Screenshot was captured but "
                    "no image path was returned."
                ),
                "reason": "image_path_missing",
            }

        # --------------------------------------------------
        # OCR FIND
        # --------------------------------------------------

        try:

            result = self.ocr.find(
                image_path,
                target,
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    f"Text search failed: {error}"
                ),
                "reason": "ocr_find_error",
            }

        if not result.get(
            "success"
        ):

            return result

        matches = result.get(
            "matches",
            []
        )

        # --------------------------------------------------
        # Convert OCR matches into candidates
        # --------------------------------------------------

        candidates = self._build_candidates(
            matches
        )

        # Sort by OCR confidence for display.

        candidates.sort(
            key=lambda item: item.get(
                "confidence",
                0,
            ),
            reverse=True,
        )

        # Re-number after sorting.

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            candidate["index"] = index

        return {

            "success": True,

            "message": (
                f"Found {len(candidates)} "
                f"candidate(s) for '{target}'."
            ),

            "target": target,

            "count": len(
                candidates
            ),

            "candidates": candidates,

            "image_path": image_path,
        }

    # ==================================================
    # SELECT VISUAL TARGET
    # ==================================================

    def _select_text(self, parameters):

        # --------------------------------------------------
        # Check OCR
        # --------------------------------------------------

        if self.ocr is None:

            return {
                "success": False,
                "selected": False,
                "message": (
                    "Local OCR is currently unavailable."
                ),
                "reason": "ocr_unavailable",
            }

        # --------------------------------------------------
        # Check target selector
        # --------------------------------------------------

        if self.target_selector is None:

            return {
                "success": False,
                "selected": False,
                "message": (
                    "Visual target selector is unavailable."
                ),
                "reason": "target_selector_unavailable",
            }

        # --------------------------------------------------
        # Requested target
        # --------------------------------------------------

        target = (
            parameters
            .get("text", "")
            .strip()
        )

        if not target:

            return {
                "success": False,
                "selected": False,
                "message": (
                    "No visual target was provided."
                ),
                "reason": "target_missing",
            }

        # --------------------------------------------------
        # Capture FRESH screen
        # --------------------------------------------------

        capture_result = (
            self.capture_service.capture()
        )

        if not capture_result.get(
            "success"
        ):

            return capture_result

        # --------------------------------------------------
        # Screenshot path
        # --------------------------------------------------

        image_path = self._get_image_path(
            capture_result
        )

        if not image_path:

            return {
                "success": False,
                "selected": False,
                "message": (
                    "Screenshot was captured but "
                    "no image path was returned."
                ),
                "reason": "image_path_missing",
            }

        # --------------------------------------------------
        # Search target using OCR
        # --------------------------------------------------

        try:

            result = self.ocr.find(
                image_path,
                target,
            )

        except Exception as error:

            return {
                "success": False,
                "selected": False,
                "message": (
                    f"Visual target search failed: {error}"
                ),
                "reason": "ocr_find_error",
            }

        if not result.get(
            "success"
        ):

            result["selected"] = False
            result["image_path"] = image_path

            return result

        # --------------------------------------------------
        # Build candidates
        # --------------------------------------------------

        matches = result.get(
            "matches",
            []
        )

        candidates = self._build_candidates(
            matches
        )

        # --------------------------------------------------
        # Target selection
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
                "selected": False,
                "message": (
                    "Visual target selection failed: "
                    f"{error}"
                ),
                "reason": "target_selection_error",
                "image_path": image_path,
            }

        # Keep screenshot path so future visual-action
        # systems know which screen state was evaluated.

        selection["image_path"] = (
            image_path
        )

        return selection

    # ==================================================
    # AI SCREEN ANALYSIS
    # ==================================================

    def _analyze(self, parameters):

        # --------------------------------------------------
        # AI availability
        # --------------------------------------------------

        if self.analyzer is None:

            return {
                "success": False,
                "message": (
                    "Vision AI is currently unavailable. "
                    "Local screen capture, OCR, and "
                    "visual targeting are still operational."
                ),
                "reason": "vision_ai_unavailable",
            }

        # --------------------------------------------------
        # Capture current screen
        # --------------------------------------------------

        capture_result = (
            self.capture_service.capture()
        )

        if not capture_result.get(
            "success"
        ):

            return capture_result

        # --------------------------------------------------
        # Screenshot path
        # --------------------------------------------------

        image_path = self._get_image_path(
            capture_result
        )

        if not image_path:

            return {
                "success": False,
                "message": (
                    "Screenshot was captured but "
                    "no image path was returned."
                ),
                "reason": "image_path_missing",
            }

        # --------------------------------------------------
        # Optional prompt
        # --------------------------------------------------

        prompt = parameters.get(
            "prompt"
        )

        # --------------------------------------------------
        # AI analysis
        # --------------------------------------------------

        try:

            return self.analyzer.analyze(
                image_path=image_path,
                prompt=prompt,
            )

        except Exception as error:

            return {
                "success": False,
                "message": (
                    "Screen analysis is temporarily "
                    f"unavailable: {error}"
                ),
                "reason": "vision_ai_error",
            }

    # ==================================================
    # BUILD OCR CANDIDATES
    # ==================================================

    @staticmethod
    def _build_candidates(matches):

        candidates = []

        for index, match in enumerate(
            matches,
            start=1,
        ):

            center = match.get(
                "center",
                {}
            )

            # --------------------------------------------------
            # Center fallback
            # --------------------------------------------------

            center_x = center.get(
                "x"
            )

            center_y = center.get(
                "y"
            )

            x = match.get(
                "x"
            )

            y = match.get(
                "y"
            )

            width = match.get(
                "width"
            )

            height = match.get(
                "height"
            )

            # If OCR somehow doesn't provide center,
            # calculate it from bounding box.

            if (
                center_x is None
                and
                x is not None
                and
                width is not None
            ):

                center_x = (
                    x
                    + width // 2
                )

            if (
                center_y is None
                and
                y is not None
                and
                height is not None
            ):

                center_y = (
                    y
                    + height // 2
                )

            candidate = {

                "index": index,

                "text": match.get(
                    "text"
                ),

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
            }

            candidates.append(
                candidate
            )

        return candidates

    # ==================================================
    # SCREENSHOT PATH HELPER
    # ==================================================

    @staticmethod
    def _get_image_path(
        capture_result
    ):

        """
        Extract screenshot path while tolerating several
        ScreenCapture response formats.

        Expected possibilities:

            path
            image_path
            file
            filename
        """

        return (
            capture_result.get(
                "path"
            )
            or capture_result.get(
                "image_path"
            )
            or capture_result.get(
                "file"
            )
            or capture_result.get(
                "filename"
            )
        )