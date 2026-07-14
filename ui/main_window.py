from __future__ import annotations

import json
import os
import queue
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
import customtkinter as ctk

from config import APP_NAME, DEFAULT_WORKERS, HISTORY_FILE, OUTPUT_DIR, SUPPORTED_IMAGE_EXTENSIONS
from ocr.engine import OCREngine
from ocr.exporter import Exporter
from worker.batch_worker import BatchWorker
from .toolbar import Toolbar
from .progress_panel import ProgressPanel
from .preview_panel import PreviewPanel
from .search_panel import SearchPanel


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__(); ctk.set_appearance_mode("system")
        self.title(APP_NAME); self.geometry("1400x850"); self.minsize(1050, 650)
        self.paths, self.display_paths, self.results, self.worker, self.events = [], [], [], None, queue.Queue()
        self.exporter = Exporter(OUTPUT_DIR)
        self._build(); self.after(100, self._poll_events)
        self._enable_drag_drop()

    def _build(self):
        top = ctk.CTkFrame(self); top.pack(fill="x", padx=10, pady=(10, 0))
        Toolbar(top, self.choose_files, self.choose_folder, self.remove_selected, self.start, self.pause, self.resume, self.stop).pack(side="left")
        ctk.CTkOptionMenu(top, values=["System", "Light", "Dark"], command=lambda v: ctk.set_appearance_mode(v.lower())).pack(side="right", padx=5)
        self.workers = ctk.CTkOptionMenu(top, values=[str(x) for x in range(1, DEFAULT_WORKERS + 1)]); self.workers.set(str(DEFAULT_WORKERS)); self.workers.pack(side="right", padx=5)
        ctk.CTkLabel(top, text="Threads").pack(side="right")
        self.search_panel = SearchPanel(self, self.search)
        self.search_panel.pack(fill="x", padx=14, pady=7)
        body = ctk.CTkFrame(self); body.pack(fill="both", expand=True, padx=10, pady=3); body.grid_columnconfigure(1, weight=1); body.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(body, width=300); left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ctk.CTkLabel(left, text="ไฟล์ที่เลือก / ผลค้นหา").pack(pady=(8, 2))
        self.files = tk.Listbox(left, activestyle="none"); self.files.pack(fill="both", expand=True, padx=8, pady=8); self.files.bind("<<ListboxSelect>>", self.select_file)
        self.preview = PreviewPanel(body); self.preview.grid(row=0, column=1, sticky="nsew", padx=6)
        right = ctk.CTkFrame(body, width=360); right.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        ctk.CTkLabel(right, text="ข้อความที่ตรวจพบ").pack(pady=(8, 2))
        self.text = tk.Text(right, wrap="word", height=12); self.text.pack(fill="both", expand=True, padx=8, pady=6)
        self.line_list = tk.Listbox(right, height=12); self.line_list.pack(fill="both", expand=True, padx=8, pady=6); self.line_list.bind("<<ListboxSelect>>", self.highlight_line)
        exports = ctk.CTkFrame(right, fg_color="transparent"); exports.pack(fill="x", padx=8, pady=(0, 8))
        for fmt in ("txt", "docx", "xlsx", "csv", "json", "pdf"):
            ctk.CTkButton(exports, text=fmt.upper(), width=52, command=lambda f=fmt: self.export(f)).pack(side="left", padx=2)
        self.progress = ProgressPanel(self); self.progress.pack(fill="x", padx=10, pady=(3, 10))
        self.status = ctk.CTkLabel(self, text="Output: " + str(OUTPUT_DIR)); self.status.pack(anchor="w", padx=15, pady=(0, 8))

    def _add_paths(self, paths):
        added = [str(Path(p)) for p in paths if Path(p).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS and str(Path(p)) not in self.paths]
        self.paths.extend(added); self.display_paths = self.paths.copy(); self.files.delete(0, tk.END)
        for path in self.display_paths: self.files.insert(tk.END, Path(path).name)
        self.status.configure(text=f"เลือกแล้ว {len(self.paths)} ไฟล์")

    def choose_files(self): self._add_paths(filedialog.askopenfilenames(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff *.webp")]))
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder: self._add_paths([p for p in Path(folder).rglob("*") if p.is_file()])

    def remove_selected(self):
        """Remove selected images from this OCR job without touching source files."""
        selected = list(self.files.curselection())
        if not selected:
            return messagebox.showinfo(APP_NAME, "กรุณาเลือกรายการที่ต้องการลบก่อน")
        removed = [self.display_paths[i] for i in selected]
        removed_set = set(removed)
        self.paths = [path for path in self.paths if path not in removed_set]
        self.display_paths = [path for path in self.display_paths if path not in removed_set]
        self.files.delete(0, tk.END)
        for path in self.display_paths:
            self.files.insert(tk.END, Path(path).name)
        self.status.configure(text=f"ลบ {len(removed)} รายการแล้ว | เหลือ {len(self.paths)} ไฟล์")

    def _enable_drag_drop(self):
        """Activate native file drops when the optional tkinterdnd2 package is available."""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            self.TkdndVersion = TkinterDnD._require(self)
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            self.status.configure(text="Drag & Drop ต้องติดตั้ง tkinterdnd2 (รวมอยู่ใน requirements.txt)")

    def _on_drop(self, event):
        dropped = self.tk.splitlist(event.data)
        paths = []
        for item in dropped:
            path = Path(item)
            paths.extend(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else paths.append(path)
        self._add_paths(paths)

    def start(self):
        if not self.paths: return messagebox.showwarning(APP_NAME, "กรุณาเลือกไฟล์หรือโฟลเดอร์ก่อน")
        self.results = []; self.status.configure(text="กำลังเริ่ม OCR (การโหลดโมเดลครั้งแรกอาจใช้เวลา)")
        engine = OCREngine(use_gpu=False)
        self.worker = BatchWorker(engine, int(self.workers.get()), lambda r: self.events.put(("result", r)), lambda *a: self.events.put(("progress", a)), lambda *a: self.events.put(("done", a)))
        self.worker.start(self.paths)
    def pause(self):
        if self.worker: self.worker.control.pause(); self.status.configure(text="พักงานอยู่")
    def resume(self):
        if self.worker: self.worker.control.resume(); self.status.configure(text="ประมวลผลต่อ")
    def stop(self):
        if self.worker: self.worker.control.stop(); self.status.configure(text="กำลังหยุดงาน")

    def _poll_events(self):
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "result": self.results.append(payload); self.exporter.per_image_text(payload)
                elif kind == "progress": self.progress.update(*payload)
                else: self.finish(*payload)
        except queue.Empty: pass
        self.after(100, self._poll_events)

    def finish(self, results, errors, elapsed):
        self._save_history(results, errors, elapsed)
        self.status.configure(text=f"เสร็จสิ้น: สำเร็จ {len(results)} | ไม่สำเร็จ {len(errors)} | {elapsed:.1f} วินาที | Output: {OUTPUT_DIR}")
        if errors: (OUTPUT_DIR / "errors.json").write_text(json.dumps(errors, ensure_ascii=False, indent=2), encoding="utf-8")
        if results: self.select_result(results[0])

    def _save_history(self, results, errors, elapsed):
        OUTPUT_DIR.mkdir(exist_ok=True); history = []
        if HISTORY_FILE.exists():
            try: history = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError: pass
        history.insert(0, {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "total": len(self.paths), "success": len(results), "failed": len(errors), "seconds": round(elapsed, 2)})
        HISTORY_FILE.write_text(json.dumps(history[:100], ensure_ascii=False, indent=2), encoding="utf-8")

    def select_file(self, _event=None):
        selection = self.files.curselection()
        if selection:
            path = self.display_paths[selection[0]] if selection[0] < len(self.display_paths) else None
            result = next((r for r in self.results if r["path"] == path), None)
            if result: self.select_result(result)
            elif path: self.preview.show(path, [])
    def select_result(self, result):
        self.preview.show(result["path"], result["lines"]); self.text.delete("1.0", tk.END); self.text.insert("1.0", result["text"])
        self.line_list.delete(0, tk.END)
        for line in result["lines"]: self.line_list.insert(tk.END, f"{line['text']}  ({line['confidence']:.0%})")
    def highlight_line(self, _event=None):
        selected = self.line_list.curselection()
        if selected: self.preview.highlight(selected[0])
    def search(self):
        # Search the completed OCR index and show only matching images.
        term = self.search_panel.query.get().strip().lower()
        matches = [r for r in self.results if term and term in r["text"].lower()]
        self.files.delete(0, tk.END)
        for result in matches: self.files.insert(tk.END, result["name"])
        self.display_paths = [r["path"] for r in matches]
        self.status.configure(text=f"พบ {len(matches)} ไฟล์สำหรับคำว่า “{term}”")
    def export(self, fmt):
        if not self.results: return messagebox.showwarning(APP_NAME, "ยังไม่มีผล OCR สำหรับส่งออก")
        try: path = self.exporter.export(self.results, fmt); self.status.configure(text=f"ส่งออกแล้ว: {path}")
        except Exception as exc: messagebox.showerror(APP_NAME, f"ส่งออก {fmt.upper()} ไม่สำเร็จ:\n{exc}")
