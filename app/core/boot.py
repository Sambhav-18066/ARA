from app.brain.planner import Planner

from app.kernel.decision_engine import DecisionEngine
from app.kernel.executor import Executor

from app.skills.windows import WindowsSkill
from app.skills.browser import BrowserSkill
from app.skills.system import SystemSkill
from app.skills.calculator import CalculatorSkill
from app.skills.vision import VisionSkill
from app.skills.visual_action import VisualActionSkill

from app.core.skill_registry import SkillRegistry


class BootManager:

    @staticmethod
    def boot(container):

        print("\n========== BOOTING ARA ==========\n")

        # ==================================================
        # CORE SERVICES
        # ==================================================

        planner = Planner()

        print("[OK] Planner")

        decision = DecisionEngine()

        print("[OK] Decision Engine")

        # ==================================================
        # SKILL REGISTRY
        # ==================================================

        registry = SkillRegistry()

        # --------------------------------------------------
        # WINDOWS
        # --------------------------------------------------

        registry.register(
            "windows",
            WindowsSkill(),
        )

        # --------------------------------------------------
        # BROWSER
        # --------------------------------------------------

        registry.register(
            "browser",
            BrowserSkill(),
        )

        # --------------------------------------------------
        # SYSTEM
        # --------------------------------------------------

        registry.register(
            "system",
            SystemSkill(),
        )

        # --------------------------------------------------
        # CALCULATOR
        # --------------------------------------------------

        registry.register(
            "calculator",
            CalculatorSkill(),
        )

        # --------------------------------------------------
        # VISION
        # --------------------------------------------------

        registry.register(
            "vision",
            VisionSkill(),
        )

        # --------------------------------------------------
        # VISUAL ACTION
        # --------------------------------------------------

        registry.register(
            "visual_action",
            VisualActionSkill(),
        )

        print("[OK] Skill Registry")

        # ==================================================
        # EXECUTOR
        # ==================================================

        executor = Executor(
            registry
        )

        print("[OK] Executor")

        # ==================================================
        # SERVICE CONTAINER
        # ==================================================

        container.register(
            "planner",
            planner,
        )

        container.register(
            "decision_engine",
            decision,
        )

        container.register(
            "registry",
            registry,
        )

        container.register(
            "executor",
            executor,
        )

        print("\nARA ONLINE\n")