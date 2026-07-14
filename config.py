from pathlib import Path

APP_NAME = "OCR Extractor"
ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
HISTORY_FILE = OUTPUT_DIR / "history.json"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}
DEFAULT_WORKERS = max(1, __import__("os").cpu_count() or 2)
