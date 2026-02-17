# Auditoría técnica del backend (Trueno)

Fecha: 2026-02-17

## Resumen ejecutivo

Estado general: **funcional pero no listo para producción**.

- Fortalezas: separación básica por capas, inventario con movimientos, snapshots de precio en venta, estados de venta (abierta/completa/anulada), devoluciones parciales y alertas de stock.
- Riesgos críticos: ausencia de autenticación/autorización, control transaccional incompleto en cierre de venta y huecos de concurrencia para ventas simultáneas.

---

## 1) Arquitectura (models/schemas/services/routers/database)

**Resultado: PARCIALMENTE CUMPLE**

✅ Correcto:
- `models/` concentra entidades ORM (`Producto`, `Venta`, `VentaProducto`, `MovimientoInventario`).
- `schemas/` usa Pydantic para requests/responses.
- `routers/` delega mayormente a `services/`.
- `database.py` centraliza engine/session.

⚠️ Observaciones:
- Hay lógica de infraestructura en router de ventas (`generar_recibo` se invoca desde router al cerrar).
- El service de ventas hace `commit()` en varios pasos de flujo (abrir/agregar/cerrar), sin bloque transaccional explícito para toda la operación de cierre.

---

## 2) Inventario por movimientos (no stock manual directo)

**Resultado: PARCIALMENTE CUMPLE**

✅ Correcto:
- Existe `MovimientoInventario` con tipos `ingreso/salida/ajuste` y motivos `compra/venta/devolucion/stock_inicial/correccion`.
- Creación de producto con `stock_inicial` registra movimiento `stock_inicial`.
- Ingresos y ajustes registran movimientos.
- Salidas por venta registran movimientos.

⚠️ Riesgo:
- Existe endpoint de **ajuste manual** de stock (`/productos/{id}/ajustar-stock`), aunque sí deja rastro en movimientos.
- No hay guardas a nivel DB para impedir cambios directos de `producto.stock` fuera de servicios.
- No existe política de "no borrado" para movimientos (no hay endpoint DELETE de movimientos, pero tampoco protección explícita a nivel modelo/DB).

---

## 3) Transacciones SQLAlchemy al crear/cerrar ventas

**Resultado: NO CUMPLE COMPLETAMENTE**

✅ Correcto:
- En flujo legado `crear_venta`, hay `try/except SQLAlchemyError` con rollback.

❌ Problemas:
- `cerrar_venta` no está envuelto en `try/except` con `rollback`.
- No hay `with db.begin()` ni `SELECT ... FOR UPDATE` para bloquear filas de producto en ventas simultáneas.
- El envío de alertas ocurre fuera del commit principal (bien para desacoplar), pero no hay cola asíncrona ni estrategia de reintento.

Impacto:
- En falla intermedia durante `cerrar_venta`, puede quedar operación inconsistente en la sesión antes del commit.
- En concurrencia, se puede vender en paralelo sin control fuerte de carrera.

---

## 4) Ventas sin stock (diseño actual)

**Resultado: CUMPLE PARCIALMENTE**

✅ Correcto:
- Si no alcanza stock, la venta se marca `sin_stock` y se incrementa `ventas_sin_stock`.
- Se genera movimiento de salida para trazabilidad.

⚠️ Observación importante:
- Cuando no hay stock suficiente, **no se descuenta stock** (evita negativos), pero se registra movimiento de salida por la cantidad completa vendida. Esto puede ser válido por diseño comercial, pero requiere reglas explícitas de backorder/pendiente para evitar ambigüedad operativa.

---

## 5) Integridad de datos

**Resultado: PARCIALMENTE CUMPLE**

✅ Correcto:
- Existen claves foráneas en `venta_productos` y `movimientos_inventario`.
- Se valida existencia de producto/venta antes de operar.

❌ Debilidades:
- Faltan `ondelete` explícitos y configuración de cascadas ORM en relaciones críticas.
- Validaciones Pydantic insuficientes en ventas: `cantidad` y `precio_unitario` no tienen constraints (`gt=0`).
- `movimiento.cantidad` no valida signo ni coherencia por tipo en schema.

---

## 6) No borrar registros críticos

**Resultado: CUMPLE EN VENTAS/MOVIMIENTOS, CON RIESGO EN DETALLES**

✅ Correcto:
- No existe endpoint para borrar ventas completas; se usa `anular` (cambio de estado).
- No se observan endpoints de borrado físico de movimientos.

⚠️ Riesgo:
- Sí existe borrado físico de detalle de venta abierta (`DELETE /ventas/{venta_id}/productos/{producto_id}`). Esto puede ser aceptable solo mientras la venta está abierta, pero debe quedar normado.

---

## 7) Cálculo de totales y snapshot de precio

**Resultado: CUMPLE**

✅ Correcto:
- La venta calcula total con suma de subtotales al cerrar.
- `VentaProducto.precio_unitario` conserva snapshot de precio histórico.
- Reportes usan `cantidad * precio_unitario` de detalle, no precio actual de producto.

---

## 8) Seguridad mínima

**Resultado: NO CUMPLE**

❌ Crítico:
- No hay autenticación en routers principales (`productos`, `ventas`, `devoluciones`, `alertas`, `reportes`).
- CORS abierto (`allow_origins=["*"]`) en aplicación principal.
- No se aprecia separación de rutas admin/user ni controles por rol.

---

## 9) Alertas de stock bajo

**Resultado: CUMPLE PARCIALMENTE**

✅ Correcto:
- Se alerta cuando `stock <= stock_minimo`.
- Existe integración con Telegram vía `enviar_mensaje`.

⚠️ Observación:
- El disparo de alertas está invocado desde `cerrar_venta`; conviene desacoplar mediante evento/cola para no mezclar notificación con flujo de venta.

---

## 10) Resistencia a errores comunes

**Resultado: NO CUMPLE COMPLETAMENTE**

✅ Correcto:
- Soporta producto sin stock (venta tipo `sin_stock`).
- Soporta devolución parcial.

❌ Pendiente:
- No hay mecanismos robustos para dos ventas simultáneas del mismo producto (sin locks).
- No hay estrategia transaccional explícita por unidad de trabajo para cierre de venta.
- No hay pruebas de concurrencia.

---

## Hallazgos prioritarios (ordenados)

1. **Implementar auth/autz mínima (JWT + roles)** para crear/cerrar/anular ventas y para rutas de inventario/reportes.
2. **Refactor transaccional de `cerrar_venta`**: `with db.begin()`, rollback garantizado y bloqueos por producto (`with_for_update`) o estrategia equivalente.
3. **Fortalecer validaciones Pydantic**: `cantidad > 0`, `precio_unitario > 0`, enum estricto para método de pago/motivos.
4. **Definir política de inmutabilidad** de movimientos y ventas (sin DELETE físico) a nivel API y DB.
5. **Desacoplar alertas** a un mecanismo async/event-driven.
6. **Agregar pruebas de concurrencia** y escenarios de caída durante cierre de venta.

---

## Veredicto final

El backend está bien encaminado para un entorno de desarrollo/operación controlada, pero **todavía no cumple nivel producción** por seguridad, concurrencia y atomicidad transaccional en flujo de venta.
