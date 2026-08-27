@echo off
set ROOT=%~dp0
set TCC=%ROOT%tcc\tcc\tcc.exe
if not exist "%TCC%" (
  echo Missing 32-bit TCC at %TCC%
  exit /b 1
)
cd /d "%ROOT%"
"%TCC%" -shared -o DINPUT8.dll dinput8.c dinput8.def -lgdi32 -luser32 -lkernel32
if errorlevel 1 exit /b 1
python "%ROOT%fix_export.py" "%ROOT%DINPUT8.dll"
if errorlevel 1 exit /b 1
copy /Y DINPUT8.dll "%ROOT%..\..\DINPUT8.dll"
echo installed DINPUT8.dll
