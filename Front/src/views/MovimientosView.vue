<template>
  <div>
    <div class="page-header">
      <div>
        <h1 class="page-title">📊 Movimientos de Inventario</h1>
        <p class="page-subtitle">Ingresos, salidas y ajustes de stock · {{ total }} registros</p>
      </div>
      <button class="btn btn-secondary btn-sm" @click="exportarCSV">📥 Exportar CSV</button>
    </div>

    <!-- Filtros -->
    <div class="card" style="margin-bottom: 20px; padding: 14px 16px;">
      <div style="display: grid; grid-template-columns: 1fr 150px 150px 150px; gap: 12px; align-items: center;">
        <input v-model="filtros.buscar" class="input" placeholder="🔍  Buscar producto..." @input="cargar" />
        <select v-model="filtros.tipo" class="input" @change="cargar">
          <option value="">Todos</option>
          <option value="ingreso">📥 Ingreso</option>
          <option value="salida">📤 Salida</option>
          <option value="ajuste">🔧 Ajuste</option>
        </select>
        <input v-model="filtros.desde" type="date" class="input" @change="cargar" />
        <input v-model="filtros.hasta" type="date" class="input" @change="cargar" />
      </div>
    </div>

    <div v-if="cargando" class="loading-center"><div class="spinner"></div></div>

    <div v-else class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Fecha</th>
            <th>Producto</th>
            <th>Tipo</th>
            <th>Motivo</th>
            <th>Cantidad</th>
            <th>Ref.</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="movimientos.length === 0">
            <td colspan="7" class="empty-state">
              <div class="empty-state-icon">📊</div>
              <div class="empty-state-text">Sin movimientos para los filtros aplicados</div>
            </td>
          </tr>
          <tr v-for="m in movimientos" :key="m.id">
            <td style="color:var(--color-muted); font-size:11px">{{ m.id }}</td>
            <td style="font-size:12px; white-space:nowrap">{{ fmtFecha(m.fecha) }}</td>
            <td>
              <div style="font-weight:500; font-size:12px">{{ m.nombre_producto }}</div>
              <div style="font-size:11px; color:var(--color-muted)">{{ m.codigo_producto }}</div>
            </td>
            <td><span :class="tipoBadge(m.tipo)">{{ m.tipo }}</span></td>
            <td><span class="badge badge-gray" style="text-transform:capitalize">{{ m.motivo }}</span></td>
            <td>
              <span style="font-weight:800; font-size:14px" :style="m.tipo === 'salida' ? 'color:var(--color-danger)' : 'color:var(--color-success)'">
                {{ m.tipo === 'salida' ? '−' : '+' }}{{ m.cantidad }}
              </span>
            </td>
            <td style="color:var(--color-muted); font-size:11px">{{ m.referencia_id ? '#' + m.referencia_id : '—' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación -->
    <div v-if="!cargando && total > limit" style="display:flex; justify-content:center; align-items:center; gap:12px; margin-top:16px">
      <button class="btn btn-secondary btn-sm" :disabled="skip === 0" @click="paginaAnterior">← Anterior</button>
      <span style="font-size:12px; color:var(--color-muted)">
        {{ skip + 1 }}–{{ Math.min(skip + limit, total) }} de {{ total }}
      </span>
      <button class="btn btn-secondary btn-sm" :disabled="skip + limit >= total" @click="paginaSiguiente">Siguiente →</button>
    </div>

    <!-- KPIs resumen -->
    <div v-if="!cargando && movimientos.length > 0" style="margin-top:16px; display:flex; gap:12px;">
      <div class="kpi-card success" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Ingresos</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-success)">+{{ sumaIngreso }}</div>
        <div class="kpi-sub">unidades</div>
      </div>
      <div class="kpi-card danger" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Salidas</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-danger)">−{{ sumaSalida }}</div>
        <div class="kpi-sub">unidades</div>
      </div>
      <div class="kpi-card warning" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Ajustes</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-warning)">{{ cantAjuste }}</div>
      </div>
      <div class="kpi-card accent" style="flex:1; padding:12px 16px">
        <div class="kpi-label">Total (página)</div>
        <div style="font-size:20px; font-weight:800; color:var(--color-accent)">{{ movimientos.length }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { movimientos as movimientosApi } from '@/api/movimientos'

const movimientos = ref([])
const cargando = ref(true)
const total = ref(0)
const skip = ref(0)
const limit = ref(100)

const filtros = ref({
  buscar: '',
  tipo: '',
  desde: '',
  hasta: '',
})

const sumaIngreso = computed(() =>
  movimientos.value.filter(m => m.tipo === 'ingreso').reduce((s, m) => s + m.cantidad, 0)
)
const sumaSalida = computed(() =>
  movimientos.value.filter(m => m.tipo === 'salida').reduce((s, m) => s + m.cantidad, 0)
)
const cantAjuste = computed(() => movimientos.value.filter(m => m.tipo === 'ajuste').length)

function tipoBadge(tipo) {
  if (tipo === 'ingreso') return 'badge badge-green'
  if (tipo === 'salida') return 'badge badge-red'
  return 'badge badge-yellow'
}
function fmtFecha(f) {
  return new Date(f).toLocaleString('es-BO', {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

async function cargar() {
  cargando.value = true
  try {
    const params = { skip: skip.value, limit: limit.value }
    if (filtros.value.tipo) params.tipo = filtros.value.tipo
    if (filtros.value.buscar) params.buscar = filtros.value.buscar
    if (filtros.value.desde) params.fecha_desde = filtros.value.desde
    if (filtros.value.hasta) params.fecha_hasta = filtros.value.hasta
    const res = await movimientosApi.listar(params)
    movimientos.value = res.data.movimientos || []
    total.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function paginaAnterior() {
  skip.value = Math.max(0, skip.value - limit.value)
  cargar()
}
function paginaSiguiente() {
  skip.value += limit.value
  cargar()
}

function exportarCSV() {
  const headers = ['ID', 'Fecha', 'Producto', 'Código', 'Tipo', 'Motivo', 'Cantidad', 'Referencia']
  const rows = movimientos.value.map(m => [
    m.id, fmtFecha(m.fecha), `"${m.nombre_producto}"`, m.codigo_producto,
    m.tipo, m.motivo, m.cantidad, m.referencia_id || ''
  ])
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `movimientos_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(cargar)
</script>
