import client from './client'

export const ventas = {
    listar: (params = {}) => client.get('/ventas', { params }),
    obtener: (id) => client.get(`/ventas/${id}`),
    abrir: () => client.post('/ventas/abrir'),
    agregarProducto: (ventaId, data) => client.post(`/ventas/${ventaId}/productos`, data),
    eliminarProducto: (ventaId, productoId) => client.delete(`/ventas/${ventaId}/productos/${productoId}`),
    cerrar: (ventaId, metodo_pago) => client.post(`/ventas/${ventaId}/cerrar`, { metodo_pago }),
    anular: (ventaId) => client.post(`/ventas/${ventaId}/anular`),
}
