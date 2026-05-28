@echo off
setlocal
set "_PY=%~dp0tools\python311_embed\python.exe"
if not exist "%_PY%" (
  echo Embedded Python not found: "%_PY%"
  exit /b 1
)
"%_PY%" %*
