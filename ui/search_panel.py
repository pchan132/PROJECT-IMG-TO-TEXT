import customtkinter as ctk


class SearchPanel(ctk.CTkFrame):
    def __init__(self, master, command):
        super().__init__(master, fg_color="transparent")
        self.query = ctk.StringVar()
        entry = ctk.CTkEntry(self, textvariable=self.query, placeholder_text="ค้นหาข้อความในทุกไฟล์...")
        entry.pack(side="left", fill="x", expand=True, padx=(0, 6)); entry.bind("<Return>", lambda _e: command())
        ctk.CTkButton(self, text="ค้นหา", width=76, command=command).pack(side="right")
