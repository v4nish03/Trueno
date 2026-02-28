import { defineStore } from 'pinia'
import { ref } from 'vue'
import client from '@/api/client'

export const useCajaStore = defineStore('caja', () => {
    const abierta = ref(false)
    const turno = ref(null)
    const cargando = ref(false)

    async function checkEstado() {
        cargando.value = true
        try {
            const res = await client.get('/caja/estado')
            abierta.value = res.data.abierta
            turno.value = res.data.turno
        } catch (e) {
            console.error("Error comprobando caja", e)
        } finally {
            cargando.value = false
        }
    }

    async function abrirCaja(monto_inicial) {
        try {
            await client.post('/caja/abrir', { monto_inicial })
            await checkEstado()
        } catch (e) {
            throw new Error(e.response?.data?.detail || "Error al abrir la caja")
        }
    }

    async function cerrarCaja() {
        try {
            await client.post('/caja/cerrar')
            await checkEstado()
        } catch (e) {
            throw new Error(e.response?.data?.detail || "Error al cerrar la caja")
        }
    }

    return { abierta, turno, cargando, checkEstado, abrirCaja, cerrarCaja }
})
