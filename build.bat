@echo off
setlocal
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name OCRExtractor --collect-all paddleocr --collect-all paddle --add-data "output;output" main.py
echo.
echo Build complete: dist\OCRExtractor\OCRExtractor.exe
pause
