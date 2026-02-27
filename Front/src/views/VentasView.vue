<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">💰 Historial de Ventas</h1>
      <p class="page-subtitle">Todas las transacciones registradas</p>
    </div>

    <!-- Filtros -->
    <div class="card" style="margin-bottom: 20px; padding: 14px 16px;">
      <div style="display: grid; grid-template-columns: auto auto 1fr; gap: 12px; align-items: center;">
        <input v-model="filtroDesde" type="date" class="input" style="width: 150px" @change="cargar" />
        <input v-model="filtroHasta" type="date" class="input" style="width: 150px" @change="cargar" />
        <div style="display:flex; gap:8px; justify-content:flex-end;">
          <button class="btn btn-ghost btn-sm" @click="limpiarFiltros">✕ Limpiar filtros</button>
          <button class="btn btn-secondary btn-sm" @click="cargar">🔄 Actualizar</button>
        </div>
      </div>
    </div>

    <!-- Resumen rápido -->
    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:14px; margin-bottom: 20px">
      <div class="kpi-card accent" style="padding:12px 16px">
        <div class="kpi-label">Total ventas</div>
        <div style="font-size:22px; font-weight:800; color:var(--color-accent)">Bs {{ fmt(totalVendido) }}</div>
        <div class="kpi-sub">{{ ventas.length }} transacciones</div>
      </div>
      <div class="kpi-card success" style="padding:12px 16px">
        <div class="kpi-label">Efectivo</div>
        <div style="font-size:22px; font-weight:800; color:var(--color-success)">Bs {{ fmt(totalEfectivo) }}</div>
      </div>
      <div class="kpi-card cyan" style="padding:12px 16px">
        <div class="kpi-label">QR</div>
        <div style="font-size:22px; font-weight:800; color:var(--color-accent-2)">Bs {{ fmt(totalQr) }}</div>
      </div>
    </div>

    <div v-if="cargando" class="loading-center"><div class="spinner"></div></div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Fecha</th>
            <th>Total</th>
            <th>Método</th>
            <th>Tipo</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="ventas.length === 0">
            <td colspan="7" class="empty-state">
              <div class="empty-state-icon">💰</div>
              <div class="empty-state-text">Sin ventas en el período seleccionado</div>
            </td>
          </tr>
          <tr v-for="v in ventas" :key="v.id" style="cursor:pointer" @click="abrirDetalle(v.id)">
            <td style="font-size:11px; color:var(--color-muted)">#{{ v.id }}</td>
            <td style="font-size:12px; white-space:nowrap">{{ fmtFecha(v.fecha) }}</td>
            <td style="font-weight:700; color:var(--color-accent)">
              Bs {{ fmt(v.total) }}
            </td>
            <td>
              <span class="badge" :class="v.metodo_pago === 'efectivo' ? 'badge-green' : 'badge-cyan'">
                {{ v.metodo_pago === 'efectivo' ? '💵 Efectivo' : '📱 QR' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="v.tipo === 'sin_stock' ? 'badge-red' : 'badge-blue'">
                {{ v.tipo === 'sin_stock' ? '⚠️ Sin stock' : '✅ Normal' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="estadoBadge(v.estado)">{{ v.estado }}</span>
            </td>
            <td>
              <div style="display:flex; gap:4px;" @click.stop>
                <button class="btn btn-ghost btn-sm" @click="abrirDetalle(v.id)" title="Ver detalle">👁</button>
                <button
                  v-if="v.estado === 'completa'"
                  class="btn btn-ghost btn-sm"
                  style="color:var(--color-danger)"
                  @click="anularVenta(v)"
                  title="Anular venta"
                >🚫</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal detalle de venta -->
    <div v-if="modalDetalle" class="modal-backdrop" @click.self="modalDetalle=null">
      <div class="modal modal-lg">
        <div class="modal-header">
          <span class="modal-title">📄 Venta #{{ modalDetalle.id }}</span>
          <button class="btn btn-ghost btn-sm" @click="modalDetalle=null">✕</button>
        </div>

        <div v-if="detalleCargando" class="loading-center"><div class="spinner"></div></div>
        <template v-else-if="detalleData">
          <!-- Info principal -->
          <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:12px; margin-bottom:16px">
            <div class="kpi-card" style="padding:10px 14px">
              <div class="kpi-label">Total</div>
              <div style="font-size:20px; font-weight:800; color:var(--color-accent)">Bs {{ fmt(detalleData.total) }}</div>
            </div>
            <div class="kpi-card" style="padding:10px 14px">
              <div class="kpi-label">Método</div>
              <div style="font-size:16px; font-weight:700">{{ detalleData.metodo_pago === 'efectivo' ? '💵 Efectivo' : '📱 QR' }}</div>
            </div>
            <div class="kpi-card" style="padding:10px 14px">
              <div class="kpi-label">Estado</div>
              <span class="badge" :class="estadoBadge(detalleData.estado)" style="font-size:12px">{{ detalleData.estado }}</span>
            </div>
          </div>

          <div style="font-size:11px; color:var(--color-muted); margin-bottom:12px">
            {{ fmtFecha(detalleData.fecha) }}
            <span v-if="detalleData.tipo === 'sin_stock'" class="badge badge-red" style="margin-left:8px">⚠️ Vendido sin stock</span>
          </div>

          <!-- Productos -->
          <div class="section-title" style="margin-bottom:10px">Productos</div>
          <div class="table-wrapper" style="margin-bottom:16px">
            <table>
              <thead>
                <tr>
                  <th>Producto</th>
                  <th>Cantidad</th>
                  <th>Precio Unit.</th>
                  <th>Subtotal</th>
                  <th>Devolución</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in detalleData.productos || detalleData.items || []" :key="item.producto_id">
                  <td style="font-weight:500; font-size:12px">{{ item.nombre || item.producto_nombre || item.producto_id }}</td>
                  <td>{{ item.cantidad }}</td>
                  <td>Bs {{ fmt(item.precio_unitario ?? item.precio) }}</td>
                  <td style="font-weight:700; color:var(--color-accent)">Bs {{ fmt((item.cantidad) * (item.precio_unitario ?? item.precio)) }}</td>
                  <td>
                    <button
                      v-if="detalleData.estado === 'completa'"
                      class="btn btn-ghost btn-sm"
                      style="color:var(--color-warning); font-size:11px"
                      @click="abrirDevolucion(item)"
                    >↩ Devolver</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Recibo -->
          <div v-if="detalleData.recibo" class="card" style="background: var(--color-surface-2); padding:12px 14px">
            <div style="font-size:11px; color:var(--color-muted); margin-bottom:4px">🧾 Recibo</div>
            <div style="font-size:12px; font-family: monospace; color:var(--color-accent-2)">{{ detalleData.recibo.codigo_qr }}</div>
          </div>
        </template>

        <!-- Modal devolución -->
        <div v-if="modalDevolucion" class="modal-backdrop" style="border-radius:14px" @click.self="modalDevolucion=null">
          <div class="modal">
            <div class="modal-header">
              <span class="modal-title">↩ Devolución</span>
              <button class="btn btn-ghost btn-sm" @click="modalDevolucion=null">✕</button>
            </div>
            <p style="font-size:13px; color:var(--color-muted)">{{ modalDevolucion.nombre || modalDevolucion.producto_id }}</p>
            <div class="form-group" style="margin-top:12px">
              <label class="form-label">Cantidad a devolver (máx. {{ modalDevolucion.cantidad }})</label>
              <input v-model.number="cantDevolucion" type="number" min="1" :max="modalDevolucion.cantidad" class="input" />
            </div>
            <div v-if="errorDevolucion" class="alert alert-danger">{{ errorDevolucion }}</div>
            <div style="display:flex; gap:8px; justify-content:flex-end; margin-top:14px">
              <button class="btn btn-secondary" @click="modalDevolucion=null">Cancelar</button>
              <button class="btn btn-primary" @click="confirmarDevolucion" :disabled="devolucionando">
                <div v-if="devolucionando" class="spinner" style="width:14px;height:14px"></div>
                Confirmar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ventas as ventasApi } from '@/api/ventas'
import { devoluciones as devolucionesApi } from '@/api/devoluciones'

const ventas = ref([])
const cargando = ref(true)
const filtroDesde = ref('')
const filtroHasta = ref('')
const modalDetalle = ref(null)
const detalleData = ref(null)
const detalleCargando = ref(false)
const modalDevolucion = ref(null)
const cantDevolucion = ref(1)
const errorDevolucion = ref('')
const devolucionando = ref(false)

const totalVendido = computed(() =>
  ventas.value.filter(v => v.estado === 'completa').reduce((s, v) => s + (v.total || 0), 0)
)
const totalEfectivo = computed(() =>
  ventas.value.filter(v => v.estado === 'completa' && v.metodo_pago === 'efectivo').reduce((s, v) => s + (v.total || 0), 0)
)
const totalQr = computed(() =>
  ventas.value.filter(v => v.estado === 'completa' && v.metodo_pago === 'qr').reduce((s, v) => s + (v.total || 0), 0)
)

function estadoBadge(estado) {
  if (estado === 'completa') return 'badge-green'
  if (estado === 'anulada') return 'badge-red'
  return 'badge-yellow'
}
function fmt(n) { return Number(n || 0).toFixed(2) }
function fmtFecha(f) {
  return new Date(f).toLocaleString('es-BO', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

async function cargar() {
  cargando.value = true
  try {
    const params = { limit: 200 }
    if (filtroDesde.value) params.fecha_desde = filtroDesde.value
    if (filtroHasta.value) params.fecha_hasta = filtroHasta.value
    const res = await ventasApi.listar(params)
    ventas.value = (res.data || []).filter(v => v.estado !== 'abierta')
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function limpiarFiltros() {
  filtroDesde.value = ''
  filtroHasta.value = ''
  cargar()
}

async function abrirDetalle(ventaId) {
  modalDetalle.value = { id: ventaId }
  detalleData.value = null
  detalleCargando.value = true
  try {
    const res = await ventasApi.obtener(ventaId)
    detalleData.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    detalleCargando.value = false
  }
}

async function anularVenta(v) {
  if (!confirm(`¿Anular la venta #${v.id} por Bs ${fmt(v.total)}? Esto devuelve el stock.`)) return
  try {
    await ventasApi.anular(v.id)
    await cargar()
  } catch (e) {
    alert(e.message)
  }
}

function abrirDevolucion(item) {
  errorDevolucion.value = ''
  cantDevolucion.value = 1
  modalDevolucion.value = item
}

async function confirmarDevolucion() {
  devolucionando.value = true
  errorDevolucion.value = ''
  try {
    await devolucionesApi.devolver(modalDetalle.value.id, modalDevolucion.value.producto_id, cantDevolucion.value)
    modalDevolucion.value = null
    await abrirDetalle(modalDetalle.value.id)
  } catch (e) {
    errorDevolucion.value = e.message
  } finally {
    devolucionando.value = false
  }
}

onMounted(cargar)
</script>
