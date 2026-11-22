@echo off
setlocal
echo ========================================================
echo   RESTORE ANTIGRAVITY CONVERSATION CHAT KE PC INI
echo ========================================================
echo.

set "TARGET_DIR=%USERPROFILE%\.gemini\antigravity\brain\dfaefe40-f699-4276-8717-cb4f8030016c"
set "SOURCE_DIR=%~dp0antigravity_brain_backup\dfaefe40-f699-4276-8717-cb4f8030016c"

if not exist "%SOURCE_DIR%" (
    echo [ERROR] Folder backup tidak ditemukan di %SOURCE_DIR%
    pause
    exit /b 1
)

echo Menyalin riwayat percakapan dan brain ke:
echo %TARGET_DIR%
echo.

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

xcopy /E /I /Y /Q "%SOURCE_DIR%\*" "%TARGET_DIR%\"

echo.
echo ========================================================
echo [SUKSES] Riwayat percakapan berhasil dipulihkan!
echo Silakan buka aplikasi Antigravity di PC ini, dan chat
echo ini akan langsung muncul dan siap dilanjutkan.
echo ========================================================
pause
