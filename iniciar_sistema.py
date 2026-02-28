import os
import subprocess
import time
import webbrowser
import sys
import platform

base_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(base_dir, 'Back')

print("==================================================")
print("🚀 INICIANDO SISTEMA TRUENO MOTORS...")
print("==================================================")

# Determinar ejecutable de Python dentro del entorno virtual
if platform.system() == 'Windows':
    python_exe = os.path.join(backend_dir, '.venv', 'Scripts', 'python.exe')
else:
    python_exe = os.path.join(backend_dir, '.venv', 'bin', 'python')

if not os.path.exists(python_exe):
    print(f"❌ Error: No se encontró el entorno virtual en: {python_exe}")
    print("Asegúrate de que la instalación (npm install y source .venv/bin/activate) se realizara antes de exportar.")
    time.sleep(10)
    sys.exit(1)

# Comando para iniciar Uvicorn en Back/
comando = [python_exe, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

try:
    print("⏳ Encendiendo Base de Datos y Backend...")
    # Ejecutamos el servidor como proceso hijo
    # NOTA: si no te reconoce uvicorn como modulo, quizas necesite estar en requirements.txt, pero ya instalamos todo en ese entorno
    server_process = subprocess.Popen(comando, cwd=backend_dir)
    
    # Pausamos para asegurar que el server HTTP esta escuchando
    time.sleep(2)
    
    url = "http://localhost:8000/"
    print(f"🌐 ¡Sistema listo y en red local! Abriendo navegador en: {url}")
    webbrowser.open(url)
    
    print("\n----------------------------------------------------")
    print("✅ EL SERVIDOR ESTÁ FUNCIONANDO. NO CIERRES ESTA VENTANA.")
    print("   (Para apagar el sistema por completo presiona Ctrl+C)")
    print("----------------------------------------------------\n")
    
    # Mantener el proceso vivo
    server_process.wait()

except KeyboardInterrupt:
    print("\n🛑 Apagando el servidor Trueno Motors...")
    server_process.terminate()
    server_process.wait()
    print("👋 ¡Hasta pronto! Cerrando aplicación segura.")
except Exception as e:
    print(f"❌ Ocurrió un error inesperado al encender la app: {e}")
    time.sleep(10)
