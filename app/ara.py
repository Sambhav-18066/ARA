# app/ara.py

from app.core.container import ServiceContainer

from app.brain.planner import Planner
from app.kernel.decision_engine import DecisionEngine

from app.core.skill_registry import SkillRegistry

# Import these when they are implemented
# from app.kernel.executor import Executor
# from app.memory.memory_manager import MemoryManager


class ARA:

    NAME = "ARA"
    VERSION = "0.2.0"
    CODENAME = "Genesis"

    def __init__(self):

        self.container = ServiceContainer()

        self.initialize()

    # --------------------------------------------------

    def initialize(self):

        print("\n========== BOOTING ARA ==========\n")

        planner = Planner()
        print("[OK] Planner")

        decision_engine = DecisionEngine()
        print("[OK] Decision Engine")

        registry = SkillRegistry()
        print("[OK] Skill Registry")

        # Uncomment once created

        # executor = Executor()
        # print("[OK] Executor")

        # memory = MemoryManager()
        # print("[OK] Memory")

        self.container.register("planner", planner)
        self.container.register("decision_engine", decision_engine)
        self.container.register("registry", registry)

        # self.container.register("executor", executor)
        # self.container.register("memory", memory)

        print("\nARA ONLINE\n")

    # --------------------------------------------------

    @property
    def version(self):

        return self.VERSION

    # --------------------------------------------------

    def process(self, user_input: str):

        planner = self.container.get("planner")

        decision_engine = self.container.get("decision_engine")

        intent = planner.plan(user_input)

        decision = decision_engine.evaluate(intent)

        return {

            "success": decision.approved,

            "reason": decision.reason,

            "risk": decision.risk,

            "intent": {

                "intent": intent.intent,

                "skill": intent.skill,

                "action": intent.action,

                "parameters": intent.parameters,

                "confidence": intent.confidence

            }

        }

    # --------------------------------------------------

    def status(self):

        return {

            "name": self.NAME,

            "version": self.VERSION,

            "codename": self.CODENAME,

            "status": "ONLINE"

        }