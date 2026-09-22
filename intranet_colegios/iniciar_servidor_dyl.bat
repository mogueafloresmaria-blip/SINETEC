@echo off
title DYL SCHOOL - Servidor Local de Gestion Escolar
chcp 65001 >nul
cls
echo =====================================================================
echo           DYL SCHOOL - PLATAFORMA DE GESTIÓN ACADÉMICA
echo =====================================================================
echo.
echo Iniciando servidor PHP local en el puerto 8080...
echo Acceso: http://127.0.0.1:8080/index.php
echo.
echo Presione CTRL+C para detener el servidor.
echo =====================================================================
echo.

start "" "http://127.0.0.1:8080/index.php"
"C:\Users\julia\AppData\Local\Microsoft\WinGet\Packages\PHP.PHP.8.3_Microsoft.Winget.Source_8wekyb3d8bbwe\php.exe" -S 127.0.0.1:8080 -t "c:\SINETEC\SINETEC\intranet_colegios"
pause
