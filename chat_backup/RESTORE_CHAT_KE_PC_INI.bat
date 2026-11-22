@echo off
chcp 65001 >nul
echo ====================================================================
echo 🚀 ANTIGRAVITY SESSION RESTORE (PULIHKAN SESI CHAT KE PC INI)
echo ====================================================================
echo.

set CONV_ID=dfaefe40-f699-4276-8717-cb4f8030016c
set TARGET_DIR=%USERPROFILE%\.gemini\antigravity\brain
set ZIP_FILE=%~dp0antigravity_chat_session.zip

if not exist "%ZIP_FILE%" (
    echo [ERROR] Berkas %ZIP_FILE% tidak ditemukan!
    pause
    exit /b 1
)

echo Menemukan paket arsip sesi chat: %ZIP_FILE%
echo Target direktori Antigravity: %TARGET_DIR%\%CONV_ID%
echo.

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

echo Sedang mengekstrak seluruh log, artefak, transcript, dan memori chat...
tar -xf "%ZIP_FILE%" -C "%TARGET_DIR%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ====================================================================
    echo ✅ SUKSES! Seluruh riwayat chat dan memori Antigravity telah pulih.
    echo 📌 Buka aplikasi Antigravity di PC ini, percakapan ini akan langsung
    echo    muncul dan dapat dilanjutkan seperti biasa.
    echo ====================================================================
) else (
    echo.
    echo [ERROR] Terjadi kesalahan saat ekstraksi.
)

echo.
pause
