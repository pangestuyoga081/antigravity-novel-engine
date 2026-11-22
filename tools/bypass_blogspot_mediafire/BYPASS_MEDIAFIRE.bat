@echo off
setlocal
echo ========================================================
echo   BYPASS BLOGSPOT / RUIDRIVE / RUISAFE TO MEDIAFIRE
echo ========================================================
echo.
set /p TARGET_URL="Masukkan URL Halaman Blogspot / Ruidrive: "

if "%TARGET_URL%"=="" (
    echo [ERROR] URL tidak boleh kosong!
    pause
    exit /b 1
)

python "%~dp0extractor.py" "%TARGET_URL%"
echo.
pause
