import tkinter as tk
from pathlib import Path
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
        self.session_target = tk.IntVar(value=1)

        self.is_running = False
        self.after_id = None
        self.mode = "Work"  # or "Break"
        self.remaining = None
        self.sessions_completed = 0
        self.setup_frame = None
        self.timer_frame = None
        self.error_var = tk.StringVar()

        self._build_setup_screen()

    def _build_setup_screen(self):
        self.geometry("900x750")
        self.configure(bg="#B78C6E")

        self.setup_frame = tk.Frame(
            self,
            padx=40,
            pady=40,
            bg="#B78C6E"
        )
        self.setup_frame.pack(fill="both", expand=True)

        self.title_label = tk.Label(
            self.setup_frame,
            text="VINYL",
            font=("Georgia", 24, "bold"),
            bg="#B78C6E",
            fg="#2E2925"
        )
        self.title_label.pack(pady=(70, 8))

        tk.Label(
            self.setup_frame,
            text="Plan your study session",
            font=("Helvetica", 16),
            bg="#B78C6E",
            fg="#2E2925"
        ).pack(pady=(0, 24))

        fields = tk.Frame(self.setup_frame, bg="#B78C6E")
        fields.pack()
        validate_digits = (self.register(self._digits_only), "%P")
        self._add_setup_field(fields, "Sessions today:", self.session_target, 0, validate_digits)
        self._add_setup_field(fields, "Work duration (seconds):", self.work_seconds, 1, validate_digits)
        self._add_setup_field(fields, "Break duration (seconds):", self.break_seconds, 2, validate_digits)

        tk.Label(
            self.setup_frame,
            textvariable=self.error_var,
            font=("Helvetica", 10),
            bg="#B78C6E",
            fg="#8B1E1E"
        ).pack(pady=(16, 4))

        tk.Button(
            self.setup_frame,
            text="START STUDY",
            command=self.start_from_setup,
            font=("Helvetica", 12, "bold"),
            padx=25,
            pady=10
        ).pack(pady=10)

    def _add_setup_field(self, parent, label_text, variable, row, validate):
        tk.Label(parent, text=label_text, font=("Helvetica", 12), bg="#B78C6E", fg="#2E2925").grid(
            row=row, column=0, sticky="e", padx=8, pady=8
        )
        tk.Entry(
            parent, textvariable=variable, validate="key", validatecommand=validate,
            font=("Helvetica", 12), width=10, justify="center"
        ).grid(row=row, column=1, padx=8, pady=8)

    @staticmethod
    def _digits_only(value):
        return value.isdigit() or value == ""

    def _build_timer_screen(self):
        self.timer_frame = tk.Frame(self, bg="#B78C6E")
        self.timer_frame.pack(fill="both", expand=True)

        tk.Label(self.timer_frame, text="VINYL", font=("Georgia", 24, "bold"), bg="#B78C6E", fg="#2E2925").pack(pady=(30, 5))
        self.mode_label = tk.Label(self.timer_frame, text=self.mode.upper(), font=("Helvetica", 14), bg="#B78C6E", fg="#2E2925")
        self.mode_label.pack()

        image_path = Path(__file__).resolve().parent / "Vinyl.PNG"
        vinyl = Image.open(image_path).resize((250, 250))
        self.vinyl_image = ImageTk.PhotoImage(vinyl)
        tk.Label(self.timer_frame, image=self.vinyl_image, bg="#B78C6E").pack(pady=15)

        self.timer_var = tk.StringVar(value="00:00")
        tk.Label(self.timer_frame, textvariable=self.timer_var, font=("Helvetica", 48), bg="#B78C6E", fg="#2E2925").pack()

        self.session_var = tk.StringVar(value=f"Session {self.sessions_completed} of {self.session_target.get()}")
        tk.Label(self.timer_frame, textvariable=self.session_var, font=("Helvetica", 12), bg="#B78C6E", fg="#2E2925").pack(pady=5)

        button_frame = tk.Frame(self.timer_frame, bg="#B78C6E")
        button_frame.pack(pady=15)
        for text, command in (("PAUSE", self.pause), ("RESET", self.reset)):
            tk.Button(button_frame, text=text, command=command, font=("Helvetica", 12, "bold"), padx=25, pady=10).pack(side="left", padx=5)

    def start_from_setup(self):
        try:
            sessions = int(self.session_target.get())
            work = int(self.work_seconds.get())
            break_time = int(self.break_seconds.get())
        except (tk.TclError, ValueError):
            self.error_var.set("Please enter numbers only in every field.")
            return

        if sessions < 1 or work < 1 or break_time < 1:
            self.error_var.set("Each value must be at least 1.")
            return

        self.session_target.set(sessions)
        self.work_seconds.set(work)
        self.break_seconds.set(break_time)
        self.error_var.set("")
        self.setup_frame.pack_forget()
        self._build_timer_screen()
        self._reset_state()
        self.start()

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
        self.session_var.set(f"Session {self.sessions_completed} of {self.session_target.get()}")

    def _switch_mode(self):
        if self.mode == "Work":
            self.sessions_completed += 1
            if self.sessions_completed >= self.session_target.get():
                self.is_running = False
                self.after_id = None
                self._update_display()
                return
            self.mode = "Break"
            self.remaining = int(self.break_seconds.get())
        else:
            self.mode = "Work"
            self.remaining = int(self.work_seconds.get())

        self._update_display()


    def _tick(self):
        if not self.is_running:
            return

        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
            self.after_id = self.after(1000, self._tick)
        else:
            self._switch_mode()
            self.after_id = self.after(1000, self._tick)

    def start(self):
        if self.is_running:
            return

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
        self._cancel_timer()
        self.is_running = False
        if self.timer_frame is not None:
            self.timer_frame.destroy()
            self.timer_frame = None
        self._build_setup_screen()


if __name__ == "__main__":
    app = PomodoroApp()
    app.mainloop()
