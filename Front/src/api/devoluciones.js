import client from './client'

export const devoluciones = {
    devolver: (ventaId, productoId, cantidad) =>
        client.post(`/devoluciones/${ventaId}/productos`, { producto_id: productoId, cantidad }),
}
