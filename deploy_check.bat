@echo off
echo 🚀 Aquaverse Video Generator - Hugging Face Spaces Deploy
echo =========================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git is not installed or not in PATH
    echo Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

REM Check if huggingface-cli is installed
huggingface-cli --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Hugging Face CLI not found
    echo Installing huggingface_hub...
    pip install huggingface_hub
    echo.
    echo Please run 'huggingface-cli login' first
    echo Get your token from: https://huggingface.co/settings/tokens
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

echo 📁 Current directory: %CD%
echo.

echo 🔍 Checking project files...
if not exist "app.py" (
    echo ❌ app.py not found
    exit /b 1
)
if not exist "web_app.py" (
    echo ❌ web_app.py not found
    exit /b 1
)
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    exit /b 1
)
echo ✅ Project files found
echo.

echo 🎯 Ready to deploy to Hugging Face Spaces!
echo.
echo Next steps:
echo 1. Create a Space at https://huggingface.co/new-space
echo 2. Choose SDK: Gradio
echo 3. Note your Space URL
echo 4. Run: git remote add origin https://huggingface.co/spaces/YOUR_USERNAME/YOUR_SPACE_NAME
echo 5. Run: python deploy_hf.py
echo.

pause