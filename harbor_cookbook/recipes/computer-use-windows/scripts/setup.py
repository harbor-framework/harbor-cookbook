"""Setup script for the computer-use-windows recipe.

Uploaded to the Windows sandbox and executed during environment startup.
Deploys the challenge app and launches it on the desktop.
"""

import os
import subprocess
import textwrap

CHALLENGE_DIR = r"C:\harbor_challenge"
CHALLENGE_PY = os.path.join(CHALLENGE_DIR, "challenge.py")
APP_DIR = r"C:\app"

CHALLENGE_SOURCE = textwrap.dedent('''\
    """Multi-step tkinter challenge that requires genuine GUI interaction."""

    import tkinter as tk


    class ChallengeApp:
        SECRET_CODE = "HARBOR-CU-2025-VERIFIED"
        PASSPHRASE = "open sesame"

        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.root.title("Harbor Challenge")
            self.root.geometry("800x500")
            self.root.resizable(False, False)

            self.frame = tk.Frame(self.root)
            self.frame.pack(expand=True)

            self.show_welcome()

        def clear(self) -> None:
            for widget in self.frame.winfo_children():
                widget.destroy()

        def show_welcome(self) -> None:
            self.clear()
            tk.Label(
                self.frame,
                text="Welcome to the Harbor Challenge",
                font=("Helvetica", 26),
            ).pack(pady=(60, 30))
            tk.Label(
                self.frame,
                text="Click the button below to begin.",
                font=("Helvetica", 18),
            ).pack(pady=10)
            tk.Button(
                self.frame,
                text="Start Challenge",
                font=("Helvetica", 18),
                width=20,
                command=self.show_passphrase,
            ).pack(pady=40)

        def show_passphrase(self) -> None:
            self.clear()
            tk.Label(
                self.frame,
                text="Enter the passphrase to continue:",
                font=("Helvetica", 22),
            ).pack(pady=(60, 10))
            tk.Label(
                self.frame,
                text=f"The passphrase is: {self.PASSPHRASE}",
                font=("Helvetica", 18),
                fg="blue",
            ).pack(pady=10)

            self.entry = tk.Entry(self.frame, font=("Helvetica", 18), width=30)
            self.entry.pack(pady=20)
            self.entry.focus_set()

            self.error_label = tk.Label(
                self.frame, text="", font=("Helvetica", 14), fg="red"
            )
            self.error_label.pack(pady=5)

            tk.Button(
                self.frame,
                text="Submit",
                font=("Helvetica", 18),
                width=20,
                command=self.check_passphrase,
            ).pack(pady=10)

        def check_passphrase(self) -> None:
            if self.entry.get().strip().lower() == self.PASSPHRASE:
                self.show_secret()
            else:
                self.error_label.config(text="Wrong passphrase. Try again.")

        def show_secret(self) -> None:
            self.clear()
            tk.Label(
                self.frame,
                text="Congratulations!",
                font=("Helvetica", 26),
                fg="green",
            ).pack(pady=(80, 30))
            tk.Label(
                self.frame,
                text=f"SECRET_CODE: {self.SECRET_CODE}",
                font=("Helvetica", 22),
            ).pack(pady=20)


    if __name__ == "__main__":
        root = tk.Tk()
        ChallengeApp(root)
        root.mainloop()
''')


def main():
    # Create directories
    os.makedirs(CHALLENGE_DIR, exist_ok=True)
    os.makedirs(APP_DIR, exist_ok=True)

    # Write challenge app
    with open(CHALLENGE_PY, "w") as f:
        f.write(CHALLENGE_SOURCE)
    print(f"Wrote challenge app to {CHALLENGE_PY}")

    # Install pyautogui (needed for CUA desktop interface)
    subprocess.run(
        ["python", "-m", "pip", "install", "pyautogui", "Pillow"],
        check=False,
    )

    # Launch challenge app in the background
    subprocess.Popen(
        ["python", CHALLENGE_PY],
        creationflags=0x00000008,  # DETACHED_PROCESS on Windows
    )
    print("Launched challenge app on desktop")


if __name__ == "__main__":
    main()
