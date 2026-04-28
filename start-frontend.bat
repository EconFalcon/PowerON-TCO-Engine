@echo off
echo Starting PowerOn TCO Calculator Frontend...
set PATH=C:\tools\nodejs\node-v22.14.0-win-x64;%PATH%
cd /d "%~dp0frontend"
npm run dev
pause
