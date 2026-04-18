@echo off
setlocal

cd /d "%~dp0\.."

if not exist ".venv\Scripts\activate.bat" (
  echo [ERROR] No existe .venv\Scripts\activate.bat
  echo Ejecuta primero: python -m venv .venv ^&^& .venv\Scripts\activate ^&^& pip install -r requirements.txt
  pause
  exit /b 1
)

call ".venv\Scripts\activate.bat"

set "PLC_HOST=192.168.10.77"
set "PLC_RACK=0"
set "PLC_SLOT=1"
set "BACKEND_URL=http://100.99.95.109:42110/plant-api"
set "PLC_MAPPING_PATH=plc_poller/mapping.example.json"
set "PLC_POLL_INTERVAL_SECONDS=1"

echo ===============================================
echo Prosil PLC Poller -> VPS
echo PLC_HOST=%PLC_HOST%
echo BACKEND_URL=%BACKEND_URL%
echo ===============================================

python -m plc_poller.main

endlocal
