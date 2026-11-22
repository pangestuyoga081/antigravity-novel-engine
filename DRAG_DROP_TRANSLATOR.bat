@echo off
setlocal
chcp 65001 >nul

echo ======================================================================
echo           NOVEL TRANSLATOR (DIRECT, TO-THE-POINT, GAUL)
echo ======================================================================
echo.

set "TARGET=%~f1"

if defined TARGET goto :PROCESS

:ASK_PATH
echo Masukkan path file (.epub / .txt) atau drag ke sini:
set "TARGET="
set /p "TARGET="

if not defined TARGET (
    echo Tidak ada file yang dimasukkan.
    pause
    exit /b
)

:PROCESS
:: Buang tanda petik ganda
set "TARGET=%TARGET:"=%"

echo.
echo Memproses: "%TARGET%"
echo.

cd /d "%~dp0"
call npx tsx "%~dp0translate-novel-dragndrop.ts" "%TARGET%"

echo.
pause
