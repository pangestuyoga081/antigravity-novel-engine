@echo off
chcp 65001 >nul
echo Menjalankan pemulihan 3 komponen sesi Antigravity...
python "%~dp0restore.py"
pause
