import webbrowser

from app.skills.base import Skill


class BrowserSkill(Skill):

    name = "browser"

    def execute(self, action, parameters):

        if action == "open":

            url = parameters.get("url")

            if url:

                webbrowser.open(url)

                return {
                    "success": True,
                    "message": f"Opened {url}"
                }

        if action == "search":

            query = parameters.get("query")

            if query:

                url = (
                    "https://www.google.com/search?q="
                    + query.replace(" ", "+")
                )

                webbrowser.open(url)

                return {
                    "success": True,
                    "message": f"Searching for {query}"
                }

        return {
            "success": False,
            "message": "Unknown browser action."
        }