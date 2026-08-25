@echo off
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"

echo ============================================================
echo   UPDATED - easy_tdx Full Feature Launcher
echo ============================================================
echo.

where npm >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js/npm not found.
  echo Please install Node.js LTS, then run this file again.
  pause
  exit /b 1
)

rem Prefer Python 3.12/3.13 because easy_tdx scientific extras are safest there.
set "PY_CMD="
py -3.12 -c "import sys; print(sys.version)" >nul 2>nul
if not errorlevel 1 set "PY_CMD=py -3.12"
if not defined PY_CMD (
  py -3.13 -c "import sys; print(sys.version)" >nul 2>nul
  if not errorlevel 1 set "PY_CMD=py -3.13"
)
if not defined PY_CMD (
  where python >nul 2>nul
  if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.12 or 3.13.
    pause
    exit /b 1
  )
  set "PY_CMD=python"
)

echo [0/5] Runtime check...
%PY_CMD% -c "import sys; print('Python:', sys.version); print('Executable:', sys.executable)"
if errorlevel 1 goto :failed
call npm --version
if errorlevel 1 goto :failed

echo.
echo [1/5] Installing Web UI dependencies...
pushd web-ui
call npm ci
if errorlevel 1 (
  popd
  goto :failed
)

echo.
echo [2/5] Building latest UPDATED Web UI...
call npm run build
if errorlevel 1 (
  popd
  goto :failed
)
popd

if not exist "web-ui\dist\index.html" (
  echo [ERROR] web-ui\dist\index.html was not generated.
  goto :failed
)

echo.
echo [3/5] Installing/updating easy_tdx core + Web dependencies...
%PY_CMD% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :failed
%PY_CMD% -m pip install -e ".[web]"
if errorlevel 1 goto :failed

echo.
echo [4/5] Installing optional scientific dependencies...
%PY_CMD% -m pip install -e ".[science]"
if errorlevel 1 (
  echo.
  echo [WARN] Scientific extras could not be installed with this Python version.
  echo        Core easy_tdx, Web UI, market data, indicators, ChanLun,
  echo        strategies, backtest, API and signal radar will still start.
  echo        For maximum compatibility install Python 3.12 or 3.13.
  echo.
)

echo.
echo [5/5] Starting easy_tdx full-feature server...
echo URL: http://127.0.0.1:8000/
echo API: http://127.0.0.1:8000/docs
echo Stop: press Ctrl+C in this window.
echo.
%PY_CMD% -m easy_tdx
exit /b %errorlevel%

:failed
echo.
echo [FAILED] Installation or build failed.
echo Copy the error above or send a screenshot to ChatGPT.
pause
exit /b 1
