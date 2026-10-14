@echo off
setlocal
cd /d "%~dp0"
set "MATHPROJECT_ENV=production"
python scripts\run_production.py
endlocal
