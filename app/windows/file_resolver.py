from pathlib import Path
import os


class FileResolver:
    """
    Resolves local files and folders for ARA.

    v0.1 goals:
    - Search common user locations
    - Support exact filenames
    - Support case-insensitive matching
    - Prefer exact matches
    - Avoid scanning the entire drive
    - Return ambiguity instead of blindly guessing
    """

    MAX_RESULTS = 20

    def __init__(self):

        self.home = Path.home()

        # Common places where a user's files are likely
        # to exist.
        self.search_roots = self._build_search_roots()

    # ==================================================
    # SEARCH ROOTS
    # ==================================================

    def _build_search_roots(self):

        candidates = [
            self.home / "Desktop",
            self.home / "Downloads",
            self.home / "Documents",
            self.home / "Pictures",
            self.home / "Videos",
            self.home / "Music",
        ]

        # Add the current working directory.
        #
        # When ARA runs from the project directory this
        # also allows project files such as main.py to
        # be resolved.

        try:
            candidates.append(
                Path.cwd()
            )
        except Exception:
            pass

        roots = []

        seen = set()

        for path in candidates:

            try:
                resolved = path.resolve()
            except Exception:
                continue

            key = str(resolved).lower()

            if key in seen:
                continue

            if not resolved.exists():
                continue

            seen.add(key)
            roots.append(resolved)

        return roots

    # ==================================================
    # PUBLIC API
    # ==================================================

    def resolve(self, query):

        query = str(
            query or ""
        ).strip()

        if not query:

            return {
                "success": False,
                "reason": "query_missing",
                "message": "No file or folder was specified.",
                "candidates": [],
            }

        # --------------------------------------------------
        # SPECIAL WINDOWS RESOURCES
        # --------------------------------------------------

        special = self._resolve_special_resource(
            query
        )

        if special is not None:
            return special

        # --------------------------------------------------
        # DIRECT PATH
        #
        # Example:
        # C:\\Users\\Name\\Downloads\\image.png
        # .\\data\\example.json
        # --------------------------------------------------

        direct = self._resolve_direct_path(
            query
        )

        if direct is not None:
            return direct

        # --------------------------------------------------
        # SEARCH COMMON LOCATIONS
        # --------------------------------------------------

        candidates = self._search(
            query
        )

        if not candidates:

            return {
                "success": False,
                "reason": "resource_not_found",
                "message": (
                    f"File or folder '{query}' "
                    "could not be found."
                ),
                "query": query,
                "candidates": [],
            }

        # --------------------------------------------------
        # RANK
        # --------------------------------------------------

        candidates.sort(
            key=lambda item: (
                item["score"],
                -len(item["path"]),
            ),
            reverse=True,
        )

        best = candidates[0]

        # --------------------------------------------------
        # AMBIGUITY
        #
        # If several resources have the same best score,
        # don't silently choose one.
        # --------------------------------------------------

        equally_good = [
            item
            for item in candidates
            if item["score"] == best["score"]
        ]

        if len(equally_good) > 1:

            return {
                "success": False,
                "resolved": False,
                "reason": "ambiguous_resource",
                "message": (
                    f"Multiple matching files or folders "
                    f"were found for '{query}'."
                ),
                "query": query,
                "candidates": equally_good[
                    :self.MAX_RESULTS
                ],
            }

        return {
            "success": True,
            "resolved": True,
            "reason": "resource_resolved",
            "message": (
                f"Resolved '{query}' to "
                f"'{best['name']}'."
            ),
            "query": query,
            "resource": best,
            "candidates": candidates[
                :self.MAX_RESULTS
            ],
        }

    # ==================================================
    # SPECIAL WINDOWS RESOURCES
    # ==================================================

    def _resolve_special_resource(
        self,
        query,
    ):

        query_normalized = (
            str(query)
            .strip()
            .lower()
        )

        if not query_normalized:
            return None

        # --------------------------------------------------
        # DRIVE ROOT
        #
        # Examples:
        #   C:
        #   C:\
        #   E:
        #   E:\
        # --------------------------------------------------

        drive_query = query_normalized

        if (
            len(drive_query) == 2
            and drive_query[0].isalpha()
            and drive_query[1] == ":"
        ):
            drive_query += "\\"

        if (
            len(drive_query) == 3
            and drive_query[0].isalpha()
            and drive_query[1:] == ":\\"
        ):

            drive = Path(
                drive_query.upper()
            )

            if drive.exists():

                return self._resolved_result(
                    query=query,
                    path=drive,
                    score=150.0,
                    match_type="drive_root",
                )

            return {
                "success": False,
                "resolved": False,
                "reason": "drive_not_found",
                "message": (
                    f"Drive '{query}' "
                    "could not be found."
                ),
                "query": query,
                "candidates": [],
            }

        # --------------------------------------------------
        # KNOWN WINDOWS / USER FOLDERS
        # --------------------------------------------------

        home = self.home

        system_drive = (
            os.environ.get(
                "SystemDrive",
                "C:"
            )
        )

        program_files = (
            os.environ.get(
                "ProgramFiles",
                system_drive + r"\Program Files",
            )
        )

        program_files_x86 = (
            os.environ.get(
                "ProgramFiles(x86)",
                system_drive + r"\Program Files (x86)",
            )
        )

        known = {
            "desktop": home / "Desktop",
            "downloads": home / "Downloads",
            "documents": home / "Documents",
            "pictures": home / "Pictures",
            "images": home / "Pictures",
            "videos": home / "Videos",
            "music": home / "Music",

            "home": home,
            "user": home,
            "user folder": home,

            "program files": Path(
                program_files
            ),

            "program files x86": Path(
                program_files_x86
            ),

            "program files (x86)": Path(
                program_files_x86
            ),
        }

        target = known.get(
            query_normalized
        )

        if target is None:
            return None

        try:
            target = target.resolve()
        except Exception:
            return None

        if not target.exists():
            return None

        return self._resolved_result(
            query=query,
            path=target,
            score=140.0,
            match_type="known_folder",
        )

    def _resolved_result(
        self,
        query,
        path,
        score,
        match_type,
    ):

        try:
            resolved = path.resolve()
        except Exception:
            resolved = path

        resource = self._make_resource(
            resolved,
            score=score,
            match_type=match_type,
        )

        return {
            "success": True,
            "resolved": True,
            "reason": "resource_resolved",
            "message": (
                f"Resolved '{query}' to "
                f"'{resource['path']}'."
            ),
            "query": query,
            "resource": resource,
            "candidates": [
                resource
            ],
        }

    # ==================================================
    # DIRECT PATH
    # ==================================================

    def _resolve_direct_path(
        self,
        query,
    ):

        try:
            path = Path(
                os.path.expandvars(
                    os.path.expanduser(
                        query
                    )
                )
            )

        except Exception:
            return None

        # A plain filename such as "photo.png" should
        # continue to normal search unless it exists in
        # the current directory.

        try:

            if not path.exists():
                return None

            resolved = path.resolve()

        except Exception:
            return None

        resource = self._make_resource(
            resolved,
            score=120.0,
            match_type="direct_path",
        )

        return {
            "success": True,
            "resolved": True,
            "reason": "direct_path",
            "message": (
                f"Resolved '{query}' directly."
            ),
            "query": query,
            "resource": resource,
            "candidates": [
                resource
            ],
        }

    # ==================================================
    # SEARCH
    # ==================================================

    def _search(
        self,
        query,
    ):

        query_lower = query.lower()

        results = []

        seen = set()

        for root in self.search_roots:

                        # The search root itself may be the target.
            #
            # Example:
            #   "Downloads"
            #   "Desktop"
            #   "Documents"

            root_score = self._match_score(
                query_lower,
                root.name,
            )

            if root_score is not None:

                self._append_result(
                    path=root,
                    score=root_score,
                    match_type=self._match_type(
                        query_lower,
                        root.name,
                    ),
                    results=results,
                    seen=seen,
                )

            self._search_root(
                root=root,
                query=query,
                query_lower=query_lower,
                results=results,
                seen=seen,
            )

            if len(results) >= self.MAX_RESULTS:
                break

        return results

    def _search_root(
        self,
        root,
        query,
        query_lower,
        results,
        seen,
    ):

        try:

            for current_root, dirs, files in os.walk(
                root,
                topdown=True,
            ):

                # ------------------------------------------
                # SKIP NOISY / EXPENSIVE DIRECTORIES
                # ------------------------------------------

                dirs[:] = [
                    directory
                    for directory in dirs
                    if directory.lower()
                    not in {
                        ".git",
                        ".venv",
                        "venv",
                        "__pycache__",
                        "node_modules",
                        ".idea",
                        ".vscode",
                    }
                ]

                # ------------------------------------------
                # DIRECTORIES
                # ------------------------------------------

                for name in dirs:

                    score = self._match_score(
                        query_lower,
                        name,
                    )

                    if score is None:
                        continue

                    path = (
                        Path(current_root)
                        / name
                    )

                    self._append_result(
                        path=path,
                        score=score,
                        match_type=self._match_type(
                            query_lower,
                            name,
                        ),
                        results=results,
                        seen=seen,
                    )

                    if len(results) >= self.MAX_RESULTS:
                        return

                # ------------------------------------------
                # FILES
                # ------------------------------------------

                for name in files:

                    score = self._match_score(
                        query_lower,
                        name,
                    )

                    if score is None:
                        continue

                    path = (
                        Path(current_root)
                        / name
                    )

                    self._append_result(
                        path=path,
                        score=score,
                        match_type=self._match_type(
                            query_lower,
                            name,
                        ),
                        results=results,
                        seen=seen,
                    )

                    if len(results) >= self.MAX_RESULTS:
                        return

        except (
            PermissionError,
            OSError,
        ):
            return

    # ==================================================
    # MATCHING
    # ==================================================

    @staticmethod
    def _match_score(
        query_lower,
        name,
    ):

        name_lower = (
            str(name)
            .lower()
            .strip()
        )

        if not name_lower:
            return None

        # Exact filename / folder name.
        if name_lower == query_lower:
            return 100.0

        # Match without extension.
        stem_lower = (
            Path(name_lower)
            .stem
        )

        if stem_lower == query_lower:
            return 90.0

        # Prefix.
        if name_lower.startswith(
            query_lower
        ):
            return 75.0

        # Partial.
        if query_lower in name_lower:
            return 60.0

        return None

    @staticmethod
    def _match_type(
        query_lower,
        name,
    ):

        name_lower = (
            str(name)
            .lower()
            .strip()
        )

        if name_lower == query_lower:
            return "exact"

        if Path(name_lower).stem == query_lower:
            return "exact_stem"

        if name_lower.startswith(
            query_lower
        ):
            return "prefix"

        return "partial"

    # ==================================================
    # RESULT HELPERS
    # ==================================================

    def _append_result(
        self,
        path,
        score,
        match_type,
        results,
        seen,
    ):

        try:
            resolved = path.resolve()
        except Exception:
            return

        key = str(
            resolved
        ).lower()

        if key in seen:
            return

        seen.add(key)

        results.append(
            self._make_resource(
                resolved,
                score,
                match_type,
            )
        )

    @staticmethod
    def _make_resource(
        path,
        score,
        match_type,
    ):

        is_file = path.is_file()
        is_directory = path.is_dir()

        if is_file:
            resource_type = "file"

        elif is_directory:
            resource_type = "folder"

        else:
            resource_type = "unknown"

        return {
            "name": path.name,
            "path": str(path),
            "type": resource_type,
            "extension": (
                path.suffix.lower()
                if is_file
                else ""
            ),
            "score": round(
                float(score),
                2,
            ),
            "match_type": match_type,
        }