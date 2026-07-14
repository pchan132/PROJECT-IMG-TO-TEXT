"""Debug script to inspect PaddleOCR v3 output structure."""
import os
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["PADDLE_PDX_ENABLE_MKLDNN_BYDEFAULT"] = "0"

from paddleocr import PaddleOCR
import json

ocr = PaddleOCR(lang="th", use_angle_cls=True, device="cpu")

# Use the same test image
img = r"E:\meter-pea\new\LINE_ALBUM_ติดตั้งใหม่2569_260715_1.jpg"

print("=== Testing .predict() ===")
result = ocr.predict(input=img)

print(f"\nresult type: {type(result)}")
for i, res in enumerate(result):
    print(f"\n--- result[{i}] ---")
    print(f"  type: {type(res)}")
    # List all attributes
    attrs = [a for a in dir(res) if not a.startswith('_')]
    print(f"  attributes: {attrs}")
    # Try to print common attribute values
    for attr in attrs:
        try:
            val = getattr(res, attr)
            if not callable(val):
                val_str = str(val)[:200]
                print(f"  {attr} = {val_str}")
        except Exception as e:
            print(f"  {attr} = ERROR: {e}")
    # Try dict conversion
    if hasattr(res, '__dict__'):
        print(f"\n  __dict__ keys: {list(res.__dict__.keys())}")
    if hasattr(res, 'keys'):
        print(f"\n  dict keys: {list(res.keys())}")
    # Try indexing
    if hasattr(res, '__getitem__'):
        try:
            print(f"\n  res[0] = {str(res[0])[:200]}")
        except Exception:
            pass
