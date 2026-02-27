import axios from 'axios'

const client = axios.create({
    baseURL: '/api',
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
    }
})

// Interceptor de errores global
client.interceptors.response.use(
    response => response,
    error => {
        const msg = error.response?.data?.detail || error.message || 'Error de conexión'
        console.error('[API Error]', msg, error.response?.status)
        return Promise.reject(new Error(msg))
    }
)

export default client
