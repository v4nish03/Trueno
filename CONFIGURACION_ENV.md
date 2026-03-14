# ⚙️ Módulo .ENV: Claves de Servidor y Notificación Telegram

El archivo de "Ambiente Oculto" o `.env` guarda tus credenciales secretas (BotTokens, Password bases de datos). Es esencial porque no puede subirse a Git ni filtrarse.
Si la guía dice que el Backend necesita un `.env`, te enseñaremos a ponerlo aquí de manera perfecta. 

En la ruta de tu proyecto `Trueno/Back`, crea un archivo de texto llamado, sin puntos previos ni txt, **`.env`** 

Pega estrictamente el siguiente formato pero alterando siempre tus claves reales:

```env
# ==========================================
# 🔌 CONEXIÓN A BASE DE DATOS (PostgreSQL)
# ==========================================
# Reemplaza 'jherkis18' por TU contraseña maestra real del postgres.
# Sintaxis final: postgresql://USUARIO:CONTRASEÑA@localhost/BASEDATOS
DATABASE_URL=postgresql://postgres:jherkis18@localhost/trueno

# ==========================================
# 🤖 BOT VIGÍA: TELEGRAM NOTIFICADOR Y BACKUPS
# ==========================================
# Determina si el Bot va a tener permiso para mandar mensajes por internet a los dueños o no (true/false)
TELEGRAM_HABILITADO=true

# 👉 EL TOKEN PRIVILEGIADO DE TU PROPIO BOT
# Créate uno hablandole al bot de Telegram "@BotFather" con el comando "/newbot".
# BotFather en un par de segundos te expelerá una API_KEY que tienes que meter acá.
TELEGRAM_TOKEN=TU_NUMERITO_SECRETO_DEL_BOTFATHER_AQUI:abcDEFghiXYZ123...

# 👉 CHAT_ID GLOBAL DEL DUEÑO (Notificaciones Alertas y Control Ventas)
# Para agarrar tu propio CHAT_ID numérico pídele a "@getmyid_bot" (también en Telegram) tu ID único.
# El sistema Trueno enviará mensajes a ese número previniendo caídas totales de inventario rojo a esa persona o grupo.
TELEGRAM_CHAT_ID=AQUI_TU_CHAT_ID_EJ_1234567

# 👉 CHAT_ID EXCLUSIVO PARA COPIAS "SQL" DE BACKUP DIARIO (Bóveda Segura)
# Recomendamos que este ID sea exactamente tu número o el chat de otra persona socia confiable.
# Al CERRAR la CAJA, él mandará un Zip de Backup aquí mismo.
TELEGRAM_CHAT_ID_BACKUP=PUEDE_SER_EL_MISMO_NÚMERO_TUYO_ID_EJ_1234567
```

---

## ⚡ Errores Clásicos que DEBEN EVITARSE en Telegram

1. **"Mi sistema marca error 200/400 al querer mandar un alerta por telegram, no me llegan notificaciones"**
   - Razón principal: Un *Bot* de telegram no puede mandarle mensajes a ninguna persona "por que de la nada se le dio la gana mandarle".
   - **SOLUCIÓN ESTRICTA:** Para que Trueno Motors se contacte contigo y te pase reportes SQL, *TÚ DEBES INICIAR UNA CONVERSACIÓN CON EL BOT QUE TÚ MISMO CREASTE EN BOTFATHER* dándole en Iniciar o `/start`. El bot guardará eso como permiso especial global, y desde esa fecha Trueno podrá spamearte advertencias tranquilamente.

2. **"No funciona la base de datos dice Password Validation"**
   - Asegurate que ninguna letra del campo `.env` `DATABASE_URL` tenga símbolos incompatibles de escape tipo espacios gigantes, URL codificación.
   - Si no quieres lidiar más problemas o dudas, apaga temporalmente a Telegram dándole `TELEGRAM_HABILITADO=false`. El sistema seguirá funcionando internamente pero no notificará.
