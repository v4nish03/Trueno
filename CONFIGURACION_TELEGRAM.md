# Configuración de Telegram para Trueno Motors

## 📱 Configuración del Sistema de Alertas y Backups por Telegram

Este documento explica cómo configurar el sistema de notificaciones por Telegram para enviar alertas y backups del sistema Trueno Motors.

## 🔧 Pasos de Configuración

### 1. Crear un Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando `/newbot`
3. Sigue las instrucciones:
   - Nombre del bot: `Trueno Motors Bot`
   - Username: `trueno_motors_bot` (o lo que prefieras)
4. **¡Importante!** Guarda el **TOKEN** que te proporciona BotFather. Se ve así:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Obtener tus Números de Telegram

Para obtener tu ID de usuario de Telegram:

1. Busca **@userinfobot** en Telegram
2. Envía cualquier mensaje
3. El bot te responderá con tu ID numérico
4. Repite este proceso para cada número que quieras configurar

### 3. Configurar en el Sistema

#### Método A: Usando la API (Recomendado)

1. Inicia el sistema Trueno Motors
2. Abre tu navegador en `http://localhost:8000/docs`
3. Busca la sección **Configuración**
4. Usa el endpoint `POST /configuracion/inicializar-telegram`

Esto creará las configuraciones básicas que necesitas modificar.

#### Método B: Configuración Manual

Usa estos endpoints para configurar cada valor:

```bash
# Token del bot
curl -X PUT "http://localhost:8000/configuracion/telegram_bot_token" \
  -H "Content-Type: application/json" \
  -d '{"valor": "TU_TOKEN_AQUI"}'

# Números para alertas (hasta 2 números, separados por coma)
curl -X PUT "http://localhost:8000/configuracion/telegram_alertas_numeros" \
  -H "Content-Type: application/json" \
  -d '{"valor": "123456789,987654321"}'

# Número para backups (solo 1 número)
curl -X PUT "http://localhost:8000/configuracion/telegram_backup_numero" \
  -H "Content-Type: application/json" \
  -d '{"valor": "123456789"}'

# Habilitar el sistema
curl -X PUT "http://localhost:8000/configuracion/telegram_habilitado" \
  -H "Content-Type: application/json" \
  -d '{"valor": "true"}'
```

## 📋 Configuraciones Disponibles

| Configuración | Descripción | Formato | Ejemplo |
|---------------|-------------|----------|---------|
| `telegram_bot_token` | Token del bot de Telegram | String | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |
| `telegram_alertas_numeros` | Números para alertas (hasta 2) | Números separados por coma | `123456789,987654321` |
| `telegram_backup_numero` | Número para backups (solo 1) | Número simple | `123456789` |
| `telegram_habilitado` | Activar/desactivar sistema | `true`/`false` | `true` |

## 🚨 Cómo Funciona el Sistema

### Alertas
- **Destinatarios**: Hasta 2 números configurados
- **Contenido**: 
  - Productos con stock bajo
  - Ventas sin stock detectadas
  - Alertas detalladas de ventas con problemas
- **Frecuencia**: Inmediata cuando ocurren eventos

### Backups
- **Destinatario**: Solo 1 número configurado
- **Contenido**: 
  - Archivo de base de datos SQLite
  - Estadísticas del sistema
  - Resumen de productos y ventas
- **Frecuencia**: Diaria (debe configurarse con un scheduler externo)

## 🧪 Verificar Configuración

Usa este endpoint para verificar que todo funciona:

```bash
curl -X GET "http://localhost:8000/configuracion/telegram_verificar"
```

O usa la interfaz web en `http://localhost:8000/docs` con el endpoint:
`GET /configuracion/telegram_verificar`

## 🔍 Solución de Problemas

### No recibo mensajes
1. Verifica que el token sea correcto
2. Confirma que el bot está iniciado
3. Revisa que `telegram_habilitado` sea `true`
4. Verifica los IDs de usuario

### Error "Token inválido"
1. Obtén un nuevo token de @BotFather
2. Asegúrate de copiar el token completo
3. No compartas tu token con nadie

### No puedo encontrar mi ID de usuario
1. Usa @userinfobot como se explicó arriba
2. O envía un mensaje a tu bot y revisa los logs del servidor

## 📝 Ejemplo Completo

```json
{
  "telegram_bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "telegram_alertas_numeros": "123456789,987654321",
  "telegram_backup_numero": "123456789",
  "telegram_habilitado": "true"
}
```

## ⚠️ Notas de Seguridad

- **Nunca compartas tu token de bot**
- **Solo agrega números de confianza**
- **Revisa periódicamente quién tiene acceso**
- **Considera deshabilitar si no usas el sistema**

## 📞 Soporte

Si tienes problemas:

1. Revisa este documento
2. Usa el endpoint de verificación
3. Revisa los logs del sistema
4. Contacta al administrador del sistema

---

**Última actualización**: 2026-02-28  
**Versión**: 1.0.0
