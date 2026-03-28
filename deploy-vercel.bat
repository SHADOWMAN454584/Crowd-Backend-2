@echo off
setlocal

REM Deploy backend to Vercel from project root in one command.
set "ROOT_DIR=%~dp0"
pushd "%ROOT_DIR%backend" >nul

where vercel >nul 2>nul
if errorlevel 1 (
    where npx >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] Vercel CLI not found and npx is unavailable.
        echo [ERROR] Install Node.js and run: npm install -g vercel
        popd >nul
        exit /b 1
    )

    echo [INFO] Global Vercel CLI not found. Using npx vercel...
    npx --yes vercel --prod --yes %*
    set "EXIT_CODE=%ERRORLEVEL%"

    popd >nul
    exit /b %EXIT_CODE%
)

vercel --prod --yes %*
set "EXIT_CODE=%ERRORLEVEL%"

popd >nul
exit /b %EXIT_CODE%
