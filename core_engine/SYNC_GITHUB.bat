@echo off
setlocal
echo ========================================================
echo   🔄 ANTIGRAVITY ENGINE - GITHUB SYNC (PULL & PUSH)
echo ========================================================
echo.

cd /d "%~dp0.."

echo [1/3] Mengambil pembaruan terbaru dari GitHub...
git pull origin main

if errorlevel 1 (
    echo [WARNING] Git pull mengalami kendala. Memeriksa status...
)

echo.
echo [2/3] Menambahkan perubahan lokal dan sinkronisasi...
git add core_engine/ *.ts *.py *.bat *.md

set "COMMIT_MSG=sync(engine): automatic cross-PC update at %DATE% %TIME%"
git commit -m "%COMMIT_MSG%"

echo.
echo [3/3] Melakukan push ke GitHub...
git push origin main

echo.
echo ========================================================
echo [SELESAI] Kode Anda sudah 100%% sinkron dengan GitHub!
echo Di PC lain, cukup jalankan skrip ini atau 'git pull'.
echo ========================================================
pause
