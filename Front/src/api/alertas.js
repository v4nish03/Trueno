import client from './client'

export const alertas = {
    stockBajo: () => client.get('/alertas/stock-bajo'),
    ventasSinStock: () => client.get('/alertas/ventas-sin-stock'),
}
