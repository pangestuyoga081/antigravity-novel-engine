@echo off
setlocal
chcp 65001 >nul

set SD_EXE="E:\novel yoga\sd_tool\sd-cli.exe"
set MODEL="E:\animagine-xl-4.0-Q8_0.gguf"
set OUT_DIR="E:\novel yoga\ilustrasi_metro"

if not exist %OUT_DIR% mkdir %OUT_DIR%

echo =======================================================
echo    GENERATOR ILUSTRASI METRO 2033 (Animagine XL 4.0)
echo    Akselerasi GPU: AMD Radeon RX 6600 XT (Vulkan)
echo =======================================================
echo.

set /p PROMPT="Masukkan Prompt Karakter/Adegan: "
if "%PROMPT%"=="" (
    set PROMPT=1boy, artyom, holding rifle, post-apocalyptic dark metro tunnel, campfire, dramatic shadows, masterpiece, best quality
)

set /p OUT_NAME="Nama file output (contoh: bab1_artyom): "
if "%OUT_NAME%"=="" (
    set OUT_NAME=ilustrasi_%random%
)

set FINAL_OUT=%OUT_DIR%\%OUT_NAME%.png

echo.
echo Sedang merender dengan GPU RX 6600 XT...
echo Tunggu sebentar...

%SD_EXE% -M img_gen -m %MODEL% -p "%PROMPT%, masterpiece, high quality, highly detailed" -o "%FINAL_OUT%" -W 896 -H 896 --steps 20 --cfg-scale 5 --sampling-method euler_a

echo.
if exist "%FINAL_OUT%" (
    echo =======================================================
    echo BERHASIL! Gambar tersimpan di:
    echo %FINAL_OUT%
    echo =======================================================
    start "" "%FINAL_OUT%"
) else (
    echo Gagal membuat gambar. Periksa error di atas.
)

pause
