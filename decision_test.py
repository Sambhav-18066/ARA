from app.brain.planner import Planner
from app.kernel.decision_engine import DecisionEngine

planner = Planner()
decision_engine = DecisionEngine()

intent = planner.plan("Open Chrome")

decision = decision_engine.evaluate(intent)

print(intent)
print()

print("Approved :", decision.approved)
print("Reason   :", decision.reason)
print("Risk     :", decision.risk)