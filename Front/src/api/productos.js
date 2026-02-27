import client from './client'

export const productos = {
    listar: (params = {}) => client.get('/productos', { params }),
    obtener: (id) => client.get(`/productos/${id}`),
    obtenerPorCodigo: (codigo) => client.get(`/productos/codigo/${codigo}`),
    crear: (data) => client.post('/productos', data),
    actualizar: (id, data) => client.put(`/productos/${id}`, data),
    descontinuar: (id) => client.delete(`/productos/${id}`),
    reactivar: (id) => client.post(`/productos/${id}/reactivar`),
    ingresarStock: (id, cantidad, motivo = 'compra') =>
        client.post(`/productos/${id}/ingresar-stock`, null, { params: { cantidad, motivo } }),
    ajustarStock: (id, nuevo_stock) =>
        client.post(`/productos/${id}/ajustar-stock`, null, { params: { nuevo_stock } }),
    historial: (id) => client.get(`/productos/${id}/historial`),
}
