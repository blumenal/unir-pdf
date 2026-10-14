@echo off
cd /d "%~dp0"
echo Gerando UnirPDF.exe...
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --onefile --windowed --name UnirPDF unir_pdf.py
echo.
echo Pronto. O executavel esta em: dist\UnirPDF.exe
pause
