# 💻 Guía de Instalación y Arranque (Windows y Linux)

Este archivo consolida cómo instalar el sistema `Trueno Motors` vacío y arrancar sin fallos por primera vez.

## 1. Requisitos Previos (Para cualquier Computadora/Servidor)
Debes tener pre-instalado estos pilares de software:
- **Python 3.10 o superior** (Lenguaje de servidor Backend).
- **Node.js 18 o superior y npm** (Para compilar las interfaces gráficas modernas Visuales).
- **PostgreSQL 14 o superior** (Motor de gestión de Bases de Datos súper robusto).

## 2. Instalación Paso a Paso (La primera vez)

### 📂 2.1: Prepara la Base de Datos
Dentro del programa "pgAdmin 4" o la terminal del postgres (`psql`), corre el siguiente código (si creaste el servidor db bajo contraseña y usuario general `postgres`):
```sql
CREATE DATABASE trueno;
```
*(No requieres inyectar tablas, el sistema creará cada tabla base automáticamente la primera vez que se ejecute).*

### 🔌 2.2: Configurar y Arrancar el Backend (Python)
Entra en tu terminal a la carpeta `/Back` del proyecto.

**En WINDOWS:**
```cmd
cd Back
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**En LINUX:**
```bash
cd Back
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**🚨 Paso Clave (El archivo de claves):**
Debes crear un archivo de texto base nombrado exactamente **`.env`** en la carpeta `Back`. Revisa en detalle la otra guía `CONFIGURACION_ENV.md` para llenarlo con seguridad de Telegram y la contraseña de base de datos.

### 🎨 2.3: Compilando el Motor Visual Frontend (Vue JS)
El frontend debe transformarse en una página web sólida. El proyecto ya está codificado, pero hay que construirlo:

**En WINDOWS y LINUX:**
Abre una terminal nueva e ingresa a tu directorio `Front`.
```bash
cd Front
npm install
npm run build
```
*(Eso es todo en el front. Si falla intenta limpiar caché con `npm cache clean --force`).* Esto creará un directorio llamado `dist/` en la carpeta Front.

---

## 3. ¿Cómo iniciar el sistema de Lunes a Domingo? (Las próximas veces)

Una vez lo instales, ya no requieres hacer nada del Paso 2, puedes encender ambos de golpe usando un simple archivo local como acceso directo de toda la vida:

### ▶️ En WINDOWS (Doble Clic Mágico)
Vete a la carpeta principal / raíz del programa.
1. Haz **doble clic** (o ejecuta en consola si eres admin) al archivo llamado `iniciar_windows.bat`
2. El sistema cobrará vida, montará estáticamente la interfaz de usuario con tu Base de Datos en un solo proceso.
3. Se abrirá automáticamente Chrome/Edge de acuerdo con tu navegador prefijado. No cierres la pantallita oscura "CMD".

### ▶️ En LINUX (Scripts BASH)
1. Abre tu terminal principal en la carpeta raíz.
2. Ejecuta dando permisos al dueño si se requiere y luego abres:
```bash
chmod +x iniciar_linux.sh
./iniciar_linux.sh
```

## 4. Direcciones Web (Punto de anclaje)
Ya en red, desde cualquier computadora dentro de la oficina accedes vía internet LAN así:
- Computadora principal (Servidor): `http://localhost:8000`
- Otros dispositivos / Laptops / Tablets por WiFi local de tu local: `http://TU_IP_LOCAL:8000` (Ejemplo real: `http://192.168.1.13:8000`)
*(Nota: Para la IP local abre `ipconfig` en Windows CMD o `ip a` en linux para descubrir el valor ipv4 `192.168...`)*
