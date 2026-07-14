from __future__ import annotations

import threading
from pathlib import Path
from .preprocess import prepare_image


class OCREngine:
    """Lazy PaddleOCR wrapper. A separate model is created per worker thread."""
    _local = threading.local()

    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu

    def _model(self):
        if not hasattr(self._local, "model"):
            try:
                from paddleocr import PaddleOCR
            except ImportError as exc:
                raise RuntimeError("PaddleOCR is not installed. Run: pip install -r requirements.txt") from exc
            self._local.model = PaddleOCR(lang="th", use_angle_cls=True, use_gpu=self.use_gpu, show_log=False)
        return self._local.model

    def read(self, path: str) -> dict:
        source = Path(path)
        image = prepare_image(str(source))
        result = self._model().ocr(image, cls=True)
        lines = []
        for page in result or []:
            for entry in page or []:
                box, (text, confidence) = entry
                lines.append({"text": text, "confidence": round(float(confidence), 4), "box": [[float(x), float(y)] for x, y in box]})
        return {"path": str(source), "name": source.name, "text": "\n".join(item["text"] for item in lines), "lines": lines}
