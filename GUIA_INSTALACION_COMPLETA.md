# 🚀 Guía de Instalación Completa - Trueno Motors

## 📋 Requisitos Previos

### Para Todos los Sistemas:
- **Python 3.8+** (recomendado 3.11+)
- **Node.js 16+** (recomendado 18+)
- **npm** o **yarn**
- **Git**

### Para Linux:
- `python3-venv` (para entornos virtuales)
- `build-essential` (para compilaciones si es necesario)

### Para Windows:
- Python 3.8+ desde [python.org](https://python.org)
- Node.js desde [nodejs.org](https://nodejs.org)
- Git para Windows

---

## 🐧 Instalación en Linux

### 1. Clonar el Repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd Trueno
```

### 2. Instalar Dependencias del Sistema
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm git

# CentOS/RHEL/Fedora
sudo dnf install python3 python3-pip nodejs npm git
# o para versiones antiguas
sudo yum install python3 python3-pip nodejs npm git
```

### 3. Configurar Backend
```bash
cd Back

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias de Python
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
nano .env  # Editar con tus configuraciones
```

### 4. Configurar Frontend
```bash
cd ../Front

# Instalar dependencias de Node.js
npm install

# O si prefieres yarn
# yarn install
```

### 5. Iniciar el Sistema
```bash
# Volver a la raíz
cd ..

# Ejecutar script de inicio
chmod +x iniciar_linux.sh
./iniciar_linux.sh

# O iniciar manualmente:
cd Back
source .venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 6. Acceder al Sistema
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000 (si está compilado)

---

## 🪟 Instalación en Windows

### 1. Clonar el Repositorio
```cmd
git clone <URL_DEL_REPOSITORIO>
cd Trueno
```

### 2. Configurar Backend
```cmd
cd Back

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Instalar dependencias de Python
pip install -r requirements.txt

# Configurar variables de entorno
copy .env.example .env
notepad .env  # Editar con tus configuraciones
```

### 3. Configurar Frontend
```cmd
cd ..\Front

# Instalar dependencias de Node.js
npm install

# O si prefieres yarn
# yarn install
```

### 4. Iniciar el Sistema
```cmd
# Volver a la raíz
cd ..

# Ejecutar script de inicio
iniciar_windows.bat

# O iniciar manualmente:
cd Back
.venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 5. Acceder al Sistema
- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Frontend**: http://localhost:8000 (si está compilado)

---

## ⚙️ Configuración del Archivo .env

### Archivo: `Back/.env`

```env
# Base de Datos
DATABASE_URL=sqlite:///./trueno.db

# Telegram - Configuración del Bot
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_ALERTAS_NUMEROS=123456789,987654321
TELEGRAM_BACKUP_NUMERO=123456789
TELEGRAM_HABILITADO=false

# Impresora
IMPRESORA_TERMINO=TM-T20II

# Servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
LOG_LEVEL=INFO

# Seguridad
SECRET_KEY=tu_clave_secreta_aqui
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000
```

### 🔑 Cómo Obtener el Token de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía `/newbot`
3. Sigue las instrucciones
4. Copia el token que te proporciona
5. Obtén tus IDs de usuario con **@userinfobot**

---

## 🏃‍♂️ Modo Desarrollo

### Backend (Linux/Mac)
```bash
cd Back
source .venv/bin/activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Backend (Windows)
```cmd
cd Back
.venv\Scripts\activate
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal Separada)
```bash
cd Front
npm run dev
# o
npm run build && npm run preview
```

---

## 🏗️ Modo Producción

### 1. Compilar Frontend
```bash
cd Front
npm run build
```

### 2. Iniciar Backend
```bash
cd Back
source .venv/bin/activate  # Linux/Mac
# o .venv\Scripts\activate  # Windows

python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Configurar Proxy Inverso (Opcional)

#### Nginx (Linux)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 🧪 Verificación y Testing

### 1. Verificar API
```bash
curl http://localhost:8000/health
```

### 2. Verificar Documentación
Abre: http://localhost:8000/docs

### 3. Probar Telegram
```bash
curl -X POST http://localhost:8000/configuracion/inicializar-telegram
```

### 4. Probar Frontend
Abre: http://localhost:8000 en tu navegador

---

## 🔧 Solución de Problemas

### Python no encontrado
```bash
# Linux
sudo apt install python3 python3-pip python3-venv

# Windows
# Asegúrate de agregar Python al PATH durante la instalación
```

### npm no encontrado
```bash
# Linux
sudo apt install nodejs npm

# Windows
# Descarga e instala desde nodejs.org
```

### Error de permisos (Linux)
```bash
chmod +x iniciar_linux.sh
chmod +x .venv/bin/activate
```

### Error de puerto ocupado
```bash
# Matar proceso en el puerto
sudo lsof -ti:8000 | xargs kill -9  # Linux
netstat -ano | findstr :8000        # Windows
```

### Error de módulos faltantes
```bash
cd Back
source .venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Error de Node.js
```bash
cd Front
rm -rf node_modules package-lock.json
npm install
```

---

## 📱 Configuración de Telegram (Paso a Paso)

### 1. Crear el Bot
1. Abre Telegram
2. Busca **@BotFather**
3. Envía `/newbot`
4. Nombre: `Trueno Motors Bot`
5. Username: `trueno_motors_bot`
6. **Guarda el token**

### 2. Obtener IDs de Usuario
1. Busca **@userinfobot**
2. Envía cualquier mensaje
3. Copia tu ID numérico
4. Repite para cada número que necesites

### 3. Configurar en el Sistema
```bash
# Usar la API
curl -X PUT "http://localhost:8000/configuracion/telegram_bot_token" \
  -H "Content-Type: application/json" \
  -d '{"valor": "TU_TOKEN_AQUI"}'

# O editar el .env directamente
nano Back/.env
```

---

## 🖨️ Configuración de Impresora

### Verificar Impresoras Disponibles
```bash
# Linux
lpstat -p

# Windows
# Panel de Control > Dispositivos e Impresoras
```

### Configurar en el Sistema
```bash
curl -X PUT "http://localhost:8000/configuracion/impresora_termino" \
  -H "Content-Type: application/json" \
  -d '{"valor": "nombre-de-tu-impresora"}'
```

---

## 📊 Estructura del Sistema

```
Trueno/
├── Back/                    # Backend FastAPI
│   ├── .venv/              # Entorno virtual Python
│   ├── .env                # Variables de entorno
│   ├── main.py             # Servidor principal
│   ├── models/             # Modelos de datos
│   ├── routers/            # Endpoints API
│   ├── services/           # Lógica de negocio
│   └── requirements.txt    # Dependencias Python
├── Front/                  # Frontend Vue.js
│   ├── src/                # Código fuente
│   ├── assets/             # Imágenes y recursos
│   ├── dist/               # Build de producción
│   └── package.json        # Dependencias Node.js
├── Mobile/                 # App Flutter (futuro)
├── Docs/                   # Documentación
└── iniciar_*.sh/.bat       # Scripts de inicio
```

---

## 🆘 Soporte y Ayuda

### Verificar Estado del Sistema
```bash
# Health check
curl http://localhost:8000/health

# Verificar configuración
curl http://localhost:8000/configuracion/

# Verificar Telegram
curl http://localhost:8000/configuracion/telegram_verificar
```

### Logs del Sistema
```bash
# Logs de la aplicación
tail -f logs/app.log

# Logs del servidor
python -m uvicorn main:app --log-level debug
```

### Contacto
- Revisa la documentación en `CONFIGURACION_TELEGRAM.md`
- Usa los endpoints de la API para diagnóstico
- Revisa los logs del sistema para errores específicos

---

**Última actualización**: 2026-02-28  
**Versión**: 1.0.0  
**Compatible**: Linux, Windows, macOS
