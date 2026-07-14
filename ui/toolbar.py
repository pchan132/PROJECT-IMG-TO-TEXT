import customtkinter as ctk


class Toolbar(ctk.CTkFrame):
    def __init__(self, master, choose_files, choose_folder, remove_selected, start, pause, resume, stop):
        super().__init__(master, fg_color="transparent")
        actions = [
            ("เลือกไฟล์", choose_files), ("เลือกโฟลเดอร์", choose_folder),
            ("ลบรายการ", remove_selected), ("เริ่ม OCR", start),
            ("พัก", pause), ("ทำต่อ", resume), ("หยุด", stop),
        ]
        for text, command in actions:
            ctk.CTkButton(self, text=text, command=command, width=92).pack(side="left", padx=4, pady=4)
