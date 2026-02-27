<template>
  <div class="pos-wrapper">
    <!-- Panel izquierdo: Búsqueda -->
    <div class="pos-left">
      <div style="margin-bottom: 16px">
        <h1 style="font-size:20px; font-weight:800; margin:0 0 4px">🛒 Punto de Venta</h1>
        <p style="font-size:12px; color: var(--color-muted); margin:0">Busca + Enter para agregar · Rápido como caja</p>
      </div>

      <!-- Barra de búsqueda -->
      <div class="pos-search-container" style="margin-bottom: 16px">
        <input
          ref="inputBusqueda"
          v-model="query"
          class="input"
          style="border:none; background:transparent; font-size:16px; padding: 10px 14px"
          placeholder="🔍  Nombre o código del producto..."
          @keydown.enter="seleccionarPrimero"
          @input="buscar"
          autofocus
        />
      </div>

      <!-- Resultados de búsqueda -->
      <div v-if="resultados.length > 0" class="resultados-lista">
        <div
          v-for="(p, i) in resultados"
          :key="p.id"
          class="resultado-item"
          :class="{ 'resultado-selected': i === indiceSeleccionado }"
          @click="agregarAlCarrito(p)"
        >
          <div style="flex:1; min-width:0">
            <div style="font-weight:600; font-size:13px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">
              {{ p.nombre }}
            </div>
            <div style="font-size:11px; color:var(--color-muted)">{{ p.codigo }}</div>
          </div>
          <div style="display:flex; flex-direction:column; align-items:flex-end; gap:4px">
            <span style="font-weight:700; color:var(--color-success); font-size:14px">Bs {{ fmt(p.precio1) }}</span>
            <span :class="stockBadge(p)" style="font-size:10px">{{ p.stock === 0 ? '🔴 Sin stock' : (p.stock <= p.stock_minimo ? '🟡 ' + p.stock : '🟢 ' + p.stock) }}</span>
          </div>
        </div>
      </div>

      <div v-else-if="query && !buscando" class="empty-state" style="padding: 32px 0">
        <div class="empty-state-icon">🔍</div>
        <div class="empty-state-text">Sin resultados para "{{ query }}"</div>
      </div>

      <div v-if="buscando" class="loading-center" style="padding: 32px 0">
        <div class="spinner"></div>
      </div>

      <!-- Mensaje de éxito -->
      <transition name="fade">
        <div v-if="mensajeExito" class="alert alert-success" style="margin-top:12px">
          ✅ {{ mensajeExito }}
        </div>
      </transition>

      <transition name="fade">
        <div v-if="mensajeError" class="alert alert-danger" style="margin-top:12px">
          ⚠️ {{ mensajeError }}
        </div>
      </transition>
    </div>

    <!-- Panel derecho: Carrito -->
    <div class="pos-right">
      <div style="margin-bottom: 14px; display:flex; align-items:center; justify-content:space-between">
        <span style="font-size:15px; font-weight:700">
          🧾 Carrito
          <span v-if="carrito.cantidadItems > 0" class="badge badge-blue" style="margin-left:4px">{{ carrito.cantidadItems }}</span>
        </span>
        <button
          v-if="carrito.items.length > 0"
          class="btn btn-ghost btn-sm"
          style="color:var(--color-danger)"
          @click="limpiarCarrito"
        >🗑 Limpiar</button>
      </div>

      <!-- Items del carrito -->
      <div class="carrito-lista">
        <div v-if="carrito.items.length === 0" class="empty-state" style="height:100%; justify-content:center">
          <div class="empty-state-icon">🛒</div>
          <div class="empty-state-text">Carrito vacío</div>
          <div style="font-size:11px; color:var(--color-muted); margin-top:4px">Busca un producto y presiona Enter</div>
        </div>

        <div v-for="item in carrito.items" :key="item.producto_id" class="cart-item">
          <div style="flex:1; min-width:0">
            <div style="font-size:12px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis">
              {{ item.nombre }}
            </div>
            <div style="font-size:11px; color:var(--color-muted)">Bs {{ fmt(item.precio_unitario) }} c/u</div>
          </div>
          <!-- Cantidad -->
          <div class="qty-control">
            <button class="qty-btn" @click="cambiarCantidad(item, -1)">−</button>
            <span class="qty-value">{{ item.cantidad }}</span>
            <button class="qty-btn" @click="cambiarCantidad(item, 1)">+</button>
          </div>
          <div style="font-weight:700; font-size:13px; min-width:70px; text-align:right; color:var(--color-accent)">
            Bs {{ fmt(item.cantidad * item.precio_unitario) }}
          </div>
          <button class="btn btn-ghost btn-sm" @click="carrito.quitarItem(item.producto_id)" style="color:var(--color-danger)">✕</button>
        </div>
      </div>

      <!-- Total y confirmar -->
      <div class="carrito-footer">
        <div class="cart-total">
          <div style="font-size:12px; font-weight:500; opacity:0.8; margin-bottom:4px">TOTAL</div>
          Bs {{ fmt(carrito.total) }}
        </div>

        <button
          class="btn btn-success"
          style="width:100%; padding: 14px; font-size:15px; font-weight:700; border-radius: 10px; margin-top:10px"
          :disabled="carrito.items.length === 0 || carrito.cargando"
          @click="abrirConfirmar"
        >
          <div v-if="carrito.cargando" class="spinner" style="width:16px;height:16px"></div>
          ✅ Confirmar Venta
        </button>
      </div>
    </div>

    <!-- Modal Confirmar Venta -->
    <div v-if="modalConfirmar" class="modal-backdrop" @click.self="modalConfirmar=false">
      <div class="modal">
        <div class="modal-header">
          <span class="modal-title">💳 Confirmar Venta</span>
          <button class="btn btn-ghost btn-sm" @click="modalConfirmar=false">✕</button>
        </div>

        <!-- Resumen -->
        <div class="resumen-venta">
          <div v-for="item in carrito.items" :key="item.producto_id" class="resumen-row">
            <span>{{ item.nombre }}</span>
            <span>{{ item.cantidad }}x</span>
            <span>Bs {{ fmt(item.cantidad * item.precio_unitario) }}</span>
          </div>
        </div>

        <div class="cart-total" style="margin: 16px 0">
          TOTAL: Bs {{ fmt(carrito.total) }}
        </div>

        <div class="form-group">
          <label class="form-label">Método de Pago</label>
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px">
            <button
              class="metodo-btn"
              :class="{ active: metodoPago === 'efectivo' }"
              @click="metodoPago = 'efectivo'"
            >💵 Efectivo</button>
            <button
              class="metodo-btn"
              :class="{ active: metodoPago === 'qr' }"
              @click="metodoPago = 'qr'"
            >📱 QR</button>
          </div>
        </div>

        <div v-if="errorConfirmar" class="alert alert-danger">{{ errorConfirmar }}</div>

        <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:16px">
          <button class="btn btn-secondary" @click="modalConfirmar=false">Cancelar</button>
          <button class="btn btn-success" @click="confirmarVenta" :disabled="!metodoPago || carrito.cargando" style="min-width:140px; font-size:14px">
            <div v-if="carrito.cargando" class="spinner" style="width:14px;height:14px"></div>
            ✅ Confirmar
          </button>
        </div>
      </div>
    </div>

    <!-- Modal éxito de venta -->
    <div v-if="ventaCompletada" class="modal-backdrop">
      <div class="modal" style="text-align:center">
        <div style="font-size:56px; margin-bottom:12px">🎉</div>
        <div style="font-size:20px; font-weight:800; margin-bottom:8px; color:var(--color-success)">¡Venta Completada!</div>
        <div style="font-size:14px; color:var(--color-muted); margin-bottom:4px">Venta #{{ ventaCompletada.venta.id }}</div>
        <div style="font-size:28px; font-weight:800; color:var(--color-accent); margin: 12px 0">
          Bs {{ fmt(ventaCompletada.venta.total) }}
        </div>
        <div class="badge" :class="ventaCompletada.venta.tipo === 'sin_stock' ? 'badge-red' : 'badge-green'" style="margin-bottom:16px; font-size:12px">
          {{ ventaCompletada.venta.tipo === 'sin_stock' ? '⚠️ Venta sin stock registrada' : '✅ Con stock' }}
        </div>
        <div style="font-size:12px; color:var(--color-muted); margin-bottom:20px">
          Método: {{ ventaCompletada.venta.metodo_pago }}
          · Recibo: {{ ventaCompletada.recibo?.codigo_qr || '' }}
        </div>
        <button class="btn btn-primary" style="width:100%" @click="ventaCompletada = null; focusBusqueda()">
          Nueva Venta
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { productos as productosApi } from '@/api/productos'
import { useCarritoStore } from '@/stores/carrito'

