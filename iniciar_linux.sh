#!/bin/bash
# =========================================================
#  SELECTOR DE NAVEGADOR - TRUENO MOTORS
#  Descomenta y edita la línea de abajo para elegir el nav:
#  Opciones: chrome | chromium | firefox | edge | opera
# =========================================================
export NAVEGADOR=chrome

cd "$(dirname "$0")"
python3 iniciar_sistema.py
