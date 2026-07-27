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

        Uses Tesseract to extract visible text and
        bounding boxes from screenshots.
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
            image = Image.open(image_path)

            data = pytesseract.image_to_data(
                image,
                output_type=Output.DICT,
                config="--psm 6",
            )

            elements = []
            text_parts = []

            count = len(data["text"])

            for index in range(count):

                text = data["text"][index].strip()

                try:
                    confidence = float(
                        data["conf"][index]
                    )
                except (TypeError, ValueError):
                    confidence = -1.0

                # Ignore empty/unreliable OCR results.
                if not text:
                    continue

                if confidence < 0:
                    continue

                x = int(data["left"][index])
                y = int(data["top"][index])
                width = int(data["width"][index])
                height = int(data["height"][index])

                center_x = x + width // 2
                center_y = y + height // 2

                element = {
                    "text": text,
                    "confidence": round(
                        confidence,
                        2,
                    ),
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "center": {
                        "x": center_x,
                        "y": center_y,
                    },
                }

                elements.append(element)
                text_parts.append(text)

            full_text = " ".join(text_parts)

            return {
                "success": True,
                "message": "Screen text extracted successfully.",
                "text": full_text,
                "elements": elements,
                "count": len(elements),
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

    def find(self, image_path, target):

        if not target:
            return {
                "success": False,
                "message": "No target text provided.",
            }

        result = self.read(image_path)

        if not result.get("success"):
            return result

        target = target.strip().lower()

        matches = []

        for element in result["elements"]:

            detected = element["text"].lower()

            if target in detected:
                matches.append(element)

        if not matches:
            return {
                "success": False,
                "message": f"Text not found: {target}",
                "matches": [],
            }

        return {
            "success": True,
            "message": (
                f"Found {len(matches)} match(es) "
                f"for '{target}'."
            ),
            "matches": matches,
        }