const carrito = useCarritoStore()
const query = ref('')
const resultados = ref([])
const buscando = ref(false)
const indiceSeleccionado = ref(0)
const inputBusqueda = ref(null)
const mensajeExito = ref('')
const mensajeError = ref('')
const modalConfirmar = ref(false)
const metodoPago = ref('efectivo')
const errorConfirmar = ref('')
const ventaCompletada = ref(null)

let buscarTimer = null

function fmt(n) {
  return Number(n || 0).toFixed(2)
}
function stockBadge(p) {
  if (p.stock === 0) return 'badge badge-red'
  if (p.stock <= p.stock_minimo) return 'badge badge-yellow'
  return 'badge badge-green'
}

async function buscar() {
  if (buscarTimer) clearTimeout(buscarTimer)
  if (!query.value.trim()) { resultados.value = []; return }
  buscarTimer = setTimeout(async () => {
    buscando.value = true
    try {
      const res = await productosApi.listar({ buscar: query.value, limit: 10 })
      resultados.value = res.data
      indiceSeleccionado.value = 0
    } catch (e) {
      resultados.value = []
    } finally {
      buscando.value = false
    }
  }, 200)
}

function seleccionarPrimero() {
  if (resultados.value.length > 0) {
    agregarAlCarrito(resultados.value[indiceSeleccionado.value])
  }
}

