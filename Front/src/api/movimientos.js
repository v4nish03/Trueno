import client from './client'

export const movimientos = {
    listar: (params = {}) => client.get('/movimientos', { params }),
}

