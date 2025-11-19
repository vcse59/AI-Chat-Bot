@echo off
REM GitHub Releases Creation Script
REM This script helps you create GitHub releases for ConvoAI

echo.
echo ========================================
echo   ConvoAI GitHub Releases Creation
echo ========================================
echo.

REM Check if GITHUB_TOKEN is set
if not defined GITHUB_TOKEN (
    echo ERROR: GITHUB_TOKEN environment variable not set!
    echo.
    echo To create releases via GitHub API:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)"
    echo 3. Name it: "ConvoAI Release Token"
    echo 4. Select scope: "repo" (Full control)
    echo 5. Generate and copy the token
    echo 6. Run: set GITHUB_TOKEN=your_token_here
    echo 7. Run this script again
    echo.
    echo OR use the Web Interface (easier):
    echo - Read GITHUB_RELEASES_GUIDE.md for instructions
    echo - Go to: https://github.com/vcse59/ConvoAI/releases/new
    echo.
    pause
    exit /b 1
)

echo GitHub Token found. Creating releases...
echo.

REM Run PowerShell script
powershell -ExecutionPolicy Bypass -File "create_releases.ps1"

echo.
echo ========================================
echo.
pause
