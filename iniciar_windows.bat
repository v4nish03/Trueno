@echo off
cd /d "%~dp0"

REM =========================================================
REM  SELECTOR DE NAVEGADOR - TRUENO MOTORS
REM  Cambia "default" por el navegador que prefieras:
REM  Opciones: default  chrome  firefox  edge  opera
REM =========================================================
SET NAVEGADOR=default

python iniciar_sistema.py
pause
