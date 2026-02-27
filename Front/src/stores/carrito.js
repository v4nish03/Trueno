import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { ventas as ventasApi } from '@/api/ventas'

export const useCarritoStore = defineStore('carrito', () => {
    const ventaId = ref(null)
    const items = ref([])
    const cargando = ref(false)
    const error = ref(null)

    const total = computed(() =>
        items.value.reduce((sum, item) => sum + item.cantidad * item.precio_unitario, 0)
    )

    const cantidadItems = computed(() => items.value.length)

    async function abrirVenta() {
        cargando.value = true
        error.value = null
        try {
            const res = await ventasApi.abrir()
            ventaId.value = res.data.venta_id
            items.value = []
        } catch (e) {
            error.value = e.message
            throw e
        } finally {
            cargando.value = false
        }
    }

    async function agregarItem(producto, cantidad = 1) {
        if (!ventaId.value) await abrirVenta()

        // Verificar si ya existe en carrito
        const existente = items.value.find(i => i.producto_id === producto.id)
        if (existente) {
            existente.cantidad += cantidad
            // Actualizar en backend
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
            items.value.push({
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
            items.value = items.value.filter(i => i.producto_id !== productoId)
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
                // Para reducir, necesitamos eliminar y re-agregar
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
            limpiar()
            return res.data
        } catch (e) {
            error.value = e.message
            throw e
        } finally {
            cargando.value = false
        }
    }

    function limpiar() {
        ventaId.value = null
        items.value = []
        error.value = null
    }

    return {
        ventaId, items, cargando, error, total, cantidadItems,
        abrirVenta, agregarItem, quitarItem, actualizarCantidad, confirmarVenta, limpiar
    }
})
