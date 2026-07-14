from __future__ import annotations

import os
import threading
from pathlib import Path
from .preprocess import prepare_image

# Disable OneDNN/MKLDNN to avoid PaddlePaddle 3.3.x regression
os.environ.setdefault("PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT", "0")


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

            # Try configurations from newest API to oldest
            device = "gpu" if self.use_gpu else "cpu"
            configs = [
                # PaddleOCR v3.x: uses 'device', 'use_textline_orientation'
                dict(lang="th", use_textline_orientation=True, device=device),
                # PaddleOCR v3.x with deprecated use_angle_cls
                dict(lang="th", use_angle_cls=True, device=device),
                # PaddleOCR v2.8+: uses 'use_gpu' and 'show_log'
                dict(lang="th", use_angle_cls=True, use_gpu=self.use_gpu, show_log=False),
                # Minimal fallback
                dict(lang="th", use_angle_cls=True),
            ]
            for cfg in configs:
                try:
                    self._local.model = PaddleOCR(**cfg)
                    break
                except TypeError:
                    continue
            else:
                raise RuntimeError("Failed to initialize PaddleOCR with any known configuration")
        return self._local.model

    def read(self, path: str) -> dict:
        source = Path(path)
        image = prepare_image(str(source))
        model = self._model()

        lines = []

        # Try v2 API first (.ocr), then v3 API (.predict)
        try:
            result = model.ocr(image, cls=True)
            for page in result or []:
                for entry in page or []:
                    box, (text, confidence) = entry
                    lines.append({"text": text, "confidence": round(float(confidence), 4), "box": [[float(x), float(y)] for x, y in box]})
        except (TypeError, AttributeError):
            # PaddleOCR v3.x uses .predict() and returns dict-like OCRResult
            result = model.predict(input=image)
            for res in result:
                texts = res.get("rec_texts", []) if hasattr(res, "get") else []
                scores = res.get("rec_scores", []) if hasattr(res, "get") else []
                boxes = res.get("dt_polys", []) if hasattr(res, "get") else []
                for i, text in enumerate(texts):
                    conf = float(scores[i]) if i < len(scores) else 0.0
                    box = [[float(x), float(y)] for x, y in boxes[i]] if i < len(boxes) else []
                    lines.append({"text": text, "confidence": round(conf, 4), "box": box})

        return {"path": str(source), "name": source.name, "text": "\n".join(item["text"] for item in lines), "lines": lines}
