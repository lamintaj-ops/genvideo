@echo off
setlocal enabledelayedexpansion

echo 🚀 Aquaverse Video Generator - File Copy for Hugging Face
echo ========================================================
echo.

REM Check if destination directory is provided
if "%~1"=="" (
    echo Usage: copy_to_space.bat "path\to\huggingface\space\directory"
    echo.
    echo Example:
    echo copy_to_space.bat "C:\HF_Spaces\aquaverse-video-generator"
    echo.
    echo Steps:
    echo 1. Create and clone your Hugging Face Space first
    echo 2. Run: git clone https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
    echo 3. Then run this script with the Space directory path
    pause
    exit /b 1
)

set "DEST_DIR=%~1"
set "SOURCE_DIR=%CD%"

echo 📁 Source: %SOURCE_DIR%
echo 📁 Destination: %DEST_DIR%
echo.

REM Check if destination exists
if not exist "%DEST_DIR%" (
    echo ❌ Destination directory not found: %DEST_DIR%
    echo Please clone your Hugging Face Space first
    pause
    exit /b 1
)

echo 📋 Copying essential files...
echo.

REM Copy Python files
echo Copying Python files...
copy "*.py" "%DEST_DIR%\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Some Python files may not have been copied
) else (
    echo ✅ Python files copied
)

REM Copy requirements.txt
echo Copying requirements.txt...
copy "requirements.txt" "%DEST_DIR%\" >nul 2>&1
if errorlevel 1 (
    echo ❌ requirements.txt not copied
) else (
    echo ✅ requirements.txt copied
)

REM Copy README files
echo Copying README files...
copy "README*.md" "%DEST_DIR%\" >nul 2>&1
copy "DEPLOY*.md" "%DEST_DIR%\" >nul 2>&1
echo ✅ README files copied

REM Copy Dockerfile if exists
echo Copying Dockerfile...
copy "Dockerfile" "%DEST_DIR%\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Dockerfile not found (optional)
) else (
    echo ✅ Dockerfile copied
)

REM Copy CSV files
echo Copying CSV files...
copy "*.csv" "%DEST_DIR%\" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  No CSV files found
) else (
    echo ✅ CSV files copied
)

REM Copy templates directory
echo Copying templates directory...
if exist "templates" (
    xcopy "templates" "%DEST_DIR%\templates\" /E /I /Y >nul 2>&1
    if errorlevel 1 (
        echo ❌ Templates directory not copied
    ) else (
        echo ✅ Templates directory copied
    )
) else (
    echo ⚠️  Templates directory not found
)

REM Copy static directory
echo Copying static directory...
if exist "static" (
    xcopy "static" "%DEST_DIR%\static\" /E /I /Y >nul 2>&1
    if errorlevel 1 (
        echo ❌ Static directory not copied
    ) else (
        echo ✅ Static directory copied
    )
) else (
    echo ⚠️  Static directory not found
)

REM Copy asset directories
echo Copying asset directories...
if exist "assets" (
    xcopy "assets" "%DEST_DIR%\assets\" /E /I /Y >nul 2>&1
    echo ✅ Assets directory copied
)
if exist "bgm" (
    xcopy "bgm" "%DEST_DIR%\bgm\" /E /I /Y >nul 2>&1
    echo ✅ BGM directory copied
)
if exist "sfx" (
    xcopy "sfx" "%DEST_DIR%\sfx\" /E /I /Y >nul 2>&1
    echo ✅ SFX directory copied
)
if exist "lut" (
    xcopy "lut" "%DEST_DIR%\lut\" /E /I /Y >nul 2>&1
    echo ✅ LUT directory copied
)

echo.
echo 🎉 File copy completed!
echo.
echo Next steps:
echo 1. cd "%DEST_DIR%"
echo 2. git add .
echo 3. git commit -m "Deploy Aquaverse Video Generator"
echo 4. git push origin main
echo.
echo Your Hugging Face Space will rebuild automatically.
echo.
pause