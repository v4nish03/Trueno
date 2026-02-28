# 🚀 Guía de Instalación y Exportación a Windows (Trueno Motors)

El sistema Trueno Motors está compuesto por un **Backend en Python (FastAPI)**, una base de datos **PostgreSQL**, y un **Frontend pre-compilado en Vue**.

Para instalar este sistema en la computadora Windows de la tienda, tienes dos caminos. Te recomiendo encarecidamente la **Opción 1** por ser inmensamente más estable y fácil de dar soporte a futuro.

---

## 🛠️ Requisitos Previos para el PC de la Tienda (Cualquier Opción)
Antes de copiar tus archivos, la computadora de la tienda NECESITA estos dos programas:
1. **Python 3.10 o superior**: 
   - Descargar desde `python.org`.
   - ⚠️ **CRÍTICO:** Durante la instalación, debes marcar la casilla que dice **"Add Python to PATH"** (Agregar Python al PATH).
2. **PostgreSQL 15 o superior**:
   - Descargar el instalador para Windows desde la página oficial.
   - Durante la instalación, te pedirá una contraseña para el superusuario `postgres`. Asegúrate de anotar esa contraseña.
   - Abre `pgAdmin` (que se instala junto con PostgreSQL) y crea una base de datos vacía llamada `trueno`.

---

## 📦 Opción 1: Exportación Estándar (¡Recomendada! ✅)
Convertir servidores web a formato `.exe` suele generar problemas de falsos positivos con los antivirus (Windows Defender) y pérdida de archivos estáticos. Lo más seguro en la industria es llevar la carpeta tal cual.

### Pasos en tu PC actual (Linux):
1. Asegúrate de tener las librerías actualizadas en un archivo de texto. Entra a la carpeta `Back` y ejecuta: 
   `pip freeze > requirements.txt` (Ya lo hicimos).
2. Agarra la carpeta completa `Trueno` (excepto las carpetas ocultas pesadas como `Back/.venv` o `Front/node_modules`) y envíala a un pendrive o súbela a la nube en un `.zip`.

### Pasos en el PC de la tienda (Windows):
1. Pega la carpeta `Trueno` en el disco local `C:\` o en Documentos.
2. Abre la terminal de Windows (`cmd`) en la carpeta `Trueno\Back` y ejecuta estos comandos para crear el entorno e instalar dependencias:
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Edita el archivo `.env` que está dentro de la carpeta `Back` para que coincida con la contraseña del PostgreSQL que instalaste en ese Windows:
   `DATABASE_URL=postgresql://postgres:LA_CONTRASEÑA_QUE_PUSISTE@localhost:5432/trueno`
4. **¡Listo!** Dale clic derecho al archivo `iniciar_windows.bat`, selecciona **"Crear acceso directo"** y arrástralo al Escritorio.
   - La primera vez que lo abran, FastAPI creará automáticamente todas las tablas vacías en la base de datos de la tienda. El dueño solo tendrá que hacer doble clic en el Escritorio todos los días.

---

## ⚙️ Opción 2: Compilación a un archivo `.exe` (PyInstaller)
Si estrictamente quieres hacer un solo archivo ejecutable `.exe` que oculte el código fuente de Python, debes usar **PyInstaller**. Ten en cuenta que seguirás necesitando instalar PostgreSQL en la máquina destino.

### Pasos (Preferiblemente hazlo desde una PC con Windows para compilar para Windows):
1. Instala PyInstaller en tu entorno virtual:
   `pip install pyinstaller`
2. Ve a la carpeta `Back` y compila el `main.py` indicándole que incluya la carpeta pre-compilada del Frontend (`Front/dist`) para que el EXE sepa dónde está la web:
   ```cmd
   pyinstaller --name "TruenoMotorsServer" --noconfirm --onedir --console --add-data "../Front/dist;Front/dist" main.py
   ```
   *(Nota: en Linux el separador de `add-data` usa dos puntos `:`, en Windows punto y coma `;`)*
3. **PyInstaller** generará una carpeta `dist/TruenoMotorsServer`. Adentro habrá un montón de archivos `.dll` y un gigante `TruenoMotorsServer.exe`.
4. Lleva toda esa carpeta a la máquina destino en Windows. 
5. Asegúrate de poner tu archivo `.env` junto al `.exe` y ejecuta el programa. Mostrará una consola negra corriendo tu servidor, y el cliente podrá entrar a `http://localhost:8000` desde Chrome.

---

### Mantenimiento y Backups
No olvides que en el Windows del cliente **debes tener instalada la herramienta de entorno `pg_dump`** en las Variables de Entorno de Windows para que la característica de los Backups a Telegram que diseñamos funcione correctamente. Normalmente el instalador de PostgreSQL la incluye en `C:\Program Files\PostgreSQL\15\bin\`.
