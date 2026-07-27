from pathlib import Path

import pytesseract
from PIL import Image
from pytesseract import Output


class LocalOCR:

    def __init__(
        self,
        tesseract_path=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    ):
        """
        Local OCR engine for ARA.

        Extracts:
        - visible text
        - OCR confidence
        - bounding boxes
        - click coordinates
        - screen position
        - OCR line/block information
        - nearby text context
        """

        self.tesseract_path = Path(tesseract_path)

        if self.tesseract_path.exists():
            pytesseract.pytesseract.tesseract_cmd = str(
                self.tesseract_path
            )

    # ==================================================
    # READ IMAGE
    # ==================================================

    def read(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            return {
                "success": False,
                "message": f"Image not found: {image_path}",
            }

        try:

            with Image.open(image_path) as image:

                screen_width, screen_height = image.size

                data = pytesseract.image_to_data(
                    image,
                    output_type=Output.DICT,
                    config="--psm 6",
                )

            elements = []
            text_parts = []

            count = len(data["text"])

            # --------------------------------------------------
            # BUILD OCR ELEMENTS
            # --------------------------------------------------

            for index in range(count):

                text = str(
                    data["text"][index]
                ).strip()

                try:

                    confidence = float(
                        data["conf"][index]
                    )

                except (TypeError, ValueError):

                    confidence = -1.0

                if not text:
                    continue

                if confidence < 0:
                    continue

                x = int(
                    data["left"][index]
                )

                y = int(
                    data["top"][index]
                )

                width = int(
                    data["width"][index]
                )

                height = int(
                    data["height"][index]
                )

                center_x = (
                    x + width // 2
                )

                center_y = (
                    y + height // 2
                )

                region = self._screen_region(
                    center_x=center_x,
                    center_y=center_y,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )

                near_edge = self._near_screen_edge(
                    center_x=center_x,
                    center_y=center_y,
                    screen_width=screen_width,
                    screen_height=screen_height,
                )

                element = {
                    "index": index,

                    "text": text,

                    "confidence": round(
                        confidence,
                        2,
                    ),

                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,

                    # Keep old API.
                    "center": {
                        "x": center_x,
                        "y": center_y,
                    },

                    # New flat API for target selection.
                    "center_x": center_x,
                    "center_y": center_y,

                    # Screen geometry.
                    "screen_width": screen_width,
                    "screen_height": screen_height,

                    "screen_region": region,
                    "near_screen_edge": near_edge,

                    # Relative coordinates.
                    "relative_x": round(
                        center_x / screen_width,
                        4,
                    ) if screen_width else 0,

                    "relative_y": round(
                        center_y / screen_height,
                        4,
                    ) if screen_height else 0,

                    # Tesseract structural metadata.
                    "page_num": self._safe_int(
                        data,
                        "page_num",
                        index,
                    ),

                    "block_num": self._safe_int(
                        data,
                        "block_num",
                        index,
                    ),

                    "par_num": self._safe_int(
                        data,
                        "par_num",
                        index,
                    ),

                    "line_num": self._safe_int(
                        data,
                        "line_num",
                        index,
                    ),

                    "word_num": self._safe_int(
                        data,
                        "word_num",
                        index,
                    ),
                }

                elements.append(element)

                text_parts.append(text)

            # --------------------------------------------------
            # ADD CONTEXT
            # --------------------------------------------------

            self._attach_context(
                elements
            )

            full_text = " ".join(
                text_parts
            )

            return {
                "success": True,
                "message": (
                    "Screen text extracted successfully."
                ),
                "text": full_text,
                "elements": elements,
                "count": len(elements),

                "screen": {
                    "width": screen_width,
                    "height": screen_height,
                },

                "image_path": str(
                    image_path.resolve()
                ),
            }

        except Exception as error:

            return {
                "success": False,
                "message": f"OCR failed: {error}",
            }

    # ==================================================
    # FIND TEXT
    # ==================================================

    def find(
        self,
        image_path,
        target,
    ):

        if not target:

            return {
                "success": False,
                "message": "No target text provided.",
            }

        result = self.read(
            image_path
        )

        if not result.get("success"):
            return result

        target_normalized = (
            self._normalize_text(
                target
            )
        )

        matches = []

        for element in result["elements"]:

            detected_normalized = (
                self._normalize_text(
                    element["text"]
                )
            )

            if (
                target_normalized
                in detected_normalized
            ):

                matches.append(
                    element
                )

        if not matches:

            return {
                "success": False,
                "message": (
                    f"Text not found: {target}"
                ),
                "target": target,
                "matches": [],
                "image_path": result.get(
                    "image_path"
                ),
            }

        return {
            "success": True,

            "message": (
                f"Found {len(matches)} match(es) "
                f"for '{target}'."
            ),

            "target": target,
            "matches": matches,

            "screen": result.get(
                "screen"
            ),

            "image_path": result.get(
                "image_path"
            ),
        }

    # ==================================================
    # ATTACH OCR CONTEXT
    # ==================================================

    def _attach_context(
        self,
        elements,
    ):

        """
        Add nearby OCR text to each element.

        Context is useful for distinguishing:

            Chrome

        appearing as a UI label from:

            click chrome on my screen

        appearing inside a terminal or editor.
        """

        for index, element in enumerate(
            elements
        ):

            # --------------------------------------------------
            # SAME OCR LINE
            # --------------------------------------------------

            same_line = []

            for other in elements:

                if other is element:
                    continue

                if self._same_line(
                    element,
                    other,
                ):

                    same_line.append(
                        other
                    )

            same_line.sort(
                key=lambda item: item["x"]
            )

            line_words = [
                item["text"]
                for item in same_line
            ]

            # --------------------------------------------------
            # NEIGHBORING WORDS
            # --------------------------------------------------

            previous_elements = (
                elements[
                    max(0, index - 3):
                    index
                ]
            )

            next_elements = (
                elements[
                    index + 1:
                    index + 4
                ]
            )

            previous_text = [
                item["text"]
                for item in previous_elements
            ]

            next_text = [
                item["text"]
                for item in next_elements
            ]

            # --------------------------------------------------
            # CONTEXT WINDOW
            # --------------------------------------------------

            context_parts = (
                previous_text
                + [element["text"]]
                + next_text
            )

            element["line_text"] = (
                " ".join(
                    line_words
                )
            )

            element["previous_text"] = (
                " ".join(
                    previous_text
                )
            )

            element["next_text"] = (
                " ".join(
                    next_text
                )
            )

            element["surrounding_text"] = (
                " ".join(
                    context_parts
                )
            )

    # ==================================================
    # SAME OCR LINE
    # ==================================================

    @staticmethod
    def _same_line(
        first,
        second,
    ):

        return (
            first.get("page_num")
            == second.get("page_num")
            and
            first.get("block_num")
            == second.get("block_num")
            and
            first.get("par_num")
            == second.get("par_num")
            and
            first.get("line_num")
            == second.get("line_num")
        )

    # ==================================================
    # SCREEN REGION
    # ==================================================

    @staticmethod
    def _screen_region(
        center_x,
        center_y,
        screen_width,
        screen_height,
    ):

        """
        Divide screen into a 3 x 3 grid.

        Examples:
            top_left
            center
            bottom_right
        """

        if (
            screen_width <= 0
            or screen_height <= 0
        ):
            return "unknown"

        relative_x = (
            center_x / screen_width
        )

        relative_y = (
            center_y / screen_height
        )

        # Horizontal.

        if relative_x < 0.33:
            horizontal = "left"

        elif relative_x > 0.67:
            horizontal = "right"

        else:
            horizontal = "center"

        # Vertical.

        if relative_y < 0.33:
            vertical = "top"

        elif relative_y > 0.67:
            vertical = "bottom"

        else:
            vertical = "center"

        if (
            horizontal == "center"
            and vertical == "center"
        ):
            return "center"

        return (
            f"{vertical}_{horizontal}"
        )

    # ==================================================
    # SCREEN EDGE DETECTION
    # ==================================================

    @staticmethod
    def _near_screen_edge(
        center_x,
        center_y,
        screen_width,
        screen_height,
    ):

        """
        Detect elements close to a screen edge.

        This is metadata only. It does NOT automatically
        mean the candidate is a better target.
        """

        if (
            screen_width <= 0
            or screen_height <= 0
        ):
            return False

        horizontal_margin = (
            screen_width * 0.08
        )

        vertical_margin = (
            screen_height * 0.08
        )

        return (
            center_x <= horizontal_margin
            or
            center_x >= (
                screen_width
                - horizontal_margin
            )
            or
            center_y <= vertical_margin
            or
            center_y >= (
                screen_height
                - vertical_margin
            )
        )

    # ==================================================
    # NORMALIZE TEXT
    # ==================================================

    @staticmethod
    def _normalize_text(
        text,
    ):

        return (
            str(text)
            .strip()
            .lower()
        )

    # ==================================================
    # SAFE INTEGER
    # ==================================================

    @staticmethod
    def _safe_int(
        data,
        key,
        index,
    ):

        try:

            return int(
                data[key][index]
            )

        except (
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ):

            return 0