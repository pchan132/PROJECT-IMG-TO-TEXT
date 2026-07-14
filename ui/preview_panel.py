from __future__ import annotations

import tkinter as tk
from PIL import Image, ImageTk
import customtkinter as ctk


class PreviewPanel(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.zoom, self.image, self.photo, self.lines = 1.0, None, None, []
        controls = ctk.CTkFrame(self, fg_color="transparent"); controls.pack(fill="x")
        ctk.CTkButton(controls, text="−", width=36, command=lambda: self.set_zoom(.8)).pack(side="left", padx=3, pady=3)
        ctk.CTkButton(controls, text="+", width=36, command=lambda: self.set_zoom(1.25)).pack(side="left", padx=3, pady=3)
        self.canvas = tk.Canvas(self, bg="#202020", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<MouseWheel>", self._wheel); self.canvas.bind("<ButtonPress-1>", self._pan_start); self.canvas.bind("<B1-Motion>", self._pan)

    def show(self, path: str, lines: list[dict]):
        self.image, self.lines, self.zoom = Image.open(path).convert("RGB"), lines, 1.0
        self.redraw()

    def set_zoom(self, ratio):
        self.zoom = max(.1, min(5, self.zoom * ratio)); self.redraw()

    def _wheel(self, event): self.set_zoom(1.1 if event.delta > 0 else .9)
    def _pan_start(self, event): self.canvas.scan_mark(event.x, event.y)
    def _pan(self, event): self.canvas.scan_dragto(event.x, event.y, gain=1)

    def redraw(self, selected=None):
        if not self.image: return
        width, height = int(self.image.width * self.zoom), int(self.image.height * self.zoom)
        self.photo = ImageTk.PhotoImage(self.image.resize((width, height)))
        self.canvas.delete("all"); self.canvas.create_image(0, 0, image=self.photo, anchor="nw")
        for i, line in enumerate(self.lines):
            coords = [v * self.zoom for point in line["box"] for v in point]
            self.canvas.create_polygon(coords, outline="#00d084" if i != selected else "#ffbd2e", fill="", width=2)
        self.canvas.configure(scrollregion=(0, 0, width, height))

    def highlight(self, index): self.redraw(index)
