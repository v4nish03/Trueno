import { defineStore } from 'pinia'
import { ref } from 'vue'
import { alertas as alertasApi } from '@/api/alertas'

export const useAlertasStore = defineStore('alertas', () => {
    const stockBajo = ref([])
    const ventasSinStock = ref([])
    const totalStockBajo = ref(0)
    const totalSinStock = ref(0)
    let intervalId = null

    async function cargar() {
        try {
            const [r1, r2] = await Promise.all([
                alertasApi.stockBajo(),
                alertasApi.ventasSinStock(),
            ])
            stockBajo.value = r1.data.productos || []
            totalStockBajo.value = r1.data.total || 0
            ventasSinStock.value = r2.data.productos || []
            totalSinStock.value = r2.data.total || 0
        } catch (e) {
            console.warn('No se pudieron cargar alertas:', e.message)
        }
    }

    function iniciar() {
        cargar()
        intervalId = setInterval(cargar, 60000)
    }

    function detener() {
        if (intervalId) clearInterval(intervalId)
    }

    return { stockBajo, ventasSinStock, totalStockBajo, totalSinStock, cargar, iniciar, detener }
})
