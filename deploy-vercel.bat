@echo off
setlocal

REM Deploy backend to Vercel from project root in one command.
set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%backend" >nul

where vercel >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Vercel CLI not found. Install it with: npm install -g vercel
    popd >nul
    exit /b 1
)

vercel --prod %*
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
