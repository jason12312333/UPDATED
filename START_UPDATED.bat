@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo   UPDATED - easy_tdx Full Feature Launcher
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Please install Python 3.10 or newer.
  pause
  exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js/npm not found. Please install Node.js LTS.
  pause
  exit /b 1
)

echo [1/4] Installing/updating Python dependencies...
python -m pip install -e ".[web,science]"
if errorlevel 1 goto :failed

echo.
echo [2/4] Installing Web UI dependencies...
pushd web-ui
call npm ci
if errorlevel 1 (
  popd
  goto :failed
)

echo.
echo [3/4] Building latest UPDATED Web UI...
call npm run build
if errorlevel 1 (
  popd
  goto :failed
)
popd

echo.
echo [4/4] Starting easy_tdx full-feature server...
echo URL: http://127.0.0.1:8000/
echo API: http://127.0.0.1:8000/docs
echo.
python -m easy_tdx
exit /b %errorlevel%

:failed
echo.
echo [FAILED] Installation or build failed. Copy the error above to ChatGPT.
pause
exit /b 1
