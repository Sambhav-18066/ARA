from datetime import datetime


class BootManager:

    def boot(self):
        print("=" * 50)
        print("Booting ARA AI Operating System")
        print("=" * 50)

        print("[OK] Loading Brain")
        print("[OK] Loading Memory")
        print("[OK] Loading Skills")
        print("[OK] Loading Decision Engine")
        print("[OK] Loading Personality")

        print(f"[OK] Boot completed at {datetime.now()}")

        print("=" * 50)