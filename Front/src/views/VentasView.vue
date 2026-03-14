<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">💰 Historial de Ventas</h1>
        <p class="page-subtitle">Todas las transacciones registradas</p>
      </div>
      <button class="btn btn-secondary btn-sm" @click="exportarCSV">📥 Exportar CSV</button>
    </div>

    <!-- Filtros -->
    <div class="card" style="margin-bottom: 20px; padding: 14px 16px;">
      <div style="display: grid; grid-template-columns: auto auto 1fr; gap: 12px; align-items: center;">
        <input v-model="filtroDesde" type="date" class="input" style="width: 150px" @change="cargar" />
        <input v-model="filtroHasta" type="date" class="input" style="width: 150px" @change="cargar" />
        <div style="display:flex; gap:8px; justify-content:flex-end;">
          <button class="btn btn-ghost btn-sm" @click="limpiarFiltros">✕ Limpiar filtros</button>
          <button class="btn btn-secondary btn-sm" style="display:flex;align-items:center;gap:5px" @click="cargar"><RefreshCw :size="13" /> Actualizar</button>
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
              <span class="badge" :class="v.metodo_pago === 'efectivo' ? 'badge-green' : 'badge-cyan'" style="display:flex; align-items:center; gap:3px">
                <Banknote v-if="v.metodo_pago === 'efectivo'" :size="11" />
                <QrCode v-else :size="11" />
                {{ v.metodo_pago === 'efectivo' ? 'Efectivo' : 'QR' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="v.tipo === 'sin_stock' ? 'badge-red' : 'badge-blue'" style="display:flex; align-items:center; gap:3px">
                <AlertTriangle v-if="v.tipo === 'sin_stock'" :size="11" />
                <Check v-else :size="11" />
                {{ v.tipo === 'sin_stock' ? 'Sin stock' : 'Normal' }}
              </span>
            </td>
            <td>
              <span class="badge" :class="estadoBadge(v.estado)">{{ v.estado }}</span>
            </td>
            <td>
              <div style="display:flex; gap:4px;" @click.stop>
                <button class="btn btn-ghost btn-sm" @click="abrirDetalle(v.id)" title="Ver detalle"><Eye :size="14" /></button>
                <button
                  v-if="v.estado === 'completa'"
                  class="btn btn-ghost btn-sm"
                  style="color:var(--color-danger)"
                  @click="anularVenta(v)"
                  title="Anular venta"
                ><Ban :size="14" /></button>
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
          <span class="modal-title">Venta #{{ modalDetalle.id }}</span>
          <div style="display:flex; gap:8px;">
            <button class="btn btn-primary btn-sm" style="display:flex;align-items:center;gap:5px" @click="imprimirTicket(modalDetalle)"><Printer :size="13" /> Imprimir Comprobante</button>
            <button class="btn btn-ghost btn-sm" @click="modalDetalle=null">✕</button>
          </div>
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
              <div style="font-size:16px; font-weight:700; display:flex; align-items:center; gap:6px">
                <Banknote v-if="detalleData.metodo_pago === 'efectivo'" :size="16" />
                <QrCode v-else :size="16" />
                {{ detalleData.metodo_pago === 'efectivo' ? 'Efectivo' : 'QR' }}
              </div>
            </div>
            <div class="kpi-card" style="padding:10px 14px">
              <div class="kpi-label">Estado</div>
              <span class="badge" :class="estadoBadge(detalleData.estado)" style="font-size:12px">{{ detalleData.estado }}</span>
            </div>
          </div>

          <div style="font-size:11px; color:var(--color-muted); margin-bottom:12px">
            {{ fmtFecha(detalleData.fecha) }}
            <span v-if="detalleData.tipo === 'sin_stock'" class="badge badge-red" style="margin-left:8px; display:inline-flex; align-items:center; gap:3px"><AlertTriangle :size="11" /> Vendido sin stock</span>
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

          <!-- Recibo y acciones -->
          <div style="display:flex; gap:8px; align-items:center; margin-top:4px; flex-wrap:wrap">
            <div v-if="detalleData.recibo" class="card" style="background: var(--color-surface-2); padding:10px 14px; flex:1">
              <div style="font-size:11px; color:var(--color-muted); margin-bottom:4px">🧾 Recibo</div>
              <div style="font-size:12px; font-family: monospace; color:var(--color-accent-2)">{{ detalleData.recibo.codigo_qr }}</div>
            </div>
            <button class="btn btn-secondary" @click="imprimirRecibo(detalleData)" style="white-space:nowrap; padding: 10px 14px; height: 100%">
              🖨 Imprimir
            </button>
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
import { Banknote, QrCode, AlertTriangle, Check, Eye, Ban, Printer, RefreshCw } from 'lucide-vue-next'
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

async function abrirDetalle(id) {
  modalDetalle.value = { id }
  detalleCargando.value = true
  detalleData.value = null
  try {
    const res = await ventasApi.obtener(id)
    detalleData.value = res.data
    // guardar el objeto completo para poder imprimirlo
    modalDetalle.value = res.data
  } catch (e) {
    alert('Error al cargar detalle: ' + e.message)
    modalDetalle.value = null
  } finally {
    detalleCargando.value = false
  }
}

function imprimirTicket(datos) {
  if (!datos || !datos.id) return
  
  // En VentasView, el objeto datos es toda la venta, pero la estructura que espera imprimirTicket
  // en PosView era { venta: {id, metodo_pago, total}, recibo: {...} }
  // Armamos una estructura compatible:
  const ventaFormat = {
    venta: {
      id: datos.id,
      metodo_pago: datos.metodo_pago,
      total: datos.total
    },
    recibo: null // Si tuviéramos información del recibo en detalleData, lo pondríamos aquí
  }

  const html = `
    <html><head><title>Ticket #${ventaFormat.venta.id}</title><style>
      body { font-family: monospace; font-size: 13px; max-width: 300px; margin: auto; padding: 16px }
      h2 { text-align:center; margin:0 0 4px } hr { border:1px dashed #ccc }
      .row { display:flex; justify-content:space-between }
      .total { font-size:16px; font-weight:bold; border-top:2px solid #000; margin-top:8px; padding-top:8px }
    </style></head><body>
      <h2>⚡ TRUENO MOTORS</h2>
      <p style="text-align:center;margin:0 0 8px">Uyuni, Bolivia · ${new Date().toLocaleString('es-BO')}</p>
      <hr/>
      <div class="row"><b>Venta #${ventaFormat.venta.id}</b><span style="text-transform:capitalize">${ventaFormat.venta.metodo_pago}</span></div>
      <hr/>
      
      <div class="row total"><span>TOTAL</span><span>Bs ${Number(ventaFormat.venta.total).toFixed(2)}</span></div>
      <p style="text-align:center;margin-top:16px;font-size:11px">¡Copia de comprobante!</p>
    </body></html>`
    
  const w = window.open('', '_blank', 'width=340,height=500')
  w.document.write(html)
  w.document.close()
  w.print()
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

function exportarCSV() {
  const headers = ['#', 'Fecha', 'Total (Bs)', 'Método', 'Tipo', 'Estado']
  const rows = ventas.value.map(v => [
    v.id, fmtFecha(v.fecha), Number(v.total).toFixed(2),
    v.metodo_pago, v.tipo, v.estado
  ])
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `ventas_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function imprimirRecibo(venta) {
  const items = (venta.productos || venta.items || [])
  const filas = items.map(i =>
    `<div class="row"><span>${i.nombre || i.producto_id} x${i.cantidad}</span><span>Bs ${Number((i.cantidad) * (i.precio_unitario ?? i.precio)).toFixed(2)}</span></div>`
  ).join('')
  const html = `
    <html><head><title>Recibo #${venta.id}</title><style>
      body { font-family: monospace; font-size: 13px; max-width: 300px; margin: auto; padding: 16px }
      h2 { text-align:center; margin:0 0 4px } hr { border:1px dashed #ccc }
      .row { display:flex; justify-content:space-between; margin:4px 0 }
      .total { font-size:16px; font-weight:bold; border-top:2px solid #000; margin-top:8px; padding-top:8px }
    </style></head><body>
      <h2>⚡ TRUENO MOTORS</h2>
      <p style="text-align:center;margin:0 0 8px">Uyuni, Bolivia · ${fmtFecha(venta.fecha)}</p>
      <hr/>
      <div class="row"><b>Venta #${venta.id}</b><span>${venta.metodo_pago === 'efectivo' ? 'Efectivo' : 'QR'}</span></div>
      <hr/>
      ${filas}
      <div class="row total"><span>TOTAL</span><span>Bs ${Number(venta.total).toFixed(2)}</span></div>
      ${venta.recibo ? `<p style="font-size:10px;text-align:center;margin-top:8px">${venta.recibo.codigo_qr}</p>` : ''}
      <p style="text-align:center;margin-top:12px;font-size:11px">¡Gracias por su compra!</p>
    </body></html>`
  const w = window.open('', '_blank', 'width=340,height=560')
  w.document.write(html)
  w.document.close()
  w.print()
}

onMounted(cargar)
</script>
