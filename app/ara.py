from urllib import response

from app.intent.local_router import LocalRouter
from app.core.container import ServiceContainer
from app.core.boot import BootManager
from app.core.renderer import ResponseRenderer


class ARA:

    NAME = "ARA"
    VERSION = "0.2.0"
    CODENAME = "Genesis"

    def __init__(self):
        self.container = ServiceContainer()
        self.local_router = LocalRouter()
        self.online = False

    @property
    def version(self):
        return self.VERSION

    @property
    def name(self):
        return self.NAME

    @property
    def codename(self):
        return self.CODENAME

    # ==================================================
    # BOOT
    # ==================================================

    def boot(self):

        if self.online:
            return

        BootManager.boot(self.container)
        self.online = True

    # ==================================================
    # PROCESS USER REQUEST
    # ==================================================

    def process(self, prompt: str):

        if not self.online:
            raise RuntimeError("ARA is not booted.")

        print("\n========== ARA ==========")
        print("User:", prompt)

        planner = self.container.get("planner")
        decision_engine = self.container.get("decision_engine")
        executor = self.container.get("executor")

        # ==================================================
        # LOCAL ROUTER
        # ==================================================

        intent = self.local_router.route(prompt)

        if intent:

            print("\n[LOCAL ROUTER]")

            # ==============================================
            # MULTI-STEP LOCAL PLAN
            # ==============================================

            if isinstance(intent, list):

                print(f"Matched {len(intent)} local actions.")

                results = []

                for index, step in enumerate(intent, start=1):

                    print(
                        f"\n[STEP {index}/{len(intent)}]"
                    )

                    print("Intent:", step)

                    # --------------------------------------
                    # SAFETY CHECK
                    # --------------------------------------

                    decision = decision_engine.evaluate(step)

                    print("Decision:", decision)

                    if not decision.approved:

                        return {
                            "success": False,
                            "message": decision.reason,
                            "reason": decision.reason,
                            "risk": decision.risk,
                            "completed_steps": index - 1,
                            "results": results,
                        }

                    # --------------------------------------
                    # EXECUTE STEP
                    # --------------------------------------

                    result = executor.execute(step)

                    results.append(result)

                    print("Result:", result)

                    # --------------------------------------
                    # STOP IF STEP FAILED
                    # --------------------------------------

                    if not result.get("success", False):

                        return {
                            "success": False,
                            "message": result.get(
                                "message",
                                "Sequence execution failed.",
                            ),
                            "completed_steps": index - 1,
                            "results": results,
                        }

                    # --------------------------------------
                    # APPLICATION STARTUP DELAY
                    # --------------------------------------

                    # Temporary solution.
                    # Later we'll replace this with
                    # window detection and focus control.
                   

                return {
                    "success": True,
                    "message": "Task completed successfully.",
                    "results": results,
                }

            # ==============================================
            # SINGLE LOCAL INTENT
            # ==============================================

            print("Matched command locally.")

        else:

            # ==================================================
            # AI PLANNER FALLBACK
            # ==================================================

            print("\n[AI PLANNER]")
            print(
                "No local match. Sending request to Gemini."
            )

            try:

                intent = planner.plan(prompt)

            except Exception as error:

                print(f"\n[AI ERROR] {error}")

                return {
                    "success": False,
                    "message": (
                        "My AI reasoning service is temporarily "
                        "unavailable. Local capabilities are "
                        "still operational."
                    ),
                    "reason": "ai_unavailable",
                    "risk": "NONE",
                }

        # ==================================================
        # SINGLE INTENT PIPELINE
        # ==================================================

        print("Intent:", intent)

        # --------------------------------------------------
        # UNSUPPORTED REQUEST
        # --------------------------------------------------

        if intent.intent == "unsupported":

            return {
                "success": False,
                "message": "I can't perform that request yet.",
                "reason": "unsupported",
                "risk": "NONE",
            }
        # --------------------------------------------------
        # DECISION ENGINE
        # --------------------------------------------------

        decision = decision_engine.evaluate(intent)

        print("Decision:", decision)

        if not decision.approved:

            return {
                "success": False,
                "message": decision.reason,
                "reason": decision.reason,
                "risk": decision.risk,
            }

        # --------------------------------------------------
        # EXECUTION
        # --------------------------------------------------

        result = executor.execute(intent)

        return result

    # ==================================================
    # STATUS
    # ==================================================

    def status(self):

        return {
            "name": self.NAME,
            "version": self.VERSION,
            "codename": self.CODENAME,
            "status": (
                "ONLINE"
                if self.online
                else "OFFLINE"
            ),
        }

    # ==================================================
    # SHUTDOWN
    # ==================================================

    def shutdown(self):

        self.online = False

        return {
            "success": True,
            "message": "ARA shutdown successfully.",
        }

    # ==================================================
    # SERVICE ACCESS
    # ==================================================

    def service(self, name: str):

        return self.container.get(name)


# ==========================================================
# COMMAND LINE INTERFACE
# ==========================================================

def main():

    ara = ARA()

    try:

        # ==================================================
        # BOOT
        # ==================================================

        ara.boot()

        print("=" * 40)
        print(
            f"{ara.name} v{ara.version} — "
            f"{ara.codename}"
        )
        print("Status: ONLINE")
        print(
            "Type 'exit' or 'quit' to shut down ARA."
        )
        print("=" * 40)
        print()

        # ==================================================
        # MAIN LOOP
        # ==================================================

        while True:

            try:

                user_input = input("You > ").strip()

                # ------------------------------------------
                # EMPTY INPUT
                # ------------------------------------------

                if not user_input:
                    continue

                # ------------------------------------------
                # EXIT
                # ------------------------------------------

                if user_input.lower() in {
                    "exit",
                    "quit",
                }:

                    result = ara.shutdown()

                    print()
                    print(
                        "ARA >",
                        result["message"],
                    )

                    break

                # ------------------------------------------
                # PROCESS COMMAND
                # ------------------------------------------

                result = ara.process(user_input)

                print()

                # ------------------------------------------
                # CLEAN RESPONSE
                # ------------------------------------------

                response = ResponseRenderer.render(result)

                print("ARA >", response)

                print()

            # ==================================================
            # CTRL + C
            # ==================================================

            except KeyboardInterrupt:

                print()

                result = ara.shutdown()

                print(
                    "ARA >",
                    result["message"],
                )

                break

            # ==================================================
            # COMMAND ERROR
            # ==================================================

            except Exception as error:

                print()
                print(
                    f"ARA > Error: {error}"
                )
                print()

    # ==========================================================
    # BOOT ERROR
    # ==========================================================

    except Exception as error:

        print()
        print(
            f"[BOOT ERROR] {error}"
        )


# ==============================================================
# ENTRY POINT
# ==============================================================

if __name__ == "__main__":
    main()