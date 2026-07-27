class Executor:

    def __init__(self, registry):
        self.registry = registry

    def execute(self, intent):

        skill = self.registry.get(intent.skill)

        if skill is None:
            return {
                "success": False,
                "message": "Skill not found."
            }

        return skill.execute(
            intent.action,
            intent.parameters
        )