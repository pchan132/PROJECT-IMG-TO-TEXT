import cv2
import numpy as np


def prepare_image(path: str) -> np.ndarray:
    """Normalize a source image while retaining useful detail for low-quality scans."""
    # cv2.imread fails on many Windows builds when a filename contains Thai
    # (or other non-ASCII) characters.  Reading bytes through NumPy and then
    # decoding lets OpenCV receive image data instead of a narrow file path.
    try:
        raw = np.fromfile(path, dtype=np.uint8)
    except OSError as exc:
        raise ValueError(f"Unable to open image: {exc}") from exc
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to read image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if min(gray.shape[:2]) < 900:
        image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return image
