from pathlib import Path
import os
import re


class ApplicationResolver:
    """
    Discovers Windows applications from Start Menu shortcuts.

    v0.1:
    - Scan user Start Menu
    - Scan system Start Menu
    - Normalize application names
    - Resolve aliases/fuzzy names
    - Return the best application candidate
    """

    def __init__(self):

        self.applications = []

        self.refresh()

    # ==================================================
    # REFRESH APPLICATION INDEX
    # ==================================================

    def refresh(self):

        self.applications = []

        seen = set()

        for directory in self._start_menu_directories():

            if not directory.exists():
                continue

            try:

                shortcuts = directory.rglob("*.lnk")

            except Exception:
                continue

            for shortcut in shortcuts:

                name = shortcut.stem.strip()

                if not name:
                    continue

                normalized = self._normalize(name)

                if not normalized:
                    continue

                key = (
                    normalized,
                    str(shortcut).lower(),
                )

                if key in seen:
                    continue

                seen.add(key)

                self.applications.append(
                    {
                        "name": name,
                        "normalized_name": normalized,
                        "shortcut": str(shortcut),
                        "source": "start_menu",
                    }
                )

        self.applications.sort(
            key=lambda app: app["name"].lower()
        )

        return {
            "success": True,
            "count": len(self.applications),
            "applications": self.applications,
        }

    # ==================================================
    # RESOLVE APPLICATION
    # ==================================================

    def resolve(self, query):

        query = str(query or "").strip()

        if not query:

            return {
                "success": False,
                "reason": "application_missing",
                "message": "No application name was provided.",
            }

        normalized_query = self._normalize(query)

        if not normalized_query:

            return {
                "success": False,
                "reason": "application_missing",
                "message": "No valid application name was provided.",
            }

        candidates = []

        for application in self.applications:

            score = self._score(
                normalized_query,
                application["normalized_name"],
            )

            if score <= 0:
                continue

            candidate = dict(application)

            candidate["score"] = score

            candidates.append(candidate)

        candidates.sort(
            key=lambda item: (
                item["score"],
                -len(item["normalized_name"]),
            ),
            reverse=True,
        )

        if not candidates:

            return {
                "success": False,
                "reason": "application_not_found",
                "message": (
                    f"No installed application matched '{query}'."
                ),
                "query": query,
            }

        best = candidates[0]

        return {
            "success": True,
            "reason": "application_resolved",
            "message": (
                f"Resolved '{query}' to '{best['name']}'."
            ),
            "query": query,
            "application": best,
            "candidates": candidates[:10],
        }

    # ==================================================
    # LIST APPLICATIONS
    # ==================================================

    def list_applications(self):

        return {
            "success": True,
            "count": len(self.applications),
            "applications": list(self.applications),
        }

    # ==================================================
    # START MENU LOCATIONS
    # ==================================================

    @staticmethod
    def _start_menu_directories():

        directories = []

        appdata = os.environ.get("APPDATA")

        programdata = os.environ.get("PROGRAMDATA")

        if appdata:

            directories.append(
                Path(appdata)
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs"
            )

        if programdata:

            directories.append(
                Path(programdata)
                / "Microsoft"
                / "Windows"
                / "Start Menu"
                / "Programs"
            )

        return directories

    # ==================================================
    # SCORE APPLICATION
    # ==================================================

    @staticmethod
    def _score(query, application):

        # Exact match.

        if query == application:
            return 100.0

        query_words = query.split()

        application_words = application.split()

        # Query matches a complete word.
        #
        # "chrome" -> "google chrome"

        if query in application_words:
            return 90.0

        # Application starts with query.

        if application.startswith(query):
            return 85.0

        # Query occurs somewhere in application name.

        if query in application:
            return 75.0

        # Every query word appears in application name.

        if (
            query_words
            and all(
                word in application_words
                for word in query_words
            )
        ):
            return 70.0

        return 0.0

    # ==================================================
    # NORMALIZE
    # ==================================================

    @staticmethod
    def _normalize(text):

        text = str(text).lower().strip()

        text = re.sub(
            r"[^a-z0-9\s]+",
            " ",
            text,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()