import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { ventas as ventasApi } from '@/api/ventas'

export const useCarritoStore = defineStore('carrito', () => {
    const cargando = ref(false)
    const error = ref(null)

    // Lista de carritos (pestañas)
    const pestanas = ref([
        { id: 1, nombre: 'Cliente 1', ventaId: null, items: [] }
    ])
    const tabActivaId = ref(1)
    let nextTabId = 2

    // ====== PERSISTENCIA LOCALSTORAGE ======
    const savedState = localStorage.getItem('trueno_carrito_state')
    if (savedState) {
        try {
            const parsed = JSON.parse(savedState)
            pestanas.value = parsed.pestanas || [{ id: 1, nombre: 'Cliente 1', ventaId: null, items: [] }]
            tabActivaId.value = parsed.tabActivaId || 1
            nextTabId = parsed.nextTabId || 2
        } catch (e) {
            console.error('Error parseando carrito de localStorage', e)
        }
    }

    watch([pestanas, tabActivaId], () => {
        localStorage.setItem('trueno_carrito_state', JSON.stringify({
            pestanas: pestanas.value,
            tabActivaId: tabActivaId.value,
            nextTabId: nextTabId
        }))
    }, { deep: true })
    // =======================================

    // Helpers para la pestaña activa
    const pestanaActiva = computed(() => pestanas.value.find(p => p.id === tabActivaId.value) || pestanas.value[0])

    const ventaId = computed(() => pestanaActiva.value?.ventaId)
    const items = computed(() => pestanaActiva.value?.items || [])

    const total = computed(() =>
        items.value.reduce((sum, item) => sum + item.cantidad * item.precio_unitario, 0)
    )
    const cantidadItems = computed(() => items.value.length)

    // Manejo de Pestañas
    function nuevaPestana() {
        const id = nextTabId++
        pestanas.value.push({
            id,
            nombre: `Cliente ${id}`,
            ventaId: null,
            items: []
        })
        tabActivaId.value = id
    }

    function cambiarPestana(id) {
        if (pestanas.value.some(p => p.id === id)) {
            tabActivaId.value = id
        }
    }

    function cerrarPestana(id) {
        if (pestanas.value.length === 1) {
            limpiar() // Si es la última, solo la vaciamos
            return
        }
        const index = pestanas.value.findIndex(p => p.id === id)
        pestanas.value = pestanas.value.filter(p => p.id !== id)
        // Si cerramos la pestaña activa, cambiamos a otra
        if (tabActivaId.value === id) {
            // Selecciona la anterior, o si era la primera, la siguiente (que ahora es índice 0)
            const nuevaActiva = pestanas.value[Math.max(0, index - 1)]
            tabActivaId.value = nuevaActiva.id
        }
    }

    // Funciones del API backend
    async function abrirVenta() {
        cargando.value = true
        error.value = null
        try {
            const res = await ventasApi.abrir()
            pestanaActiva.value.ventaId = res.data.venta_id
            pestanaActiva.value.items = []
        } catch (e) {
            error.value = e.message
            throw e
        } finally {
            cargando.value = false
        }
    }

    async function agregarItem(producto, cantidad = 1) {
        if (!ventaId.value) await abrirVenta()

        // Verificar si ya existe en este carrito
        const existente = items.value.find(i => i.producto_id === producto.id)
        if (existente) {
            existente.cantidad += cantidad
            try {
                await ventasApi.agregarProducto(ventaId.value, {
                    producto_id: producto.id,
                    cantidad,
                    precio_unitario: existente.precio_unitario
                })
            } catch (e) {
                existente.cantidad -= cantidad
                throw e
            }
            return
        }

        try {
            await ventasApi.agregarProducto(ventaId.value, {
                producto_id: producto.id,
                cantidad,
                precio_unitario: producto.precio1
            })
            pestanaActiva.value.items.push({
                producto_id: producto.id,
                nombre: producto.nombre,
                codigo: producto.codigo,
                cantidad,
                precio_unitario: producto.precio1,
                stock: producto.stock,
            })
        } catch (e) {
            error.value = e.message
            throw e
        }
    }

    async function quitarItem(productoId) {
        if (!ventaId.value) return
        try {
            await ventasApi.eliminarProducto(ventaId.value, productoId)
            pestanaActiva.value.items = pestanaActiva.value.items.filter(i => i.producto_id !== productoId)
        } catch (e) {
            error.value = e.message
            throw e
        }
    }

    async function actualizarCantidad(productoId, nuevaCantidad) {
        if (nuevaCantidad < 1) {
            await quitarItem(productoId)
            return
        }
        const item = items.value.find(i => i.producto_id === productoId)
        if (!item) return
        const diff = nuevaCantidad - item.cantidad
        if (diff === 0) return

        try {
            if (diff > 0) {
                await ventasApi.agregarProducto(ventaId.value, {
                    producto_id: productoId,
                    cantidad: diff,
                    precio_unitario: item.precio_unitario
                })
            } else {
                // Para reducir, eliminar y re-agregar
                await ventasApi.eliminarProducto(ventaId.value, productoId)
                if (nuevaCantidad > 0) {
                    await ventasApi.agregarProducto(ventaId.value, {
                        producto_id: productoId,
                        cantidad: nuevaCantidad,
                        precio_unitario: item.precio_unitario
                    })
                }
            }
            item.cantidad = nuevaCantidad
        } catch (e) {
            error.value = e.message
            throw e
        }
    }

    async function confirmarVenta(metodoPago) {
        if (!ventaId.value || items.value.length === 0) throw new Error('Carrito vacío')
        cargando.value = true
        try {
            const res = await ventasApi.cerrar(ventaId.value, metodoPago)
            cerrarPestana(tabActivaId.value) // Al completar, cerramos esta pestaña
            return res.data
        } catch (e) {
            error.value = e.message
            throw e
        } finally {
            cargando.value = false
        }
    }

    function limpiar() {
        if (pestanaActiva.value) {
            pestanaActiva.value.ventaId = null
            pestanaActiva.value.items = []
        }
        error.value = null
    }

    return {
        cargando, error,
        pestanas, tabActivaId,
        ventaId, items, total, cantidadItems,
        nuevaPestana, cambiarPestana, cerrarPestana,
        abrirVenta, agregarItem, quitarItem, actualizarCantidad, confirmarVenta, limpiar
    }
})
