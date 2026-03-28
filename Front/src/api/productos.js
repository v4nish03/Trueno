import client from './client'

export const productos = {
    listar: (params = {}) => client.get('/productos/', { params }),
    categorias: (params = {}) => client.get('/productos/categorias', { params }),
    subirImagen: (formData) => client.post('/productos/upload-imagen', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    descargarCatalogoPdf: (params = {}) => client.get('/productos/catalogo-pdf', {
        params,
        responseType: 'blob',
    }),
    obtener: (id) => client.get(`/productos/${id}`),
    obtenerPorCodigo: (codigo) => client.get(`/productos/codigo/${codigo}`),
    crear: (data) => client.post('/productos/', data),
    actualizar: (id, data) => client.put(`/productos/${id}`, data),
    descontinuar: (id) => client.delete(`/productos/${id}`),
    reactivar: (id) => client.post(`/productos/${id}/reactivar`),
    ingresarStock: (id, cantidad, motivo = 'compra', ubicacion = 'tienda') =>
        client.post(`/productos/${id}/ingresar-stock`, null, { params: { cantidad, motivo, ubicacion } }),
    ajustarStock: (id, nuevo_stock, ubicacion = 'tienda') =>
        client.post(`/productos/${id}/ajustar-stock`, null, { params: { nuevo_stock, ubicacion } }),
    moverBodegaATienda: (id, cantidad) =>
        client.post(`/productos/${id}/mover-bodega-tienda`, null, { params: { cantidad } }),
    historial: (id) => client.get(`/productos/${id}/historial`),
}
