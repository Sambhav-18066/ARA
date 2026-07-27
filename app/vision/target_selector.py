import re


class TargetSelector:
    """
    Context-aware visual target selector.

    Ranking signals:
    - OCR confidence
    - exact/partial text match
    - OCR noise
    - valid coordinates
    - surrounding OCR context
    - code/terminal-like context
    - sentence-like text context

    ARA should select a target only when the evidence
    is strong enough to justify acting on it.
    """

    # ==================================================
    # THRESHOLDS
    # ==================================================

    MIN_OCR_CONFIDENCE = 50.0

    AUTO_SELECT_SCORE = 80.0

    MIN_SCORE_GAP = 15.0

    HIGH_OCR_CONFIDENCE = 90.0

    HIGH_CONFIDENCE_MIN_GAP = 8.0

    # Even a candidate with excellent OCR confidence
    # should not be selected if contextual penalties
    # push its final score below this value.

    CONTEXT_MIN_SCORE = 80.0

    # ==================================================
    # CONTEXT SIGNALS
    # ==================================================

    CODE_MARKERS = (
        "python",
        "powershell",
        "pprint",
        "execute",
        "find_text",
        "select_text",
        "click_text",
        "center_x",
        "center_y",
        "confidence",
        "candidate",
        "__pycache__",
        ".py",
    )

    COMMAND_MARKERS = (
        "find ",
        "select ",
        "click ",
        "open ",
        "execute ",
        "text ",
        "target ",
    )

    # ==================================================
    # PUBLIC API
    # ==================================================

    def select(
        self,
        target,
        candidates,
    ):

        if not target:

            return {
                "success": False,
                "selected": False,
                "reason": "target_missing",
                "message": (
                    "No visual target was provided."
                ),
            }

        if not candidates:

            return {
                "success": False,
                "selected": False,
                "reason": "no_candidates",
                "message": (
                    f"No visual candidates found "
                    f"for '{target}'."
                ),
            }

        target_normalized = self._normalize(
            target
        )

        scored = []

        # --------------------------------------------------
        # SCORE ALL CANDIDATES
        # --------------------------------------------------

        for candidate in candidates:

            result = self._score_candidate(
                target_normalized,
                candidate,
            )

            if result is not None:

                scored.append(
                    result
                )

        # --------------------------------------------------
        # NOTHING SURVIVED OCR FILTERING
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

        # --------------------------------------------------
        # SORT STRONGEST FIRST
        # --------------------------------------------------

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
        # BEST CANDIDATE TOO WEAK
        # --------------------------------------------------

        if best["score"] < self.CONTEXT_MIN_SCORE:

            return {
                "success": False,
                "selected": False,
                "reason": (
                    "no_interactive_target"
                ),
                "message": (
                    "Visual text was found for "
                    f"'{target}', but no candidate "
                    "looked reliable enough to act on."
                ),
                "best_candidate": best,
                "candidates": scored,
            }

        # --------------------------------------------------
        # SINGLE STRONG CANDIDATE
        # --------------------------------------------------

        if second is None:

            return self._selected_result(
                target=target,
                best=best,
                candidates=scored,
                selection_mode=(
                    "single_candidate"
                ),
            )

        # --------------------------------------------------
        # COMPARE TOP TWO
        # --------------------------------------------------

        score_gap = (
            best["score"]
            - second["score"]
        )

        best_confidence = self._safe_float(
            best.get(
                "confidence",
                0,
            )
        )

        second_confidence = self._safe_float(
            second.get(
                "confidence",
                0,
            )
        )

        ocr_gap = (
            best_confidence
            - second_confidence
        )

        # --------------------------------------------------
        # HIGH-CONFIDENCE LEAD
        # --------------------------------------------------

        if (
            best_confidence
            >= self.HIGH_OCR_CONFIDENCE
            and
            score_gap
            >= self.HIGH_CONFIDENCE_MIN_GAP
        ):

            return self._selected_result(
                target=target,
                best=best,
                candidates=scored,
                selection_mode=(
                    "high_confidence_lead"
                ),
                score_gap=score_gap,
                ocr_gap=ocr_gap,
            )

        # --------------------------------------------------
        # NORMAL SCORE LEAD
        # --------------------------------------------------

        if score_gap >= self.MIN_SCORE_GAP:

            return self._selected_result(
                target=target,
                best=best,
                candidates=scored,
                selection_mode="score_lead",
                score_gap=score_gap,
                ocr_gap=ocr_gap,
            )

        # --------------------------------------------------
        # AMBIGUOUS
        # --------------------------------------------------

        return {
            "success": False,
            "selected": False,
            "reason": "ambiguous_target",
            "message": (
                f"Multiple strong visual targets "
                f"were found for '{target}'."
            ),
            "score_gap": round(
                score_gap,
                2,
            ),
            "ocr_gap": round(
                ocr_gap,
                2,
            ),
            "best_candidate": best,
            "second_candidate": second,
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
            candidate.get(
                "text",
                "",
            )
        ).strip()

        if not raw_text:

            return None

        confidence = self._safe_float(
            candidate.get(
                "confidence",
                0,
            )
        )

        # --------------------------------------------------
        # OCR FILTER
        # --------------------------------------------------

        if confidence < self.MIN_OCR_CONFIDENCE:

            return None

        detected_normalized = (
            self._normalize(
                raw_text
            )
        )

        if not detected_normalized:

            return None

        score = 0.0

        reasons = []

        # --------------------------------------------------
        # OCR CONFIDENCE
        #
        # Maximum: 50
        # --------------------------------------------------

        confidence_score = (
            min(
                max(
                    confidence,
                    0.0,
                ),
                100.0,
            )
            * 0.50
        )

        score += confidence_score

        reasons.append(
            f"ocr_confidence={confidence:.1f}"
        )

        # --------------------------------------------------
        # TEXT MATCH
        # --------------------------------------------------

        if (
            detected_normalized
            == target_normalized
        ):

            score += 50.0

            reasons.append(
                "exact_match"
            )

        elif (
            target_normalized
            in detected_normalized
        ):

            score += 20.0

            reasons.append(
                "partial_match"
            )

        else:

            return None

        # --------------------------------------------------
        # OCR NOISE
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
        # VALID CENTER
        # --------------------------------------------------

        center_x = candidate.get(
            "center_x"
        )

        center_y = candidate.get(
            "center_y"
        )

        if (
            center_x is not None
            and
            center_y is not None
        ):

            score += 5.0

            reasons.append(
                "valid_center"
            )

        # --------------------------------------------------
        # CONTEXT
        # --------------------------------------------------

        context_result = (
            self._score_context(
                target_normalized,
                candidate,
            )
        )

        score += context_result[
            "score"
        ]

        reasons.extend(
            context_result[
                "reasons"
            ]
        )

        # --------------------------------------------------
        # FINAL RESULT
        # --------------------------------------------------

        result = dict(
            candidate
        )

        result[
            "normalized_text"
        ] = detected_normalized

        result[
            "score"
        ] = round(
            score,
            2,
        )

        result[
            "score_reasons"
        ] = reasons

        result[
            "context_score"
        ] = round(
            context_result["score"],
            2,
        )

        return result

    # ==================================================
    # CONTEXT SCORING
    # ==================================================

    def _score_context(
        self,
        target_normalized,
        candidate,
    ):

        score = 0.0

        reasons = []

        surrounding = str(
            candidate.get(
                "surrounding_text",
                "",
            )
        ).strip()

        line_text = str(
            candidate.get(
                "line_text",
                "",
            )
        ).strip()

        previous_text = str(
            candidate.get(
                "previous_text",
                "",
            )
        ).strip()

        next_text = str(
            candidate.get(
                "next_text",
                "",
            )
        ).strip()

        combined = " ".join(
            part
            for part in (
                surrounding,
                line_text,
                previous_text,
                next_text,
            )
            if part
        )

        combined_lower = (
            combined.lower()
        )

        # --------------------------------------------------
        # NO CONTEXT AVAILABLE
        # --------------------------------------------------

        if not combined_lower:

            return {
                "score": 0.0,
                "reasons": [],
            }

        # --------------------------------------------------
        # CODE / TERMINAL SIGNALS
        # --------------------------------------------------

        code_hits = 0

        for marker in self.CODE_MARKERS:

            if marker in combined_lower:

                code_hits += 1

        if code_hits:

            penalty = min(
                code_hits * 10.0,
                35.0,
            )

            score -= penalty

            reasons.append(
                "code_context_penalty="
                f"-{penalty:.1f}"
            )

        # --------------------------------------------------
        # COMMAND-LIKE TEXT
        #
        # Examples:
        #
        # click chrome on my screen
        # find chrome on my screen
        # select chrome on my screen
        # --------------------------------------------------

        command_hits = 0

        for marker in self.COMMAND_MARKERS:

            if marker in combined_lower:

                command_hits += 1

        if command_hits:

            penalty = min(
                command_hits * 7.5,
                22.5,
            )

            score -= penalty

            reasons.append(
                "command_context_penalty="
                f"-{penalty:.1f}"
            )

        # --------------------------------------------------
        # CODE SYMBOL DENSITY
        # --------------------------------------------------

        symbol_count = len(
            re.findall(
                r"[{}\[\]()<>=\\\"']",
                combined,
            )
        )

        if symbol_count >= 3:

            penalty = min(
                symbol_count * 2.0,
                20.0,
            )

            score -= penalty

            reasons.append(
                "code_symbol_penalty="
                f"-{penalty:.1f}"
            )

        # --------------------------------------------------
        # LONG SENTENCE / PARAGRAPH CONTEXT
        #
        # A short isolated label such as:
        #
        #     Chrome
        #
        # is more target-like than:
        #
        #     we'll use the actual Chrome candidates...
        #
        # --------------------------------------------------

        words = re.findall(
            r"[a-zA-Z0-9]+",
            line_text,
        )

        word_count = len(
            words
        )

        if word_count >= 8:

            penalty = min(
                (word_count - 7) * 2.0,
                16.0,
            )

            score -= penalty

            reasons.append(
                "long_line_penalty="
                f"-{penalty:.1f}"
            )

        # --------------------------------------------------
        # ISOLATED LABEL BONUS
        #
        # If the OCR line is basically just the target,
        # that's useful evidence that it may be a label.
        # --------------------------------------------------

        normalized_line = (
            self._normalize(
                line_text
            )
        )

        if (
            normalized_line
            == target_normalized
        ):

            score += 10.0

            reasons.append(
                "isolated_label_bonus=+10.0"
            )

        return {
            "score": score,
            "reasons": reasons,
        }

    # ==================================================
    # SELECTED RESULT
    # ==================================================

    @staticmethod
    def _selected_result(
        target,
        best,
        candidates,
        selection_mode,
        score_gap=None,
        ocr_gap=None,
    ):

        result = {
            "success": True,
            "selected": True,
            "reason": "target_selected",

            "message": (
                "Selected visual target "
                f"'{best['text']}'."
            ),

            "target": target,

            "selection_mode": (
                selection_mode
            ),

            "candidate": best,

            "candidates": candidates,
        }

        if score_gap is not None:

            result[
                "score_gap"
            ] = round(
                score_gap,
                2,
            )

        if ocr_gap is not None:

            result[
                "ocr_gap"
            ] = round(
                ocr_gap,
                2,
            )

        return result

    # ==================================================
    # NORMALIZE
    # ==================================================

    @staticmethod
    def _normalize(text):

        text = (
            str(text)
            .lower()
            .strip()
        )

        text = re.sub(
            r"[^a-z0-9\s]+",
            "",
            text,
        )

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

        return len(
            re.findall(
                r"[^a-zA-Z0-9\s_-]",
                str(text),
            )
        )

    # ==================================================
    # SAFE FLOAT
    # ==================================================

    @staticmethod
    def _safe_float(value):

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0