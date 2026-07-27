class SkillRegistry:
    """
    Stores and manages all available skills.

    Example:
        registry.register("windows", WindowsSkill())
        registry.register("browser", BrowserSkill())
        registry.register("system", SystemSkill())
        registry.register("calculator", CalculatorSkill())
        

        skill = registry.get("windows")
        skill.execute(...)
    """

    def __init__(self):
        self.skills = {}

    def register(self, name: str, skill):
        """Register a skill instance."""
        self.skills[name] = skill
        print(f"[Skill] Registered: {name}")

    def get(self, name: str):
        """Return a skill by name."""
        return self.skills.get(name)

    def exists(self, name: str) -> bool:
        """Check if a skill exists."""
        return name in self.skills

    def unregister(self, name: str):
        """Remove a skill."""
        if name in self.skills:
            del self.skills[name]

    def list_skills(self):
        """Return all registered skill names."""
        return list(self.skills.keys())

    def count(self):
        """Return number of registered skills."""
        return len(self.skills)