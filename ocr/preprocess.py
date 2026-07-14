import cv2
import numpy as np


def prepare_image(path: str) -> np.ndarray:
    """Normalize a source image while retaining useful detail for low-quality scans."""
    image = cv2.imread(path)
    if image is None:
        raise ValueError("Unable to read image")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if min(gray.shape[:2]) < 900:
        image = cv2.resize(image, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    return image
