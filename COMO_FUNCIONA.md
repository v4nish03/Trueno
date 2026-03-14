# ⚡ Sistema Trueno Motors - ¿Cómo funciona?

Este documento explica las capacidades del sistema y cómo interactúan sus módulos principales. Trueno Motors es un **Punto de Venta (POS) y Gestor de Inventario** diseñado para ser rápido y evitar errores operativos.

## 1. 🏪 Punto de Venta (POS)
Es la pantalla principal para realizar facturación y ventas rápidas.
- **Búsqueda instantánea:** Puedes buscar productos por código (usando un lector láser) o por nombre.
- **Precios dinámicos:** Si un producto tiene varios precios (P1, P2, P3, P4), puedes elegir cuál aplicarle al cliente en ese instante mediante botones directos.
- **Alertas de Stock en tiempo real:** Muestra en colores (verde, amarillo, rojo) cuánto stock físico queda. Permite **vender aunque no haya stock** (el stock se volverá negativo), pero esto soltará una alarma interna al administrador.
- **Aperturas:** El POS requiere obligatoriamente que la caja esté "Abierta" para vender.
- **Pagos flexibles:** Soporta múltiples métodos de pago, como Efectivo y transferencias QR.
- **Tickets Automáticos:** Al confirmar cada venta genera inmediatamente un comprobante listo para imprimir (`impresión de ticket clásico`).

## 2. 📦 Productos e Inventario
Aquí das de alta tu mercadería y manejas tu stock central.
- **Gestión de Stock blindada:** Todo producto nuevo se crea con "0" inventario. Para sumarle stock a la tienda debes usar explícitamente el botón `+📦 Ingresar Stock` y declarar si es por "compra nueva", "devolución de cliente", u otro motivo.
- **Múltiples Precios Flexibles:** Maneja explícitamente hasta 4 escalas de precio por producto según cliente preferencial o mostrador.
- **Filtros Avanzados:** Puedes visualizar y manejar listas masivas buscando por nombre, código o filtrando cuáles están en riesgo (sin stock), e incluso revisando solo los productos "Descontinuados".
- **Historial Individual (La Lupa del Producto):** Cada ítem tiene un botón de "Historial" (📋) para observar qué día entró mercadería específica y a qué hora salió, todo numerado mágicamente.

## 3. 📋 Historial Global de Ventas y Movimientos
- **Ventas (Tablero Auditor):** Muestra todas las transacciones históricas de arriba abajo.
  Desde acá podrás ver qué se cobró por Efectivo o QR en el día. Y también el gran superpoder: **Anular Ventas Completas** (que regresa los productos al stock en un clic) o presionar "🖨 Imprimir Comprobante" para volver a exportar un viejo ticket descargable.
- **Movimientos:** Es el registro "forense". Todo lo que afecte al stock aparece aquí (ingresos manuales, compras registradas en el POS, ajustes misteriosos, etc).
  Cualquier alteración humana reporta el _Motivo_ y la _Cantidad_, sin censura.

## 4. 🗄️ Turnos de Caja (Cierre de fin de jornada)
No puedes vender hoy si no abres turno de hoy.
- **Abrir Caja:** Se abre con "x" cantidad de sencillo (monedas base del día).
- **Cierre de Caja:** Al terminar tu jornada, los dueños calculan la plata física (Billetes) más la plata virtual (Vouchers QR) y se contrasta si sobró o faltó dinero del total que el sistema tiene anotado matemáticamente.
- **El Salto de Seguridad Final (Respaldo Automático):** En el segundo en el que se ejecuta el **"Cierre de Caja"**, el sistema bloquea todo, comprime por sí mismo una copia `.sql` de tu base de datos y la expulsa por los cielos enviándole ese archivo por mensaje de Telegram directo a tu número celular para que nunca pierdas datos y previniendo caídas totales de computadoras quemadas.

## 5. 🤖 Sistema Vigía con Bots de Telegram
Telegram no es un lujo, es el vigilante 24/7 de tu negocio. El sistema mandará mensajes a los dueños asignados en dos momentos críticos:
1. **Seguridad Operativa:** Avisa si un cajero logró vender un producto cuyo stock en tienda estaba en rojo de "Agotado". (Venta sin stock).
2. **Backups aéreos:** Te mandará el archivo sólido de la Base de Datos cada vez que cierren la tienda al atardecer.
