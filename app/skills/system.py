import platform

from app.skills.base import Skill


def system_info():
    return {
        "os": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


class SystemSkill(Skill):

    name = "system"

    def execute(self, action, parameters):

        if action == "info":
            return {
                "success": True,
                "data": system_info()
            }

        return {
            "success": False,
            "message": "Unknown system action."
        }