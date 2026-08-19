import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PomodoroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Timer")
        self.resizable(True, True)

        # Defaults (seconds for quick testing)
        self.work_default = 25
        self.break_default = 10

        self.work_seconds = tk.IntVar(value=self.work_default)
        self.break_seconds = tk.IntVar(value=self.break_default)

        self.is_running = False
        self.after_id = None
        self.mode = "Work"  # or "Break"
        self.remaining = None
        self.sessions_completed = 0

        self._build_ui()
        self._reset_state()

    def _build_ui(self):
        # Window
        self.geometry("900x750")
        self.configure(bg="#B78C6E")

        # Main container
        main_frame = tk.Frame(
            self,
            bg="#B78C6E"
        )
        main_frame.pack(fill="both", expand=True)

        # Title
        self.title_label = tk.Label(
            main_frame,
            text="VINYL",
            font=("Georgia", 24, "bold"),
            bg="#B78C6E",
            fg="#2E2925"
        )
        self.title_label.pack(pady=(30, 5))

        # Mode
        self.mode_label = tk.Label(
            main_frame,
            text=self.mode.upper(),
            font=("Helvetica", 14),
            bg="#B78C6E",
            fg="#2E2925"
        )
        self.mode_label.pack()

        # Vinyl image
        vinyl = Image.open("vinyl.png")
        vinyl = vinyl.resize((250, 250))

        self.vinyl_image = ImageTk.PhotoImage(vinyl)

        self.vinyl_label = tk.Label(
            main_frame,
            image=self.vinyl_image,
            bg="#B78C6E"
        )
        self.vinyl_label.pack(pady=15)

        # Timer
        self.timer_var = tk.StringVar(value="00:00")

        self.timer_label = tk.Label(
            main_frame,
            textvariable=self.timer_var,
            font=("Helvetica", 48),
            bg="#B78C6E",
            fg="#2E2925"
        )
        self.timer_label.pack()

        # Session counter
        self.session_var = tk.StringVar(
            value=f"Session {self.sessions_completed}"
        )

        self.session_label = tk.Label(
            main_frame,
            textvariable=self.session_var,
            font=("Helvetica", 12),
            bg="#B78C6E",
            fg="#2E2925"
        )
        self.session_label.pack(pady=5)

        # Buttons
        button_frame = tk.Frame(
            main_frame,
            bg="#B78C6E"
        )
        button_frame.pack(pady=15)

        self.start_btn = tk.Button(
            button_frame,
            text="START",
            command=self.start,
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=10
        )
        self.start_btn.grid(row=0, column=0, padx=5)

        self.pause_btn = tk.Button(
            button_frame,
            text="PAUSE",
            command=self.pause,
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=10
        )
        self.pause_btn.grid(row=0, column=1, padx=5)

        self.reset_btn = tk.Button(
            button_frame,
            text="RESET",
            command=self.reset,
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=10
        )
        self.reset_btn.grid(row=0, column=2, padx=5)

    def adjust_duration(self, kind, delta):
        if kind == "work":
            current = int(self.work_seconds.get())
            new_value = max(1, current + delta)
            self.work_seconds.set(new_value)
            if self.mode == "Work" and not self.is_running:
                self.remaining = new_value
        elif kind == "break":
            current = int(self.break_seconds.get())
            new_value = max(1, current + delta)
            self.break_seconds.set(new_value)
            if self.mode == "Break" and not self.is_running:
                self.remaining = new_value

        if self.remaining is None:
            self.remaining = int(self.work_seconds.get())
        self._update_display()

    def _reset_state(self):
        self.is_running = False
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

        self.mode = "Work"
        self.remaining = int(self.work_seconds.get())
        self.sessions_completed = 0
        self._update_display()

    def _update_display(self):
        mins, secs = divmod(int(self.remaining), 60)
        self.timer_var.set(f"{mins:02d}:{secs:02d}")
        self.mode_label.config(text=self.mode.upper())
        self.session_var.set(f"Sessions: {self.sessions_completed}")

    def _tick(self):
        if not self.is_running:
            return

        if self.remaining is None:
            # initialize
            self.remaining = int(self.work_seconds.get()) if self.mode == "Work" else int(self.break_seconds.get())

        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
            self.after_id = self.after(1000, self._tick)
        else:
            # session ended — switch modes
            if self.mode == "Work":
                self.sessions_completed += 1
                self.mode = "Break"
                self.remaining = int(self.break_seconds.get())
            else:
                self.mode = "Work"
                self.remaining = int(self.work_seconds.get())

            self._update_display()
            self.after_id = self.after(1000, self._tick)

    def start(self):
        if self.is_running:
            return
        # If starting fresh (remaining is None or was reset), initialize from inputs
        if self.remaining is None:
            self.remaining = int(self.work_seconds.get()) if self.mode == "Work" else int(self.break_seconds.get())

        self.is_running = True
        self._tick()

    def pause(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def reset(self):
        self._reset_state()


if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()
