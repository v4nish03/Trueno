import client from './client'

export const reportes = {
    dashboard: () => client.get('/reportes/dashboard'),
    ventasDiarias: (fecha) => client.get('/reportes/ventas-diarias', { params: { fecha } }),
    mensual: (year, month) => client.get('/reportes/mensual', { params: { year, month } }),
    productosMasVendidos: (fecha_inicio, fecha_fin) =>
        client.get('/reportes/productos-mas-vendidos', { params: { fecha_inicio, fecha_fin } }),
    ventasSinStock: () => client.get('/reportes/ventas-sin-stock'),
    porProducto: () => client.get('/reportes/por-producto'),
    porMetodoPago: () => client.get('/reportes/por-metodo-pago'),
    ingresosInventario: (fecha_inicio, fecha_fin) =>
        client.get('/reportes/ingresos-inventario', { params: { fecha_inicio, fecha_fin } }),
}
