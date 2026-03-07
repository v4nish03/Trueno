# 📖 Cómo Funciona el Sistema - Trueno Motors Uyuni

## ¿Qué es?
Trueno Motors es un sistema de gestión de inventario y ventas diseñado específicamente para la tienda Trueno Motors Uyuni. Permite controlar el stock de productos, registrar ventas, manejar un turno de caja, y recibir alertas automáticas por Telegram.

---

## 🏗️ Arquitectura General

```
[Navegador Web] ⟷ [Servidor Python/FastAPI] ⟷ [Base de Datos PostgreSQL]
                                    ⟷ [Telegram Bot (alertas y backups)]
```

El sistema tiene dos partes principales:
- **Backend (Python + FastAPI):** La "cabeza" del sistema. Contiene toda la lógica de negocio, valida los datos y los guarda en PostgreSQL.
- **Frontend (Vue.js):** La "cara" del sistema. Una página web que se carga en el navegador y se conecta al backend.

---

## 🖥️ Módulos Disponibles

### 1. Dashboard (`/dashboard`)
Vista general del negocio con KPIs en tiempo real:
- Total vendido hoy, en la última semana y en el último mes.
- Proporción de ventas en Efectivo vs QR.
- Productos más vendidos del mes.
- Estado del turno de caja (Abierta / Cerrada).
- **Desde aquí**: se abre y cierra el turno de caja.

### 2. Punto de Venta — POS (`/pos`)
La pantalla principal donde se registran las ventas.
- Función de búsqueda de productos por nombre o código.
- **Pestañas múltiples** para atender varios clientes a la vez.
- El contenido de cada carrito se **guarda automáticamente** en el navegador para sobrevivir a recargas o apagones.
- Al confirmar una venta se escoge el método de pago: **Efectivo** o **QR**.
- ⚠️ Solo funciona si hay un turno de caja abierto.

### 3. Productos (`/productos`)
Gestión del inventario:
- Crear, ver y desactivar productos.
- Cada producto tiene hasta 4 niveles de precio.
- Se pueden registrar **ajustes de stock** (ingreso o salida de mercadería).
- Se muestran alertas visuales si el stock está bajo o agotado.

### 4. Movimientos (`/movimientos`)
Historial de todos los movimientos de inventario:
- Cada venta, compra o ajuste de stock queda registrado.
- KPIs de movimientos del período.

### 5. Ventas (`/ventas`)
Historial completo de ventas:
- Filtros por fecha.
- Ver el detalle de cada venta (productos, total, método de pago, recibo).
- Opción de **anular** una venta (devuelve el stock al inventario).

---

## 🏧 Turno de Caja
El sistema implementa un control de turnos de caja:
1. **Abrir Caja** (desde Dashboard): Se ingresa el monto inicial en efectivo (el dinero de cambio en el cajón).
2. Cada venta se asocia al turno activo, registrando el método de pago.
3. **Cerrar Caja**: Muestra el resumen del turno (Efectivo Inicial + Ventas Efectivo = Efectivo Esperado en Cajón, más el total en QR).
4. **Al cerrar caja**, el sistema automáticamente hace un backup de la base de datos.

---

## 📲 Alertas y Backups por Telegram
El sistema puede enviarte mensajes automáticos a Telegram:

- **Alertas de Stock Bajo / Sin Stock**: Cuando un producto llega a su stock mínimo o se vende sin tener suficiente stock.
- **Backup Automático**: Al cerrar el turno de caja, se genera un respaldo completo de la base de datos en formato `.sql.gz`:
  - Se guarda una copia **local** en la carpeta `Back/Backups/`.
  - Se envía el archivo comprimido a Telegram.

### Configuración en `.env`:
```
TELEGRAM_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=id_alertas_1,id_alertas_2   # Reciben mensajes de texto
TELEGRAM_CHAT_ID_BACKUP=id_backup             # Recibe el archivo de backup
```

---

## 🗄️ Base de Datos
- **Motor**: PostgreSQL.
- **Tablas principales**: `productos`, `ventas`, `venta_productos`, `movimientos`, `turnos_caja`, `configuracion`, `recibos`.
- En instalaciones nuevas, las tablas se crean automáticamente al iniciar el servidor.
