from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from .queue_manager import QueueController


class BatchWorker:
    def __init__(self, engine, workers: int, on_result, on_progress, on_done):
        self.engine, self.workers = engine, workers
        self.on_result, self.on_progress, self.on_done = on_result, on_progress, on_done
        self.control = QueueController()

    def start(self, paths: list[str]):
        import threading
        threading.Thread(target=self._run, args=(paths,), daemon=True).start()

    def _run(self, paths):
        started, results, errors, completed = time.monotonic(), [], [], 0
        def process(path):
            if not self.control.wait(): return None
            return self.engine.read(path)
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(process, p): p for p in paths}
            for future in as_completed(futures):
                if self.control.cancelled.is_set(): break
                path = futures[future]; completed += 1
                try:
                    result = future.result()
                    if result: results.append(result); self.on_result(result)
                except Exception as exc: errors.append({"path": path, "error": str(exc)})
                elapsed = time.monotonic() - started
                eta = elapsed / completed * (len(paths) - completed) if completed else 0
                self.on_progress(completed, len(paths), eta)
        self.on_done(results, errors, time.monotonic() - started)
