import os
import sys
import platform

def generar_linux():
    # Obtener el path absoluto actual (donde viva Trueno)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    desktop_dir = os.path.join(os.path.expanduser('~'), 'Escritorio')
    if not os.path.exists(desktop_dir):
        desktop_dir = os.path.join(os.path.expanduser('~'), 'Desktop')
        
    desktop_file = os.path.join(desktop_dir, 'Trueno_Motors.desktop')
    
    contenido = f"""[Desktop Entry]
Version=1.0
Name=Trueno Motors
Comment=Sistema de Gestión POS
Exec="{current_dir}/iniciar_linux.sh"
Icon={current_dir}/Front/assets/img/logo.jpeg
Terminal=true
Type=Application
Categories=Office;
"""
    with open(desktop_file, 'w') as f:
        f.write(contenido)
    
    # Dar permisos de ejecución al shortcut (vital en linux)
    os.chmod(desktop_file, 0o755)
    print(f"✅ ¡Éxito! Acceso directo creado en: {desktop_file}")
    print("👉 NOTA: Si al hacerle doble clic Ubuntu/Mint te pregunta, dale a 'Permitir Lanzar' o 'Allow Launching'.")

def generar_windows():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    vbs_script = os.path.join(current_dir, "crear_shortcut_temporal.vbs")
    
    ico_path = os.path.join(current_dir, "trueno_icono.ico")
    bat_path = os.path.join(current_dir, "iniciar_windows.bat")
    
    vbs_content = f"""
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = oWS.SpecialFolders("Desktop") & "\\Trueno Motors.lnk"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{bat_path}"
oLink.WorkingDirectory = "{current_dir}"
oLink.IconLocation = "{ico_path}"
oLink.Save
"""
    with open(vbs_script, 'w') as f:
        f.write(vbs_content)
        
    print("⏳ Generando ícono de Windows...")
    os.system(f'cscript //nologo "{vbs_script}"')
    os.remove(vbs_script)
    print("✅ ¡Éxito! Acceso directo creado en tu Escritorio de Windows.")

if __name__ == "__main__":
    print("="*50)
    print("🚗 GENERADOR DE ACCESOS DIRECTOS - TRUENO MOTORS 🚗")
    print("="*50)
    if platform.system() == "Windows":
        generar_windows()
    else:
        generar_linux()
    
    print("\nYa puedes cerrar esta ventana.")
    input("Presiona ENTER para salir...")
