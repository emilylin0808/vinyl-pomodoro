import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

class PomodoroApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pomodoro Timer")
        self.resizable(False, False)

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
        pad = 8

        frm = ttk.Frame(self, padding=pad)
        frm.grid(row=0, column=0)

        # Vinyl image
        self.vinyl_image = tk.PhotoImage(file="vinyl.png").subsample(3, 3)
        self.vinyl_label = ttk.Label(frm, image=self.vinyl_image)
        self.vinyl_label.grid(row=0, column=5, rowspan=5, padx=(20, 0))

        # Mode label
        self.mode_label = ttk.Label(frm, text=self.mode, font=(None, 14, "bold"))
        self.mode_label.grid(row=0, column=0, columnspan=3, pady=(0, 6))

        # Timer display
        self.timer_var = tk.StringVar(value="00:00")
        self.timer_label = ttk.Label(frm, textvariable=self.timer_var, font=(None, 36))
        self.timer_label.grid(row=1, column=0, columnspan=3, pady=(0, 6))

        # Duration controls
        ttk.Label(frm, text="Work (s):").grid(row=2, column=0, sticky="e")
        self.work_spin = ttk.Spinbox(frm, from_=1, to=3600, textvariable=self.work_seconds, width=6)
        self.work_spin.grid(row=2, column=1, sticky="w")

        self.work_minus_btn = ttk.Button(frm, text="-5", command=lambda: self.adjust_duration("work", -5))
        self.work_minus_btn.grid(row=2, column=2, padx=(8, 2))

        self.work_plus_btn = ttk.Button(frm, text="+5", command=lambda: self.adjust_duration("work", 5))
        self.work_plus_btn.grid(row=2, column=3, padx=(2, 8))

        ttk.Label(frm, text="Break (s):").grid(row=3, column=0, sticky="e")
        self.break_spin = ttk.Spinbox(frm, from_=1, to=3600, textvariable=self.break_seconds, width=6)
        self.break_spin.grid(row=3, column=1, sticky="w")

        self.break_minus_btn = ttk.Button(frm, text="-5", command=lambda: self.adjust_duration("break", -5))
        self.break_minus_btn.grid(row=3, column=2, padx=(8, 2))

        self.break_plus_btn = ttk.Button(frm, text="+5", command=lambda: self.adjust_duration("break", 5))
        self.break_plus_btn.grid(row=3, column=3, padx=(2, 8))

        # Session counter
        self.session_var = tk.StringVar(value=f"Sessions: {self.sessions_completed}")
        ttk.Label(frm, textvariable=self.session_var).grid(row=2, column=4, rowspan=2, padx=(12, 0))

        # Buttons
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=4, column=0, columnspan=5, pady=(8, 0))

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=4)

        self.pause_btn = ttk.Button(btn_frame, text="Pause", command=self.pause)
        self.pause_btn.grid(row=0, column=1, padx=4)

        self.reset_btn = ttk.Button(btn_frame, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=2, padx=4)

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
        self.mode_label.config(text=self.mode)
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
