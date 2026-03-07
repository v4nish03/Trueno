# ▶️ Cómo Iniciar el Sistema - Trueno Motors Uyuni

## ⚡ Inicio Rápido (Uso Diario)

### En Windows:
Haz **doble clic** en el archivo:
```
iniciar_windows.bat
```
Se abrirá una ventana negra (no la cierres) y el navegador automáticamente.

### En Linux:
Abre una terminal en la carpeta `Trueno/` y ejecuta:
```bash
./iniciar_linux.sh
```
O bien haz doble clic en `iniciar_linux.sh` desde el explorador de archivos.

> ⚠️ **No cierres la ventana negra/terminal.** Si la cierras, el sistema se apaga.

---

## 🌐 Acceso desde Otros Dispositivos en la Misma Red
Una vez iniciado el sistema, cualquier dispositivo (celular, tablet, otra PC) en la misma red WiFi puede acceder escribiendo en el navegador:
```
http://<IP-DE-LA-PC-SERVER>:8000
```
Ejemplo: `http://192.168.1.10:8000`

Para encontrar tu IP en Windows: abre CMD y escribe `ipconfig`.
Para encontrar tu IP en Linux: abre terminal y escribe `ip a`.

---

## 🔧 Primera Vez / Nueva Instalación

### Requisitos:
| Programa | Versión | Link |
|---|---|---|
| Python | 3.10 o superior | python.org (**marcar "Add to PATH"**) |
| PostgreSQL | 15 o superior | postgresql.org |

### Pasos:
1. **Copia** la carpeta `Trueno/` al equipo (sin `.venv` ni `node_modules`).
2. **Crea la base de datos** llamada `trueno` en PostgreSQL.
3. **Configura el archivo** `Back/.env` con tu base de datos y Telegram.
4. Abre el CMD/Terminal en la carpeta `Back/` y ejecuta:
   ```
   python -m venv .venv
   .venv\Scripts\activate         (Windows)
   source .venv/bin/activate      (Linux)
   pip install -r requirements.txt
   ```
5. **¡Listo!** Ya puedes ejecutar el sistema con el script de inicio.

---

## 🛑 Cómo Apagar el Sistema
Simplemente cierra la ventana negra o presiona `Ctrl+C` en la terminal.

---

## ❓ El sistema no abre / Error de Base de Datos
1. Verifica que el servicio **PostgreSQL** esté corriendo en tu computadora.
2. Verifica que el archivo `Back/.env` tenga la contraseña correcta.
3. Asegúrate de haber creado la base de datos `trueno` en pgAdmin.
