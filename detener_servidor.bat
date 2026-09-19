@echo off
chcp 65001 >nul
title Detener Servidor SINETEC
echo ========================================================
echo        DETENIENDO SERVIDOR SINETEC (PUERTO 8000)
echo ========================================================
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    taskkill /f /pid %%a >nul 2>&1
)
taskkill /f /im pythonw.exe >nul 2>&1
echo [OK] El servidor SINETEC ha sido detenido.
echo.
pause
