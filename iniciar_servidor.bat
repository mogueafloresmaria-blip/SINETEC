@echo off
chcp 65001 >nul
title Servidor SINETEC - Media Técnica SENA
echo ===================================================================
echo             SISTEMA SINETEC - SERVIDOR LOCAL Y MÓVIL
echo ===================================================================
echo.
echo  • Desde tu computadora:    http://localhost:8000
echo  • Desde tu celular (Wi-Fi): http://192.168.40.23:8000
echo.
echo Iniciando servidor en segundo plano...
start "" "venv\Scripts\pythonw.exe" manage.py runserver 0.0.0.0:8000
echo.
echo [LISTO] El servidor ya está corriendo. Puedes cerrar esta ventana.
echo ===================================================================
timeout /t 5
