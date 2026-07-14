import customtkinter as ctk


class ProgressPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.label = ctk.CTkLabel(self, text="พร้อมทำงาน")
        self.label.pack(anchor="w", padx=12, pady=(8, 0))
        self.bar = ctk.CTkProgressBar(self); self.bar.set(0); self.bar.pack(fill="x", padx=12, pady=8)

    def update(self, done, total, eta=0):
        self.bar.set(done / total if total else 0)
        self.label.configure(text=f"ประมวลผล {done}/{total}  |  ETA {int(eta // 60):02d}:{int(eta % 60):02d}")