async function agregarAlCarrito(producto) {
  mensajeError.value = ''
  try {
    await carrito.agregarItem(producto, 1)
    mensajeExito.value = `✅ ${producto.nombre} agregado`
    query.value = ''
    resultados.value = []
    setTimeout(() => { mensajeExito.value = '' }, 2000)
    focusBusqueda()
  } catch (e) {
    mensajeError.value = e.message
    setTimeout(() => { mensajeError.value = '' }, 3000)
  }
}

async function cambiarCantidad(item, delta) {
  try {
    await carrito.actualizarCantidad(item.producto_id, item.cantidad + delta)
  } catch (e) {
    mensajeError.value = e.message
    setTimeout(() => { mensajeError.value = '' }, 3000)
  }
}

async function limpiarCarrito() {
  if (!confirm('¿Limpiar el carrito?')) return
  carrito.limpiar()
}

function abrirConfirmar() {
  errorConfirmar.value = ''
  metodoPago.value = 'efectivo'
  modalConfirmar.value = true
}

async function confirmarVenta() {
  if (!metodoPago.value) return
  errorConfirmar.value = ''
  try {
    const resultado = await carrito.confirmarVenta(metodoPago.value)
    modalConfirmar.value = false
    ventaCompletada.value = resultado
  } catch (e) {
    errorConfirmar.value = e.message
  }
}

function focusBusqueda() {
  nextTick(() => inputBusqueda.value?.focus())
}

onMounted(() => {
  focusBusqueda()
})
</script>

<style scoped>
.pos-wrapper {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 20px;
  height: calc(100vh - 56px);
  overflow: hidden;
}

.pos-left {
  overflow-y: auto;
  padding-right: 4px;
}

.pos-right {
  display: flex;
  flex-direction: column;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 16px;
  overflow: hidden;
}

.resultados-lista {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.resultado-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.12s;
}
.resultado-item:hover, .resultado-selected {
  border-color: var(--color-accent);
  background: rgba(108,99,255,0.08);
}

.carrito-lista {
  flex: 1;
  overflow-y: auto;
  min-height: 0;
  margin-bottom: 12px;
}

.carrito-footer {
  flex-shrink: 0;
}

.qty-control {
  display: flex;
  align-items: center;
  gap: 0;
  background: var(--color-surface-2);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  overflow: hidden;
}
.qty-btn {
  background: none;
  border: none;
  color: var(--color-text);
  cursor: pointer;
  width: 28px;
  height: 28px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.1s;
}
.qty-btn:hover { background: var(--color-border); }
.qty-value {
  min-width: 28px;
  text-align: center;
  font-size: 13px;
  font-weight: 700;
}

.resumen-venta {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 8px;
  margin-bottom: 8px;
}
.resumen-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 5px 0;
  font-size: 12px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
}
.resumen-row:last-child { border-bottom: none; }

.metodo-btn {
  padding: 12px;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface-2);
  color: var(--color-text);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.metodo-btn:hover { border-color: var(--color-accent); }
.metodo-btn.active {
  border-color: var(--color-success);
  background: rgba(34,197,94,0.1);
  color: var(--color-success);
}
</style>
