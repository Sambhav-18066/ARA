from app.core.event_bus import event_bus


class ARAEngine:

    def __init__(self):

        self.running = False

    def start(self):

        self.running = True

        print("\n============================")
        print("ARA ENGINE STARTED")
        print("============================")

        event_bus.emit("engine_started")

    def stop(self):

        self.running = False

        event_bus.emit("engine_stopped")