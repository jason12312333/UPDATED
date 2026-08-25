@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title UPDATED - easy_tdx

echo ============================================================
echo   UPDATED - easy_tdx Full Feature Launcher
echo ============================================================
echo Project: %CD%
echo.

rem IMPORTANT: do not probe py -3.12 / py -3.13.
rem New Windows Python Manager may pop up a runtime-install prompt and close the launcher.
where python >nul 2>nul
if errorlevel 1 goto :no_python
set "PY_CMD=python"

where npm >nul 2>nul
if errorlevel 1 goto :no_node

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
%PY_CMD% -m pip install --upgrade pip setuptools wheel hatchling
if errorlevel 1 goto :failed
%PY_CMD% -m pip install -e ".[web]"
if errorlevel 1 goto :failed

echo.
echo [4/5] Installing optional scientific dependencies...
%PY_CMD% -m pip install -e ".[science]"
if errorlevel 1 (
  echo.
  echo [WARN] Optional scipy/science dependency could not be installed.
  echo        The server will still start with the core easy_tdx + Web features.
  echo.
)

echo.
echo [5/5] Starting easy_tdx full-feature server...
echo URL: http://127.0.0.1:8000/
echo API: http://127.0.0.1:8000/docs
echo Stop: press Ctrl+C in this window.
echo.
%PY_CMD% -m easy_tdx
set "SERVER_RC=%errorlevel%"
echo.
echo easy_tdx server stopped. Exit code: %SERVER_RC%
echo This window will stay open so the error can be read.
pause
exit /b %SERVER_RC%

:no_python
echo [ERROR] The command "python" was not found.
echo This launcher will NOT request Python 3.12 or any other runtime automatically.
echo Open CMD and run: python --version
echo Then send the result to ChatGPT.
pause
exit /b 1

:no_node
echo [ERROR] Node.js/npm was not found.
echo Open CMD and run: npm --version
echo Then send the result to ChatGPT.
pause
exit /b 1

:failed
echo.
echo ============================================================
echo [FAILED] UPDATED could not finish installation/build.
echo The window is intentionally kept open.
echo Send the last error lines to ChatGPT.
echo ============================================================
pause
exit /b 1
