from app.brain.planner import Planner

planner = Planner()

intent = planner.plan("Open Chrome")

print(intent)