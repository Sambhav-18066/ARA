import re


class TargetSelector:
    """
    Selects the most likely OCR candidate for a requested
    visual target.

    v0.1 goals:
    - Prefer exact normalized text matches
    - Prefer high OCR confidence
    - Penalize noisy OCR results
    - Reject low-confidence candidates
    - Detect ambiguity
    - Never guess when two candidates are too similar
    """

    MIN_OCR_CONFIDENCE = 50.0

    AUTO_SELECT_SCORE = 80.0

    MIN_SCORE_GAP = 15.0

    # ==================================================
    # PUBLIC API
    # ==================================================

    def select(self, target, candidates):

        if not target:

            return {
                "success": False,
                "selected": False,
                "reason": "target_missing",
                "message": "No visual target was provided.",
            }

        if not candidates:

            return {
                "success": False,
                "selected": False,
                "reason": "no_candidates",
                "message": (
                    f"No visual candidates found for '{target}'."
                ),
            }

        target_normalized = self._normalize(target)

        scored = []

        # --------------------------------------------------
        # SCORE CANDIDATES
        # --------------------------------------------------

        for candidate in candidates:

            result = self._score_candidate(
                target_normalized,
                candidate,
            )

            if result is not None:
                scored.append(result)

        # --------------------------------------------------
        # NOTHING SURVIVED FILTERING
        # --------------------------------------------------

        if not scored:

            return {
                "success": False,
                "selected": False,
                "reason": "no_reliable_candidates",
                "message": (
                    f"No reliable visual target found "
                    f"for '{target}'."
                ),
            }

        # Highest score first.

        scored.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        best = scored[0]

        second = (
            scored[1]
            if len(scored) > 1
            else None
        )

        # --------------------------------------------------
        # BEST CANDIDATE STILL TOO WEAK
        # --------------------------------------------------

        if best["score"] < self.AUTO_SELECT_SCORE:

            return {
                "success": False,
                "selected": False,
                "reason": "low_target_confidence",
                "message": (
                    f"Visual candidates were found for "
                    f"'{target}', but none were reliable "
                    f"enough to select automatically."
                ),
                "best_candidate": best,
                "candidates": scored,
            }

        # --------------------------------------------------
        # AMBIGUITY CHECK
        # --------------------------------------------------

        if second is not None:

            gap = (
                best["score"]
                - second["score"]
            )

            if gap < self.MIN_SCORE_GAP:

                return {
                    "success": False,
                    "selected": False,
                    "reason": "ambiguous_target",
                    "message": (
                        f"Multiple possible visual targets "
                        f"were found for '{target}'."
                    ),
                    "score_gap": round(gap, 2),
                    "candidates": scored,
                }

        # --------------------------------------------------
        # TARGET SELECTED
        # --------------------------------------------------

        return {
            "success": True,
            "selected": True,
            "reason": "target_selected",
            "message": (
                f"Selected visual target '{best['text']}'."
            ),
            "target": target,
            "candidate": best,
            "candidates": scored,
        }

    # ==================================================
    # SCORE CANDIDATE
    # ==================================================

    def _score_candidate(
        self,
        target_normalized,
        candidate,
    ):

        raw_text = str(
            candidate.get("text", "")
        ).strip()

        if not raw_text:
            return None

        try:

            confidence = float(
                candidate.get(
                    "confidence",
                    0,
                )
            )

        except (TypeError, ValueError):

            confidence = 0.0

        # --------------------------------------------------
        # REJECT LOW OCR CONFIDENCE
        # --------------------------------------------------

        if confidence < self.MIN_OCR_CONFIDENCE:
            return None

        detected_normalized = self._normalize(
            raw_text
        )

        if not detected_normalized:
            return None

        score = 0.0

        reasons = []

        # --------------------------------------------------
        # OCR CONFIDENCE
        #
        # Max contribution: 50 points
        # --------------------------------------------------

        confidence_score = (
            min(
                max(confidence, 0.0),
                100.0,
            )
            * 0.50
        )

        score += confidence_score

        reasons.append(
            f"ocr_confidence={confidence:.1f}"
        )

        # --------------------------------------------------
        # EXACT NORMALIZED MATCH
        #
        # Strongest textual signal.
        # --------------------------------------------------

        if detected_normalized == target_normalized:

            score += 50.0

            reasons.append(
                "exact_match"
            )

        # --------------------------------------------------
        # PARTIAL MATCH
        # --------------------------------------------------

        elif target_normalized in detected_normalized:

            score += 20.0

            reasons.append(
                "partial_match"
            )

        else:

            # Candidate no longer resembles the target.
            return None

        # --------------------------------------------------
        # OCR NOISE PENALTY
        #
        # Example:
        #
        # Chrome       -> clean
        # 'chrome',    -> noisy
        # “chrome"}))  -> very noisy
        # --------------------------------------------------

        noise = self._noise_count(
            raw_text
        )

        if noise:

            penalty = min(
                noise * 4.0,
                20.0,
            )

            score -= penalty

            reasons.append(
                f"noise_penalty=-{penalty:.1f}"
            )

        # --------------------------------------------------
        # VALID COORDINATES
        # --------------------------------------------------

        center_x = candidate.get(
            "center_x"
        )

        center_y = candidate.get(
            "center_y"
        )

        if (
            center_x is not None
            and center_y is not None
        ):

            score += 5.0

            reasons.append(
                "valid_center"
            )

        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        result = dict(candidate)

        result["normalized_text"] = (
            detected_normalized
        )

        result["score"] = round(
            score,
            2,
        )

        result["score_reasons"] = (
            reasons
        )

        return result

    # ==================================================
    # NORMALIZE TEXT
    # ==================================================

    @staticmethod
    def _normalize(text):

        text = str(text).lower().strip()

        # Remove punctuation/noise around OCR words
        # while retaining letters, digits and spaces.

        text = re.sub(
            r"[^a-z0-9\s]+",
            "",
            text,
        )

        # Collapse repeated whitespace.

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ==================================================
    # OCR NOISE
    # ==================================================

    @staticmethod
    def _noise_count(text):

        """
        Count punctuation/symbol characters surrounding
        OCR text.

        Letters, digits, spaces, hyphens and underscores
        are treated as normal.
        """

        return len(
            re.findall(
                r"[^a-zA-Z0-9\s_-]",
                str(text),
            )
        )